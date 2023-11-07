import json
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from .models import Catalyst
import psycopg2
from psycopg2 import InterfaceError, OperationalError, ProgrammingError
from psycopg2.extras import RealDictCursor
from allauth.account.forms import SignupForm
from .models import CMIUsers
from django.contrib.auth import authenticate, login
from django.contrib import messages
from background_task import background
import pandas as pd
#import numpy as np
# Create your views here.


DATABASE_CONFIG = {
    'dbname': 'dataset',
    'user': 'catalyst_admin',
    'password': 'beta',
    'host': 'localhost',
    'port': '5432',
}

@csrf_exempt
def home(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return render(request, 'upload.html')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'home.html')
    else:
        return render(request, 'home.html')

@csrf_exempt
def users(request):
    if request.method=="GET":
        #import pdb; pdb.set_trace()
        users = CMIUsers.objects.all().values_list('username','email')
        user_list = [list(item) for item in users]
        data = {
            'users': user_list
        }
        return render(request, 'users.html', data)
    return render(request, 'users.html')

@csrf_exempt
def adduser(request):
    if request.method == "GET":
        return render(request, 'adduser.html')

    if request.method == 'POST':
        #import pdb; pdb.set_trace()
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(request)
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            cmi_user = CMIUsers.objects.create(user=user, email=email, password=password, username = username) 
            cmi_user.save()
            return redirect('users')
        else:
            print(form.errors)
    else:
        form = SignupForm()
    return JsonResponse({"message":"User submitted"})


@background(schedule=0)
def process_file(file_path):
    for chunk in pd.read_csv(file_path, chunksize=700000):
        for index, row in chunk.iterrows():
            Catalyst.objects.create(
                name=row['name'],
                domain=row['domain'],
                year=row['year founded'],
                industry=row['industry'],
                size_range=row['size range'],
                city=row['locality'],
                country=row['country'],
                linkedin_url=row['linkedin url']
            )



@csrf_exempt
def upload(request):
    if not request.user.is_authenticated:
        return redirect('home')
    if request.method=="GET":
        return render(request, 'upload.html')

    if request.method == "POST" and request.FILES['file']:
        file = request.FILES['file']

        # Assuming you have saved the file locally, use its path
        file_path = '/home/akshitasuthar/post/free-7-million-company-dataset/companies_sorted2.csv'

        process_file(file_path)
        return JsonResponse({'message': 'File upload successfully.'})

    return JsonResponse({'message': 'File upload failed.'})


@csrf_exempt
def query_builder(request):
    if request.method == "GET":
        
        city = Catalyst.objects.all().values_list('city', flat=True).distinct().order_by('city')
        industry = Catalyst.objects.all().values_list('industry', flat=True).distinct().order_by('industry')
        country = Catalyst.objects.all().values_list('country', flat=True).distinct().order_by('country')
        year = Catalyst.objects.all().values_list('year', flat=True).distinct().order_by('-year')
        domain = Catalyst.objects.all().values_list('domain', flat=True).distinct().order_by('domain')

        context = {
            'city': city,
            'industry': industry,
            'country': country,
            'year' : year,
            'domain' : domain
        }
        return render(request, 'query_builder.html', context)

    if request.method == "POST":
        try:
            #import pdb; pdb.set_trace()
            country_data = request.POST.get('country')
            city_data = request.POST.get('city')
            industry_data = request.POST.get('industry')
            domain_data = request.POST.get('domain')

            query_set = Catalyst.objects.filter(
            country__iexact=country_data,
            industry__iexact=industry_data, city__iexact=city_data, domain=domain_data).distinct()

            count = query_set.count()

            return JsonResponse({'message': 'Success', 'count': count})
        except Exception as e:
            return JsonResponse({'message': f'An error occurred: {e}'}, status=500)

    return HttpResponse("Invalid request method.")


        




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
        users = list(CMIUsers.objects.all().values_list('email',flat=True))
    data = {
        'data': users
    }

    return JsonResponse(data)
    #return render(request, 'users.html')

@csrf_exempt
def adduser(request):
    if request.method == "GET":
        return render(request, 'adduser.html')

    if request.method == 'POST':
        #import pdb; pdb.set_trace()
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(request)
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            cmi_user = CMIUsers.objects.create(user=user, email=email, password=password) 
            cmi_user.save()
            return redirect('users')
        else:
            print(form.errors)
    else:
        form = SignupForm()
    return JsonResponse({"message":"User submitted"})


@csrf_exempt
def upload(request):
    if not request.user.is_authenticated:
        return redirect('home')
    if request.method=="GET":
        return render(request, 'upload.html')

    if request.method=="POST" and request.FILES['file']:
        print("jdskhfjsh")
        #file = request.FILES['file']
        file= '/home/akshitasuthar/post/free-7-million-company-dataset/cmp.csv'

        # Iterate through file chunks and save them
        for chunk in pd.read_csv(file, chunksize=100):
            for index, row in chunk.iterrows():
                created = Catalyst.objects.update_or_create(
                    name=row['name'],
                    domain=row['domain'],
                    year=row['year founded'],
                    industry=row['industry'],
                    size_range=row['size range'],
                    city=row['locality'],
                    country=row['country'],
                    linkedin_url=row['linkedin url']
                )
                if not created:
                    return JsonResponse({'message': 'File already exists. Skipped uploading.'})

        if created:
            message = 'File upload successful.'
        else:
            message = 'File already exists. Skipped uploading.'


        return JsonResponse({'message': message})

    return JsonResponse({'message': 'File upload failed.'})


@csrf_exempt
def query_builder(request):
    if request.method=="GET":
        """city = Catalyst.objects.all().values_list('city',flat=True).distinct()
        state = Catalyst.objects.all().values_list('state',flat=True).distinct()
        industry = Catalyst.objects.all().values_list('industry',flat=True).distinct()
        year_founded = Catalyst.objects.all().values_list('year',flat=True).distinct()"""
        country = Catalyst.objects.all().values_list('country',flat=True).distinct()

        context = {
            #'city': city,
            #'industry': industry,
            #'year_founded': year_founded,
            'country': country
        }
        return render(request, 'query_builder.html', context)

    if request.method=="POST":
        try:
            data = request.POST.get('country')
            print("hey")
            queryset = Catalyst.objects.filter(country=data).distinct().count()

            return JsonResponse({'message': "Success","count":queryset})
            return JsonResponse(results, safe=False)
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}")

    return HttpResponse("Invalid request method.")
        


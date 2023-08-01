# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.core.paginator import Paginator
from .forms import DonationForm, GroupForm, DonorForm, StudentForm, SponsorshipTypeForm
from django.urls import reverse
from .models import Donation, Beneficiary, Group, Donor, SponsorshipType
from django.shortcuts import get_object_or_404, render, redirect
from datetime import datetime
import csv, io
from decimal import *
from itertools import chain

@login_required
def get_sponsor_email(request, id=None):

    instance = get_object_or_404(Donor, id=id)
    context={
        'instance': instance
    }
    return render(request, 'home/email-modal.html', context)

@login_required(login_url="/login/")
def index(request):

    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.save()
            return HttpResponseRedirect('payments.html')
    else:
        form = DonationForm()
        context = {'donationForm':form}

    context['segment'] = 'index'

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

def Sponsor_Add(request):

    if request.method == 'POST':
        form = DonorForm(request.POST)
        if form.is_valid():
            donor = form.save(commit=False)
            donor.save()
        else:
            form = DonorForm()
        return HttpResponseRedirect('../sponsors.html')


def Donation_Add(request):

    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.save()
        else:
            form = DonationForm()
        return HttpResponseRedirect('../payments.html')
    
def Donations(request):
    print("HERE!")
    return HttpResponseRedirect('donations.html')


# needs to be refactored to use dedicated functions for each view
@login_required(login_url="/login/")
def pages(request):
    pays = Donation.objects.all()
    students = Beneficiary.objects.all()
    donors = Donor.objects.all()
    paymentForm = DonationForm()


    projects = SponsorshipType.objects.all()
    churches = Group.objects.all()
    context = {'students':students,
               'payments':pays,
               'donors':donors,
               'projects':projects,
               'churches':churches,
               'payForm': paymentForm
               }


    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))

        if load_template == 'search.html':
            if request.method == 'POST':
                searchText = request.POST['search-text']

                resultsDonors = Donor.objects.filter(name__contains=searchText)
                resultsStudents = Beneficiary.objects.filter(name__contains=searchText)
                resultsPaymentsDonor = Donation.objects.filter(donor__name__contains=searchText)
                resultsPaymentsStudent = Donation.objects.filter(student__name__contains=searchText)
                resultsPrograms = SponsorshipType.objects.filter(name__contains=searchText)
                resultsGroups = Group.objects.filter(name__contains=searchText)
                results = chain(resultsDonors, resultsStudents, resultsPrograms, resultsGroups, resultsPaymentsDonor, resultsPaymentsStudent)

                context['results'] = results
                context['searchTerm'] = searchText

            else:
                searchText = request.POST['search-text']
                context['searchTerm'] = searchText



        if load_template == 'overfunded.html':
            overfunded_students = []
            for student in students:

                # How much should they have?
                program_cost = SponsorshipType.objects.get(name=student.program).cost
                funded_thru = datetime.now().date()
                months_to_be_funded = diff_month(funded_thru, student.enroll_date)
                expected_amount = program_cost * months_to_be_funded

                #need donor under/overfunded?
                #why is the student over/underfunded?


                # How much do they actually have?
                total = Decimal()
                this_students_donations = Donation.objects.filter(student=student)

                for p in this_students_donations:
                    total += p.amount

                if total > expected_amount:
                    overfunded_students.append(student)
                    student.overfunded_amount = total-expected_amount

            context['overfunded'] = overfunded_students


        if load_template == 'underfunded.html':
            underfunded_students = []
            for student in students:

                # How much should they have?
                program_cost = SponsorshipType.objects.get(name=student.program).cost
                funded_thru = datetime.now().date()
                months_to_be_funded = diff_month(funded_thru, student.enroll_date)
                expected_amount = program_cost * months_to_be_funded


                # How much do they actually have?
                total = Decimal()
                this_students_donations = Donation.objects.filter(student=student)

                for p in this_students_donations:
                    total += p.amount

                if total < expected_amount:
                    underfunded_students.append(student)
                    student.deficit_amount = total-expected_amount

            context['underfunded'] = underfunded_students


        # hacked, needs to be refactored, extract to individual methods
        if load_template == 'payments.html':
            if request.method == 'POST':
                form = DonationForm(request.POST)
                if form.is_valid():
                    donation = Donation(commit=False)
                    donation.save()
                    return HttpResponseRedirect('payments.html')
            else:
                form = DonationForm()
                context['form'] = form


        if load_template == 'students.html':
            form = StudentForm(request.POST)
            if form.is_valid():
                student = form.save(commit=False)
                #testEnroll = '2021/10/20'
                #student.enroll_date = datetime.strptime(testEnroll, "%Y/%m/%d")
                student.enroll_date = datetime.now()
                student.save()
                newSponsor = form.cleaned_data['sponsor'].first()
                student.sponsor.add(newSponsor)
                form.save_m2m()

                return HttpResponseRedirect('students.html')
            else:
                form = StudentForm()
                context['form'] = form



        if load_template == 'sponsors.html':
            form = DonorForm(request.POST)
            if form.is_valid():
                donor = form.save(commit=False)
                donor.save()

                return HttpResponseRedirect('sponsors.html')
            else:
                form = DonorForm()
                context['form'] = form

        if load_template == 'programs.html':
            form = SponsorshipTypeForm(request.POST)
            if form.is_valid():
                program = SponsorshipType(commit=False)
                program.save()

                return HttpResponseRedirect('programs.html')
            else:
                form = SponsorshipTypeForm()
                context['form'] = form

        if load_template == 'groups.html':
            form = GroupForm(request.POST)
            if form.is_valid():
                church = form.save(commit=False)
                church.save()

                return HttpResponseRedirect('groups.html')
            else:
                form = GroupForm()
                context['form'] = form


        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

"""     except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request)) """

@login_required(login_url="/login/")
def Payment_Detail(request, id):
    payment = Donation.objects.get(id=id)
    template = loader.get_template('home/payment.html')

    if request.method == 'POST':
        form = DonationForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('../payments.html')
    else:
        payform = DonationForm(instance=payment)

    context = {
        'payment':payment,
        'form':payform,
    }
    return HttpResponse(template.render(context, request))

@login_required(login_url="/login/")
def Group_Detail(request, id):
    group = Group.objects.get(id=id)
    template = loader.get_template('home/group.html')

    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('../groups.html')
    else:
        initial_data = {
            'name':group.name,
            'address':group.address.raw,
            'email':group.email,
            'phone':group.phone
        }
        form = GroupForm(instance=group, initial=initial_data)

    context = {
        'group':group,
        'form':form,
    }
    return HttpResponse(template.render(context, request))

@login_required(login_url="/login/")
def Sponsor_Detail(request, id):
    sponsor = Donor.objects.get(id=id)
    template = loader.get_template('home/sponsor.html')


    # TODO: fix address updating... currently, it just creates an entirely new record in address table
    if request.method == 'POST':
        form = DonorForm(request.POST, instance=sponsor)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('../sponsors.html')
    else:
        initial_data = {
            'name':sponsor.name,
            'address':sponsor.address.raw,
            'email':sponsor.email,
            'phone':sponsor.phone,
            'church':sponsor.church
        }
        sponsorform = DonorForm(instance=sponsor, initial=initial_data)

    context = {
        'sponsor':sponsor,
        'form': sponsorform,
    }
    return HttpResponse(template.render(context, request))

@login_required(login_url="/login/")
def Student_Detail(request, id):
    student = Beneficiary.objects.get(id=id)
    template = loader.get_template('home/student.html')

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('../students.html')
    else:
        form = StudentForm(instance=student)

    context = {
        'student':student,
        'form': form,
    }
    return HttpResponse(template.render(context, request))

@login_required(login_url="/login/")
def Program_Detail(request, id):
    program = SponsorshipType.objects.get(id=id)
    template = loader.get_template('home/program.html')

    if request.method == 'POST':
        form = SponsorshipTypeForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('../programs.html')
    else:
        form = SponsorshipTypeForm(instance=program)

    context = {
        'program':program,
        'form':form,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url="/login/")
def Delete_Data(request):

    Donation.objects.all().delete()
    SponsorshipType.objects.all().delete()
    Donor.objects.all().delete()
    Beneficiary.objects.all().delete()
    Group.objects.all().delete()


    return HttpResponseRedirect('../')

#test upload
@login_required(login_url="/login/")
def Upload(request):
    if request.method=='POST':
        upload = request.FILES['doc']
        file = upload.read().decode('utf-8')

        reader = csv.DictReader(io.StringIO(file))

        data = [line for line in reader]

        for d in data:
            print(d)

        print(data)

        return HttpResponseRedirect('../')

@login_required(login_url="/login/")
def Upload_Sponsors(request):
    if request.method=='POST':
        upload = request.FILES['doc']
        file = upload.read().decode('utf-8')

        reader = csv.DictReader(io.StringIO(file))

        data = [line for line in reader]

        for d in data:
            created = Donor(
                name = d['sponsor_Name'],
                email = d['sponsor_email'],
                phone = d['phone'],
                address = d['address']
                )
            created.save()

        return HttpResponseRedirect('../sponsors.html')

@login_required(login_url="/login/")
def Upload_Students(request):
    if request.method=='POST':
        upload = request.FILES['doc']
        file = upload.read().decode('utf-8')

        reader = csv.DictReader(io.StringIO(file))

        data = [line for line in reader]

        for d in data:
            created = Beneficiary(
                name = d['name'],
                program = SponsorshipType.objects.get(name=d['program']),
                community = d['community'],
                grade = d['grade'],
                enroll_date = datetime.now()
                )
            created.save()

        print(data)

        return HttpResponseRedirect('../students.html')


def Sponsor_Delete(request, id):
    sponsor = Donor.objects.get(pk=id)
    sponsor.delete()
    return HttpResponseRedirect("../../sponsors.html")

def Student_Delete(request, id):
    student = Beneficiary.objects.get(pk=id)
    student.delete()
    return HttpResponseRedirect("../../students.html")

def Group_Delete(request, id):
    group = Group.objects.get(pk=id)
    group.delete()
    return HttpResponseRedirect("../../groups.html")

def Program_Delete(request, id):
    prog = SponsorshipType.objects.get(pk=id)
    prog.delete()
    return HttpResponseRedirect("../../programs.html")

def Payment_Delete(request, id):
    payment = Donation.objects.get(pk=id)
    payment.delete()
    return HttpResponseRedirect("../../payments.html")

#from top solution here: https://stackoverflow.com/questions/4039879/best-way-to-find-the-months-between-two-dates
def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

def display_latestnews(request):

    newsdata = Donor.objects.all()
    # articles per page
    per_page = 4
    # Paginator in a view function to paginate a queryset
    # show 4 news per page
    obj_paginator = Paginator(newsdata, per_page)
    # list of objects on first page
    first_page = obj_paginator.page(1).object_list
    # range iterator of page numbers
    page_range = obj_paginator.page_range

    context = {
    'obj_paginator':obj_paginator,
    'first_page':first_page,
    'page_range':page_range
    }
    #
    if request.method == 'POST':
        #getting page number
        page_no = request.POST.get('page_no', None)
        results = list(obj_paginator.page(page_no).object_list.values('id', 'title','content'))
        return JsonResponse({"results":results})

    return render(request, 'home/test.html',context)

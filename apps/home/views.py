# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.core.paginator import Paginator
from .forms import DonationForm, GroupForm, DonorForm, StudentForm, SponsorshipTypeForm, SponsorshipForm, CommunityForm 
from django.urls import reverse, reverse_lazy
from .models import Donation, Beneficiary, Group, Donor, SponsorshipType, Sponsorship, Community
from django.shortcuts import get_object_or_404, render, redirect
from funky_sheets.formsets import HotView
from django.forms import CheckboxSelectMultiple, CheckboxInput, DateInput
from datetime import datetime
import csv, io
from decimal import *
from itertools import chain


@login_required
def Sponsorships(request):
    load_template = request.path.split('/')[-1]
    sponsorships = Sponsorship.objects.all()
    sponsorshipForm = SponsorshipForm()


    context = {'sponsorships':sponsorships,
               'sponsorshipForm': sponsorshipForm}
    

    form = SponsorshipForm()
    context['form'] = form

    context['segment'] = load_template

    html_template = loader.get_template('home/' + load_template)
    return HttpResponse(html_template.render(context, request))


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
            return HttpResponseRedirect('donations.html')
    else:
        form = DonationForm()
        context = {'donationForm':form}

    context['segment'] = 'index'

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

@login_required
def Sponsorship_Add(request):

    if request.method == 'POST':
        form = SponsorshipForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            form = SponsorshipForm()
        return HttpResponseRedirect('../sponsorships.html')

@login_required
def Sponsor_Add(request):

    if request.method == 'POST':
        form = DonorForm(request.POST)
        if form.is_valid():
            donor = form.save(commit=False)
            donor.save()
        else:
            form = DonorForm()
        return HttpResponseRedirect('../sponsors.html')

@login_required
def Donation_Add(request):

    if request.method == 'POST':
        
        form = DonationForm(request.POST)
        
        
        if form.is_valid():
            donation = form.save(commit=False)            
            donation.save()
        
            



    else:
        print(form.errors.values)
        form = DonationForm()
            
    return HttpResponseRedirect('../donations.html')
    
@login_required
def Donations(request):
    load_template = request.path.split('/')[-1]
    donations = Donation.objects.all()
    students = Beneficiary.objects.all()
    donors = Donor.objects.all()
    projects = SponsorshipType.objects.all()
    churches = Group.objects.all()
    
    
    donationForm = DonationForm()

    context = {'students':students,
               'donations':donations,
               'donors':donors,
               'projects':projects,
               'churches':churches,
               'donationForm': donationForm
               }
    
    if request.method == 'POST':
        form = DonationForm(request.POST)
    
        if form.is_valid():
            donation = Donation(commit=False)
            donation.save()
            return HttpResponseRedirect('donations.html')
        else:
            print(form.errors)
    else:
        form = DonationForm()
        context['form'] = form

    context['segment'] = load_template

    html_template = loader.get_template('home/' + load_template)
    return HttpResponse(html_template.render(context, request))

def Donors(request):
    pass


# needs to be refactored to use dedicated functions for each view
@login_required(login_url="/login/")
def pages(request):
    pays = Donation.objects.all()
    students = Beneficiary.objects.all()
    donors = Donor.objects.all()
    paymentForm = DonationForm()
    communities = Community.objects.all()


    projects = SponsorshipType.objects.all()
    churches = Group.objects.all()
    context = {'students':students,
               'communities':communities,
               'donations':pays,
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
                resultsCommunity = Community.objects.filter(name__contains=searchText)
                resultsPaymentsDonor = Donation.objects.filter(donor__name__contains=searchText)
                resultsPaymentsStudent = Donation.objects.filter(beneficiary__name__contains=searchText)
                resultsPrograms = SponsorshipType.objects.filter(name__contains=searchText)
                resultsGroups = Group.objects.filter(name__contains=searchText)
                results = chain(resultsDonors, resultsStudents, resultsPrograms, resultsGroups, resultsPaymentsDonor, resultsPaymentsStudent, resultsCommunity)

                context['results'] = results
                context['searchTerm'] = searchText

            else:
                searchText = request.POST['search-text']
                context['searchTerm'] = searchText



        if load_template == 'overfunded.html':
            sponsorships = Sponsorship.objects.all()
            overfunded_students = []
            for sponsorship in sponsorships:

                # How much should they have?
                funded_thru = datetime.now().date()
                months_to_be_funded = diff_month(funded_thru, sponsorship.beneficiary.enroll_date)
                expected_amount = sponsorship.type.cost * months_to_be_funded


                #need donor under/overfunded?
                #why is the student over/underfunded?


                # How much do they actually have?
                total = Decimal()
                this_students_donations = Donation.objects.filter(beneficiary=sponsorship.beneficiary)

                for p in this_students_donations:
                    total += p.amount

                if total > expected_amount:
                    overfunded_students.append(sponsorship)
                    sponsorship.overfunded_amount = total-expected_amount

            context['overfunded'] = overfunded_students


        if load_template == 'underfunded.html':
            sponsorships = Sponsorship.objects.all()
            underfunded_students = []
            for sponsorship in sponsorships:

                # How much should they have?
                funded_thru = datetime.now().date()
                months_to_be_funded = diff_month(funded_thru, sponsorship.beneficiary.enroll_date)
                expected_amount = sponsorship.type.cost * months_to_be_funded


                # How much do they actually have?
                total = Decimal()
                this_students_donations = Donation.objects.filter(beneficiary=sponsorship.beneficiary)

                for p in this_students_donations:
                    total += p.amount

                if total < expected_amount:
                    underfunded_students.append(sponsorship)
                    sponsorship.deficit_amount = total-expected_amount

            context['underfunded'] = underfunded_students




        if load_template == 'students.html':
            form = StudentForm(request.POST)
            if form.is_valid():
                student = form.save(commit=False)
                student.save()
                #donor = form.cleaned_data['donor'].first()
                #student.sponsor.add(newSponsor)
                form.save_m2m()

                return HttpResponseRedirect('students.html')
            else:
                form = StudentForm()
                context['form'] = form
                sponsorships = Sponsorship.objects.all()
                context['sponsorships'] = sponsorships
        
        if load_template == 'communities.html':
            form = CommunityForm(request.POST)
            if form.is_valid():
                community = form.save(commit=False)
                community.save()

                return HttpResponseRedirect('communities.html')
            else:
                form = CommunityForm()
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
                program = form.save(commit=False)
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
def Donation_Detail(request, id):
    donation = Donation.objects.get(id=id)
    template = loader.get_template('home/donation.html')

    if request.method == 'POST':
        form = DonationForm(request.POST, instance=donation)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('../donations.html')
    else:
        payform = DonationForm(instance=donation)

    context = {
        'donation':donation,
        'form':payform,
    }
    return HttpResponse(template.render(context, request))

@login_required(login_url="/login/")
def Group_Detail(request, id):
    group = Group.objects.get(id=id)
    template = loader.get_template('home/group.html')
    donations = Donation.objects.filter(group=group)

    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('../groups.html')
    else:
        initial_data = {
            'name':group.name,
            'address':group.address,
            'email':group.email,
            'phone':group.phone
        }
        form = GroupForm(instance=group, initial=initial_data)

    context = {
        'group':group,
        'donations':donations,
        'form':form,
    }
    return HttpResponse(template.render(context, request))

@login_required(login_url="/login/")
def Sponsor_Detail(request, id):
    donor = Donor.objects.get(id=id)
    hasActiveSponsorships = False
    template = loader.get_template('home/sponsor.html')
    sponsorships = Sponsorship.objects.filter(sponsor=donor)
    donations = Donation.objects.filter(donor=donor)

    for s in sponsorships:
        if s.isActive:
            hasActiveSponsorships = True

    # TODO: fix address updating... currently, it just creates an entirely new record in address table
    if request.method == 'POST':

        form = DonorForm(request.POST, instance=donor)
        
        if form.is_valid():
                    
            form.save()
            return HttpResponseRedirect('../sponsors.html')
    else:
        initial_data = {
            'name':donor.name,
            'address':donor.address,
            'email':donor.email,
            'phone':donor.phone,
            'group':donor.group
        }
        donorform = DonorForm(instance=donor, initial=initial_data)

    context = {
        'sponsorshipStatus':hasActiveSponsorships,
        'sponsor':donor,
        'donations':donations,
        'sponsorships': sponsorships,
        'form': donorform,
    }

    
    
    return HttpResponse(template.render(context, request))

@login_required(login_url="/login/")
def Sponsorship_Detail(request, id):
    sponsorship = Sponsorship.objects.get(id=id)
    template = loader.get_template('home/sponsorship.html')


    # TODO: fix address updating... currently, it just creates an entirely new record in address table
    if request.method == 'POST':
        form = SponsorshipForm(request.POST, instance=sponsorship)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('../sponsorships.html')
    else:
        initial_data = {
            'type':sponsorship.type,
            'isActive': sponsorship.isActive,
            'begin_date':sponsorship.begin_date,
            'end_date':sponsorship.end_date,
            'payment_interval':sponsorship.payment_interval,
            'additional_cost':sponsorship.additional_cost,
            'sponsor':sponsorship.sponsor,
            'beneficiary': sponsorship.beneficiary
        }
        sponsorshipForm = SponsorshipForm(instance=sponsorship, initial=initial_data)

    context = {
        'sponsor':sponsorship,
        'form': sponsorshipForm,
    }
    return HttpResponse(template.render(context, request))

@login_required(login_url="/login/")
def Student_Detail(request, id):
    student = Beneficiary.objects.get(id=id)
    hasActiveSponsorships = False
    sponsorships = Sponsorship.objects.filter(beneficiary=student)
    template = loader.get_template('home/student.html')

    for s in sponsorships:
        if s.isActive:
            hasActiveSponsorships = True

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('../students.html')
    else:
        form = StudentForm(instance=student)

    context = {
        'sponsorshipStatus': hasActiveSponsorships,
        'sponsorships':sponsorships,
        'student':student,
        'form': form,
    }
    return HttpResponse(template.render(context, request))
@login_required(login_url="/login/")
def Community_Detail(request, id):
    community = Community.objects.get(id=id)
    template = loader.get_template('home/community.html')
    
    if request.method == 'POST':
        form = CommunityForm(request.POST, instance=community)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('../communities.html')
    else:
        form = CommunityForm(instance=community)

    context = {
        'community':community,
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

def Sponsorship_Delete(request, id):
    sponsorship = Sponsorship.objects.get(pk=id)
    sponsorship.delete()
    return HttpResponseRedirect("../../sponsorships.html")

def Sponsor_Delete(request, id):
    #figure out what to do with this sponsor's associated records (donations, beneficiaries, groups, etc)
    sponsor = Donor.objects.get(pk=id)
    sponsor.delete()
    return HttpResponseRedirect("../../sponsors.html")

def Student_Delete(request, id):
    student = Beneficiary.objects.get(pk=id)
    student.delete()
    return HttpResponseRedirect("../../students.html")

def Community_Delete(request, id):
    community = Community.objects.get(pk=id)
    community.delete()
    return HttpResponseRedirect("../../communities.html")

def Group_Delete(request, id):
    group = Group.objects.get(pk=id)
    group.delete()
    return HttpResponseRedirect("../../groups.html")

def Program_Delete(request, id):
    prog = SponsorshipType.objects.get(pk=id)
    prog.delete()
    return HttpResponseRedirect("../../programs.html")

def Donation_Delete(request, id):
    donation = Donation.objects.get(pk=id)
    donation.delete()
    return HttpResponseRedirect("../../donations.html")

class FunkyCreate(HotView):
    # Define model to be used by the view
    model = Donor
    # Define template
    template_name = 'home/create.html'
    # Define custom characters/strings for checked/unchecked checkboxes
    checkbox_checked = 'yes' # default: true
    checkbox_unchecked = 'no' # default: false
    # Define prefix for the formset which is constructed from Handsontable spreadsheet on submission
    prefix = 'table'
    # Define success URL
    success_url = reverse_lazy('update')
    # Define fields to be included as columns into the Handsontable spreadsheet
    fields = (
        'name',
        'group',
        'email',
        'address',
        'phone',
        'date_of_birth',
    )
    # Define extra formset factory kwargs
    factory_kwargs = {
        'widgets': {
            'date_of_birth': DateInput(attrs={'type': 'date'}),
        }
    }
    # Define Handsontable settings as defined in Handsontable docs
    hot_settings = {
        'contextMenu': 'true',
        'autoWrapRow': 'true',
        'rowHeaders': 'true',
        'contextMenu': 'true',
        'search': 'true',
        # When value is dictionary don't wrap it in quotes
        'headerTooltips': {
            'rows': 'false',
            'columns': 'true'
        },
        # When value is list don't wrap it in quotes
        'dropdownMenu': [
            'remove_col',
            '---------',
            'make_read_only',
            '---------',
            'alignment'
        ],
        'licenseKey': 'non-commercial-and-evaluation',
    }


class FunkyUpdate(FunkyCreate):
  template_name = 'home/datatable.html'
  # Define 'update' action
  action = 'update'
  # Define 'update' button
  button_text = 'Update'
  hot_settings = {
      'licenseKey': 'non-commercial-and-evaluation',
  }
 

#from top solution here: https://stackoverflow.com/questions/4039879/best-way-to-find-the-months-between-two-dates
def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

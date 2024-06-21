# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.forms import ModelForm, TextInput, DateInput, NumberInput, Select, Textarea, EmailInput
from .models import Donation, Group, Donor, Beneficiary, SponsorshipType, Sponsorship, PAYMENT_CHOICES, PAYMENT_INTERVALS


class DonorForm(ModelForm):
    class Meta:
        model = Donor
        fields = "__all__"

    name            = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Name', 'class':'form-control'}))
    group           = forms.ModelChoiceField(required=False, queryset=Group.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    email           = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'placeholder':'Email', 'class':'form-control', 'type':'email'}))
    address         = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Address', 'class':'form-control .'}))
    phone           = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone', 'class':'form-control'}))
    date_of_birth   = forms.DateField(required=False, widget=forms.DateInput(attrs={'placeholder': 'Date of Birth', 'class':'form-control', 'type':'date'}))


    

class StudentForm(ModelForm):
    class Meta:
        model = Beneficiary
        fields = "__all__"

        
    name            = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Name', 'class':'form-control'}))
    email           = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'placeholder':'Email', 'class':'form-control', 'type':'email'}))
    address         = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Address', 'class':'form-control .'}))
    phone           = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone', 'class':'form-control'}))
    date_of_birth   = forms.DateField(required=False, widget=forms.DateInput(attrs={'placeholder': 'Date of Birth', 'class':'form-control', 'type':'date'}))
    enroll_date     = forms.DateField(required=False, widget=forms.DateInput(attrs={'placeholder': 'Date of Birth', 'class':'form-control', 'type':'date'}))


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = "__all__"

    name    = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Name', 'class':'form-control'}))
    email   = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'placeholder':'Email', 'class':'form-control', 'type':'email'}))
    address = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Address', 'class':'form-control .'}))
    phone   = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Phone', 'class':'form-control'}))

class DonationForm(ModelForm):
    class Meta:
        model = Donation
        fields = "__all__"

    
    amount          = forms.DecimalField(widget=forms.NumberInput(attrs={'placeholder': 'Amount', 'class':'form-control'}))
    method          = forms.ChoiceField(choices=PAYMENT_CHOICES, widget=forms.Select(attrs={'placeholder':'Payment Method', 'class':'form-control'}))
    date            = forms.DateField(widget=forms.DateInput(attrs={'placeholder': 'Date of Donation', 'class':'form-control', 'type':'date'}))
    donor           = forms.ModelChoiceField(queryset=Donor.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    group           = forms.ModelChoiceField(required=False, queryset=Group.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    beneficiary     = forms.ModelChoiceField(required=False, queryset=Beneficiary.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))


class SponsorshipTypeForm(ModelForm):
    class Meta:
        model = SponsorshipType
        fields = "__all__"

    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Program Name', 'class':'form-control'}))
    cost = forms.DecimalField(widget=forms.NumberInput(attrs={'placeholder':'Base program cost', 'class':'form-control'}))

class SponsorshipForm(ModelForm):
    class Meta:
        model = Sponsorship
        fields = "__all__"

    isActive         = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':'form-check-label'}))
    isActive.label   = "Active?"
    type             = forms.ModelChoiceField(queryset=SponsorshipType.objects.all(), widget=forms.Select(attrs={'placeholder':'Program','class': 'form-control'}))
    type.label       = "Program"
    begin_date       = forms.DateField(widget=forms.DateInput(attrs={'placeholder':'Start date of sponsorship', 'class':'form-control', 'type':'date'}))
    end_date         = forms.DateField(widget=forms.DateInput(attrs={'placeholder':'Start date of sponsorship', 'class':'form-control', 'type':'date'}))
    payment_interval = forms.ChoiceField(choices=PAYMENT_INTERVALS, widget=forms.Select(attrs={'placeholder':'Payment Method', 'class':'form-control'}))
    additional_cost  = forms.DecimalField(widget=forms.NumberInput(attrs={'placeholder':'Is there any extra cost?', 'class':'form-control'}))
    sponsor          = forms.ModelChoiceField(queryset=Donor.objects.all(),widget=forms.Select(attrs={'class': 'form-control'}))
    beneficiary      = forms.ModelChoiceField(queryset=Beneficiary.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))

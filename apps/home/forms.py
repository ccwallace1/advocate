# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.forms import ModelForm, TextInput, DateInput, NumberInput, Select, Textarea, EmailInput
from .models import Donation, Group, Donor, Beneficiary, SponsorshipType, Sponsorship


class DonorForm(ModelForm):
    class Meta:
        model = Donor
        fields = "__all__"

    name            = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Name', 'class':'form-control'}))
    group = forms.ModelChoiceField(queryset=Group.objects.all(), widget=forms.Select(attrs={'class': 'custom-select'}))
    email           = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'Email', 'class':'form-control', 'type':'email'}))
    address         = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address', 'class':'form-control .'}))
    phone           = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Phone', 'class':'form-control'}))
    date_of_birth   = forms.DateField(widget=forms.DateInput(attrs={'placeholder': 'Date of Birth', 'class':'form-control', 'type':'date'}))


    

class StudentForm(ModelForm):
    class Meta:
        model = Beneficiary
        fields = "__all__"

class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = "__all__"

class DonationForm(ModelForm):
    class Meta:
        model = Donation
        fields = "__all__"


class SponsorshipTypeForm(ModelForm):
    class Meta:
        model = SponsorshipType
        fields = "__all__"

class SponsorshipForm(ModelForm):
    class Meta:
        model = Sponsorship
        fields = "__all__"
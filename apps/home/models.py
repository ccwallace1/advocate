# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django import template

# Create your models here.
# Program choices
PAYMENT_INTERVALS = (
    (1, "Monthly"),
    (3, "Quarterly"),
    (6, "Biannual"),
    (12, "Yearly"),
)

# Program choices
PAYMENT_CHOICES = (
    ("Check", "Check"),
    ("Online", "Online"),
)


class Person(models.Model):
    name = models.CharField(max_length=70)
    email = models.EmailField(max_length=254, blank=True, null=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=25, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
    
class Project(models.Model):
    pass
    
class Group(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=254, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=25, blank=True)

    #implement a get members function here?
    
    def __str__(self):
        return self.name
    
        
class SponsorshipType(models.Model):
    name = models.CharField(max_length=35)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
        
    def __str__(self):
        return self.name
    
class Community(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Beneficiary(Person):
    enroll_date = models.DateField(null=True)
    community = models.ForeignKey(Community, on_delete=models.SET_NULL, blank=True, null=True)
    #sponsorships = models.ManyToManyField(Sponsorship, blank=True)
    #donations = GenericRelation(Donation, related_query_name='donations')

    def __str__(self):
        return self.name
    

    @property
    def isSponsored(self):
        for i in self.sponsorship_set.all():
            if i.isActive:
                return True
        return False
    
    @property
    def sponsorshipProgram(self):
        for i in self.sponsorship_set.all():
            if i.isActive:
                return i.type
            else:
                return ""
    
class Donor(Person):
    #sponsorships = models.ForeignKey(Sponsorship, on_delete=models.SET_NULL, blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True)
    #donations = GenericRelation(Donation, related_query_name='donations')
    

    def __str__(self):
        return self.name
    
    @property
    def isSponsor(self):
        for i in self.sponsorship_set.all():
            if i.isActive:
                return True
        return False
    
    
class Sponsorship(models.Model):
    isActive = models.BooleanField()
    type = models.ForeignKey(SponsorshipType, on_delete=models.SET_NULL, null=True)
    begin_date = models.DateField(blank=True)
    end_date = models.DateField(blank=True, null=True)
    payment_interval = models.IntegerField(choices=PAYMENT_INTERVALS, default='Monthly')
    additional_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    sponsor = models.ForeignKey(Donor, on_delete=models.CASCADE, null=True)
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE)
    
    
class Donation(models.Model):
    date = models.CharField(default="", max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='Check')

    # The donor of a donation object could be the individual or group giving money
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)

    # The receiver of a donation object could be a Beneficiary or a generic program (like a water project)
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name







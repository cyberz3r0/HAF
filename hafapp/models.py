from django.db import models
from django.db.models.base import Model
from django.db.models.fields.related import ForeignKey
import re
# Create your models here.

class UserManager(models.Manager):
    def validator(self, postData):
        EMAIL_REGEX = re.compile('^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        errors = {}
        if len(postData['fname']) < 2:
            errors['fname'] = "First name should be at least 2 characters."
        if len(postData['lname']) < 2:
            errors['lname'] = "Last name should be at least 2 characters."
        if not EMAIL_REGEX.match(postData['email']):           
            errors['email'] = "Invalid email address format!"
        elif User.objects.filter(email = postData['email']):
            errors['email'] = "This email address is already taken."
        if  0 <= len(postData['password']) <= 4:
            errors['password'] = "Password needs to be at least 5 characters."
        elif postData['cpassword'] != postData['password']:
            errors['password'] = "Passwords do not match!"
        return errors
        
class User(models.Model):
    first_name= models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    password=models.CharField(max_length=100)
    email=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

class Friend(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, related_name="friends" , on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Order(models.Model):
    name = models.CharField(max_length=50)
    sales_tax = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    tip = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    grand_total = models.DecimalField(max_digits=6, decimal_places=2, null=True) 
    creator = models.ForeignKey(User, related_name="owner" , on_delete = models.CASCADE)
    friends = models.ManyToManyField(Friend, related_name="orders")
    total_cost = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Item(models.Model):
    name= models.CharField(max_length=50)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    order = models.ForeignKey(Order, related_name="items" , on_delete = models.CASCADE)
    ordered_by_friend = models.ForeignKey(Friend, related_name="items" , on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
from django import forms
from django.forms import fields
from .models import CustomUser, Payment, Withdrawal
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomForm(forms.ModelForm):
    class Meta:
        model=CustomUser
        fields = '__all__'

class CustomForms(forms.ModelForm):
    class Meta:
        model=CustomUser
        exclude = ('country',)

class UserForm(forms.ModelForm):
    class Meta:
        model=User
        fields = ('username','first_name','last_name','email')

class RegisterationForm(UserCreationForm):
    class Meta:
        model=User
        fields = ('username','first_name','last_name','email','password1','password2')

class DepositForm(forms.ModelForm):
    class Meta:
        model=Payment
        fields= ('user','payment_option', 'amount', 'memo')


      

            
        
        
    
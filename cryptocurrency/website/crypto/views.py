import email
import profile
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import crypto
from .form import CustomForm,RegisterationForm,DepositForm, UserForm, CustomForms
from django.contrib import messages
from .models import Contact,CustomUser,Currency,Payment, History, Withdrawal,Investment, Transfer
from django.contrib.auth.models import User
from django.contrib.auth.views import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from .utils import TokenGenerator
from django.conf import settings





def home(request):

    return render(request, 'crypto/home.html')

def EmailVerification(request, uidb64, token):
    try:
        uid =  force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError,ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and TokenGenerator.check_token(user, token):
        user.is_active=  True
        user.save()
        return redirect('/login')
    

def Register(request):
    if request.method=='POST':
        form = RegisterationForm(request.POST)
        forms = CustomForm(request.POST)
        if form.is_valid() and forms.is_valid():
            user = form.save()
            profile = forms.save(commit=False)
            profile.user=user
            profile.save()
            return redirect('/login')
    else:    
        form = RegisterationForm()
        forms = CustomForm()
    args = {'form':form, 'forms':forms}
    return render(request, 'crypto/register.html', args)

def ReferalRegister(request, referal):
    if request.method=='POST':
        targetuser =  CustomUser.objects.get(referal=referal)
        form = RegisterationForm(request.POST)
        forms = CustomForm(request.POST)
        if form.is_valid() and forms.is_valid():
            user = form.save()
            profile = forms.save(commit=False)
            profile.user=user
            profile.refered_by=targetuser.user
            profile.save()
            return redirect('/login')
    else:     
        form = RegisterationForm()
        forms = CustomForm()
    args = {'form':form, 'forms':forms}
    return render(request, 'crypto/register.html', args)

@login_required(login_url='/login/')  
def Dashboard(request):
    user = request.user
    payment =Payment.objects.filter(user= user).last()
    data = History.objects.filter(user = user)[:10]
    detail = CustomUser.objects.get(user=user)
    arg = {'detail':detail, 'data':data}
    return render(request, 'crypto/dashboard.html', arg)

@login_required(login_url='/login/')
def Deposit(request):
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            current = form.save(commit=False)
            current.user= request.user
            current.save()
            bills = Payment.objects.last()
            qrcode =  Currency.objects.filter(name=bills.payment_option).last()
            return render(request, 'crypto/confirmpayment.html', {'currency':current.payment_option, 'amount':current.amount, 'type':qrcode})
    else:
        form = DepositForm()
    arg = {'form':form}
    return render(request, 'crypto/deposit.html', arg)

@login_required(login_url='/login/')
def ConfirmPayment(request):
    user = request.user
    bill = Payment.objects.filter(user = user).last()
    return JsonResponse('Admin Notified About Payment', safe=False)
    
@login_required(login_url='/login/')  
def profiledetails(request):
    detail =  CustomUser.objects.get(user = request.user.id)
    arg = {'details':detail}
    return render(request, 'crypto/profiledetails.html', arg)

@login_required(login_url='/login/')  
def Referal(request):
    detail =  CustomUser.objects.all().filter(user = request.user)
    refer = CustomUser.objects.all().filter(refered_by = str(request.user.username))
    arg = {'total':refer.count(), 'refer':refer}
    return render(request, 'crypto/referal.html', arg)

@login_required(login_url='/login/')  
def history(request):
    user = request.user
    payment =Payment.objects.filter(user= user).last()
    data = History.objects.filter(user = user)
    args = {'data':data}
    return render(request, 'crypto/history.html', args)

@login_required(login_url='/login/')
def editProfile(request):
    if request.method=='POST':
        form = CustomForms( request.POST, instance=request.user.customuser)
        forms = UserForm(request.POST, instance = request.user)
        if form.is_valid() and forms.is_valid():
            data = forms.save()
            custom= form.save(commit=False)
            custom.user = data
            custom.save()
            messages.add_message(request, messages.SUCCESS, 'Profile updated!',)
            return redirect('/logout')
            
    else:
        forms =  UserForm(instance=request.user)
        form =  CustomForms(instance=request.user.customuser)
    args = {'form':form, 'forms':forms}
    return render(request, 'crypto/editprofile.html' , args)

@login_required(login_url='/login/')
def passwordreset(request):
    if request.method=='POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.add(request, 'Password has been succesfully updated!')
            return redirect('/login')
            
    else:
        form =  PasswordChangeForm(request.user)
    args = {'form':form}
    return render(request, 'crypto/passwordreset.html' , args)

@login_required(login_url='/login/') 
def RenderWithdrawal(request):
    data =  Currency.objects.all()
    args = {'data':data}
    return render(request, 'crypto/withdrawal.html', args)

@login_required(login_url='/login/') 
def MakeWithdrawal(request):
    amount = request.POST['amount']
    select = request.POST['select']
    withdraw = Withdrawal.objects.create(user= request.user, currency = select, amount= amount)
    withdraw.save()
    bal =  CustomUser.objects.get(user= request.user)
    bal.balance -= int(amount)
    bal.save()
    return JsonResponse('Succesfully placed withdrawal', safe=False)

@login_required(login_url='/login/') 
def Contactinfo(request):
        
    
    return render(request, 'crypto/contact.html')

@login_required(login_url='/login/') 
def AdminContact(request):
    name = request.POST['name']
    email = request.POST['email']
    message = request.POST['message']
    data = Contact.objects.create(name=name, email=email, message=message)
    data.save()
    return JsonResponse('DATA SUBMITTED', safe=False)


@login_required(login_url='/login/') 
def About(request):
    return render(request, 'crypto/about.html')


@login_required(login_url='/login/') 
def investment(request):
    
    return render(request, 'crypto/investment.html')

@login_required(login_url='/login/') 
def ActiveInvestment(request):
    
    return render(request, 'crypto/active.html')

@login_required(login_url='/login/') 
def SubmitInvestment(request):
    amount = request.POST['amount']
    select = request.POST['select']
    invest = Investment.objects.create(user= request.user, Plan= select, amount= amount, status = True)
    invest.save()
    bal =  CustomUser.objects.get(user= request.user)
    bal.balance -= int(amount)
    bal.save()
    return JsonResponse('Investment successfully', safe=False)

@login_required(login_url='/login/') 
def Faq(request):

    return render(request, 'crypto/Faq.html')

@login_required(login_url='/login/') 
def transfer(request):
    amount = request.POST['amount']
    username = request.POST['username']
    transfer = Transfer.objects.create(user= request.user, reciever=username, amount=amount, status = True  )
    bal =  CustomUser.objects.get(user= request.user)
    bal.balance -= int(amount)
    bal.save()
    recieved = User.objects.get(username=username)
    custom = CustomUser.objects.get(user = recieved.pk)
    custom.balance += int(amount)
    custom.save()
    transfer.save()

    return JsonResponse('Transfer successful', safe=False)


@login_required(login_url='/login/') 
def InitiateTransfer(request):
    
    return render(request, 'crypto/transfer.html')




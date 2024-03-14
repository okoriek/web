from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from .form import CustomForm,RegisterationForm,DepositForm, UserForm, CustomForms
from django.contrib import messages
from .models import Contact,CustomUser,Currency,Payment, History, Withdrawal,Investment, Transfer, Plan, SystemEaring, ReferalBonus, Reinvestment, NotificationVisibility
from django.contrib.auth.models import User
from django.contrib.auth.views import login_required
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from .utils import TokenGenerator, SendReferalMail, SendEmail
from django.utils import timezone
from datetime import datetime





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
        messages.add_message(request, messages.SUCCESS, 'Email verification complete' )
        return redirect('/login')
    

def Register(request):
    if request.method=='POST':
        form = RegisterationForm(request.POST)
        forms = CustomForm(request.POST)
        if form.is_valid() and forms.is_valid():
            user = form.save(commit=False)
            user.is_active =False
            user.save()
            profile = forms.save(commit=False)
            profile.user=user
            profile.save()

            website = get_current_site(request).domain
            email_subject = 'Email Verification'
            email_body =  render_to_string('email/activation.html',{
                'user':user.username,
                'domain':website,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': TokenGenerator.make_token(user)
            })
            email = EmailMessage(subject=email_subject, body=email_body,
                from_email='Apexfortitude <admin@apexfortitude.com>', to=[user.email]
                )
            email.content_subtype = 'html'
            email.send()
            messages.success(request, 'A Verification mail has been sent to your email or spam box')
            return redirect('/login')
    else:    
        form = RegisterationForm()
        forms = CustomForm()
    args = {'form':form, 'forms':forms}
    return render(request, 'crypto/register.html', args)

def ReferalRegister(request, referal):
    if request.method=='POST':
        referer =  CustomUser.objects.get(referal=referal)
        form = RegisterationForm(request.POST)
        forms = CustomForm(request.POST)
        if form.is_valid() and forms.is_valid():
            user = form.save(commit=False)
            user.is_active =False
            user.save()
            profile = forms.save(commit=False)
            profile.user=user
            profile.refered_by=str(referer.user)
            profile.save()


            website = get_current_site(request).domain
            email_subject = 'Email Verification'
            email_body =  render_to_string('email/activation.html',{
                'user':user.username,
                'domain':website,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': TokenGenerator.make_token(user)
            })
            email = EmailMessage(subject=email_subject, body=email_body,
                from_email='Apexfortitude <admin@apexfortitude.com>', to=[user.email]
                )
            email.content_subtype = 'html'
            email.send()
            SendReferalMail(user,referer)
            messages.success(request, 'A Verification mail has been sent to your email or spam box')
            return redirect('/login')
    else:     
        form = RegisterationForm()
        forms = CustomForm()
    args = {'form':form, 'forms':forms}
    return render(request, 'crypto/register.html', args)




@login_required(login_url='/login/')  
def Dashboard(request):
    earn =  SystemEaring.objects.filter(user =  request.user, is_active=True)
    invest =  Investment.objects.filter(user =request.user, is_active=True)
    for x in earn:
        
        x.save()
    for y in invest:
        y.save()
    user = request.user
    data = History.objects.filter(user = user)[:10]
    detail = CustomUser.objects.get(user=user)

    #referer

    details =  CustomUser.objects.get(user = request.user)
    refer = CustomUser.objects.all().filter(refered_by = str(request.user.username))
    bonus = ReferalBonus.objects.all().filter(user=str(request.user))
    total = 0
    for i in bonus:
        total += i.earnings
    arg = {'detail':detail, 'data':data, 'total':refer.count(), 'refer': details.referal, 'earnings':total}
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
    detail =  CustomUser.objects.get(user = request.user)
    refer = CustomUser.objects.all().filter(refered_by = str(request.user.username))
    bonus = ReferalBonus.objects.all().filter(user=str(request.user))
    total = 0
    for i in bonus:
        total += i.earnings
    arg = {'total':refer.count(), 'refer': detail.referal, 'earning':total}
    return render(request, 'crypto/referal.html', arg)

@login_required(login_url='/login/')  
def history(request):
    user = request.user
    data = History.objects.filter(user = user)
    args = {'data':data}
    return render(request, 'crypto/history.html', args)

@login_required(login_url='/login/')  
def deposithistory(request):
    user = request.user
    data = History.objects.filter(user = user, action='Deposit')
    args = {'data':data}
    return render(request, 'crypto/history.html', args)

@login_required(login_url='/login/')  
def withdrawalhistory(request):
    user = request.user
    data = History.objects.filter(user = user, action='Withdrawal')
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


def Contactinfo(request):
        
    
    return render(request, 'crypto/contact.html')


def terms(request):

    return render(request, 'crypto/terms.html')


def AdminContact(request):
    name = request.POST['name']
    email = request.POST['email']
    message = request.POST['message']
    data = Contact.objects.create(name=name, email=email, message=message)
    data.save()
    return JsonResponse('DATA SUBMITTED', safe=False)



def About(request):
    return render(request, 'crypto/about.html')



def investment(request):
    
    return render(request, 'crypto/investment.html')

@login_required(login_url='/login/') 
def ActiveInvestment(request):
    invest =  Plan.objects.all().values
    args = {'invest':invest}
    return render(request, 'crypto/active.html', args)

@login_required(login_url='/login/') 
def SubmitInvestment(request):
    amount = request.POST['amount']
    select = request.POST['select']

    reinvest = Reinvestment.objects.filter(user=request.user, plan=select)

    if reinvest.exists():
        counting = Reinvestment.objects.get(user=request.user, plan=select)
        if counting.plan == 'Starter' and counting.number_of_investment < 2 or counting.plan == 'Premium' and counting.number_of_investment <4:
            invest = Investment.objects.create(user= request.user, plan= select, amount= amount, is_active= True)
            referal =  CustomUser.objects.get(user=request.user)

            def Earn():
                if select == 'Starter':
                    return 2
                elif select == 'Premium':
                    return 3
                else:
                    return 5
            ReferalBonus.objects.create(user = str(referal.refered_by), earnings = Earn())
            bal =  CustomUser.objects.get(user= request.user)
            bal.balance -= int(amount)
            bal.save()
            counting.number_of_investment += 1
            counting.save()
            return JsonResponse('Investment successfully', safe=False)
        else:
            return JsonResponse(f"Number of Reinvestment reached for {select}", safe=False)
    else:
        new = Reinvestment.objects.create(user=request.user, plan=select)
        invest = Investment.objects.create(user= request.user, plan= select, amount= amount, is_active= True)
        referal =  CustomUser.objects.get(user=request.user)

        def Earn():
            if select == 'Starter':
                return 2
            elif select == 'Premium':
                return 3
            else:
                return 5
        ReferalBonus.objects.create(user = str(referal.refered_by), earnings = Earn())
        bal =  CustomUser.objects.get(user= request.user)
        bal.balance -= int(amount)
        bal.save()
        new.number_of_investment += 1
        new.save()
        return JsonResponse('Investment successfully', safe=False)
 
def Faq(request):

    return render(request, 'crypto/faq.html')

@login_required(login_url='/login/') 
def transfer(request):
    amount = request.POST['amount']
    username = request.POST['username']
    transfer = Transfer.objects.create(user= request.user, reciever=username, amount=amount, status = False )
    transfer.save()

    return JsonResponse('Transfer Pending', safe=False)


@login_required(login_url='/login/') 
def InitiateTransfer(request):
    
    return render(request, 'crypto/transfer.html')


@login_required(login_url='/login/') 
def notification(request):
    user = request.user
    id =  request.POST['id']
    data = NotificationVisibility.objects.update_or_create(user = user, notification_id=int(id))
    data.save()
    return JsonResponse('successfully updated', safe=False)


def DisplayEmail(request):

    return render(request, 'crypto/mailsending.html')



def SendBulkEmail(request):
    email  =  request.POST['email']
    subject =  request.POST['subject']
    val = request.POST['value']
    message =  request.POST['message']

    if val == 'true':
        item = User.objects.all()
        for i in item:
            user = {
                'username': i.username,
                'email': i.email
            }
            SendEmail(subject, user, message)
    else:
        item = User.objects.filter(email = email)
        for i in item:
            user = {
                'username': i.username,
                'email': i.email
            }
            SendEmail(subject, user, message)
    return JsonResponse({'message': 'Email Successfully Sent'})






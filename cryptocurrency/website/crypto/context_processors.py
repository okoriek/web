from .models import CustomUser, History, Notification,SystemEaring, Investment
from django.contrib.auth.models import User

def TotalDeposit(request):
    try:
        amount= CustomUser.objects.get(user=request.user)
        bal = amount.balance
        return {'balance':bal}
    except:
        return {'balance':None}
    
def PendingWithdrawal(request):
    try:
        bal = History.objects.filter(user=request.user, status=False, action= 'Withdrawal')
        total = 0
        for i in  bal:
            total  += int(i.amount)
        return {'withdraw': total}
    except:
        return {'withdraw': None}
def TotalWithdrawal(request):
    try:
        bal = History.objects.filter(user=request.user, status=True, action= 'Withdrawal')
        total = 0
        for i in  bal:
            total  += int(i.amount)
        return {'confirm': total}
    except:
        return {'confirm': None}
    

def ActiveDeposit(request):
    try:
        bal = Investment.objects.filter(user=request.user, is_active=True)
        total = 0
        for i in  bal:
            total  += int(i.amount)
        return {'invest': total}
    except:
        return {'invest': None}
    
def ActiveEarnings(request):
    try:
        bal = SystemEaring.objects.filter(user=request.user, is_active=True)
        total = 0
        for i in  bal:
            total  += int(i.balance)
        return {'earning': total}
    except:
        return {'earning': None}
    
def Notify(request):
    try:
        notify = Notification.objects.all().count()
        return {'num':notify}
    except:
        return {'num': None, 'data':None}
    
def Message(request):
    try:
        data = Notification.objects.all().filter(ended = False)
        return {'item':data}
    except:
        return {'item':None}



    







    



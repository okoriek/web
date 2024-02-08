from .models import CustomUser, History, Notification,SystemEaring, Investment, NotificationVisibility
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
    data = NotificationVisibility.objects.filter(user = request.user)
    val = []
    try:
        for i in data:
            notify = Notification.objects.all().exclude(i.notification_id)
            val.append(notify)
        return {'num':val.count()}
    except:
        return {'num': None, 'data':None}
    
def Message(request):
    raw_data = NotificationVisibility.objects.filter(user = request.user)
    data = []
    try:
        for i in raw_data: 
            obj = Notification.objects.all().filter(ended = False).exclude(i.notification_id)
            data.append(obj)
        return {'item':data}
    except:
        return {'item':None}



    







    



from .models import CustomUser, History
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
        bal = History.objects.filter(user=request.user, status=True, action= 'Investment')
        total = 0
        for i in  bal:
            total  += int(i.amount)
        return {'invest': total}
    except:
        return {'invest': None}




    



from collections.abc import Iterable
from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.utils import timezone
from django_countries.fields import CountryField
import qrcode
from django.core.files import File
from PIL import Image, ImageDraw
from io import BytesIO
from decimal import Decimal


class CustomUser(models.Model):
    user =  models.OneToOneField(User, on_delete=models.CASCADE , blank=True, null=False)
    balance = models.IntegerField(blank=True, null=True)
    referal = models.CharField(max_length=6, unique=True, blank=True, null=True)
    refered_by = models.CharField(max_length=50, blank=True, null=True)
    btc_wallet = models.CharField(max_length=300, blank=True, null=True)
    eth_wallet = models.CharField(max_length=300, blank=True, null=True)
    usdt_trc20_wallet = models.CharField(max_length=300, blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    country = CountryField(verbose_name='countries')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    def save(self, *args, **kwargs):
        self.referal = get_random_string(6)
        super().save(*args, **kwargs)
    

class Contact(models.Model):
    name =  models.CharField(max_length=300)
    email =  models.EmailField(max_length=200)
    message = models.TextField(max_length=1000)

    def __str__(self):
        return f"{self.name}  {self.email}"
    

class Currency(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    rate = models.CharField(max_length=20, blank=True, null=True)
    wallet_id = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to='wallet/', blank=True, null=True)

    class Meta:
        verbose_name_plural='Currencies'

    def __str__(self):
        return self.name
    

    def save(self, *args, **kwargs):
        img = qrcode.make(self.wallet_id)
        canvas = Image.new('RGB',(390,390), 'white')
        draw = ImageDraw.Draw(canvas)
        canvas.paste(img)
        name = f'{self.name}QRCODE.png'
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        self.image.save(name, File(buffer), save=False)
        canvas.close()
        super().save(*args, **kwargs)




class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    payment_option= models.ForeignKey(Currency, on_delete=models.DO_NOTHING, blank=True, null=True)
    amount = models.FloatField()
    memo = models.CharField(max_length=200, blank=True, null=True)
    status = models.BooleanField(default=False) 
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.payment_option} {self.amount}"
    
    def save(self, *args, **kwargs):
        if self.status == True:
            account = self.user.customuser
            payment = Currency.objects.get(name = str(self.payment_option))
            total = self.amount/float(payment.rate)
            account.balance =+ total
            account.save()
        super().save(*args, **kwargs)

class Investment(models.Model):
    choice = (
        ('Starter', 'Starter'),
        ('Premium', 'Premium'),
        ('Vip', 'Vip'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    Plan = models.CharField(max_length=100, choices=choice, default='Starter')
    amount = models.FloatField()
    status = models.BooleanField(default=False) 
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}  {self.amount} {self.date_created}"  
     
class Withdrawal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    currency = models.CharField(max_length=20, blank=True, null=True)
    amount = models.IntegerField()
    status = models.BooleanField(default=False) 
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.currency} {self.amount}"
    

class Transfer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    reciever = models.CharField(max_length=20, blank=True, null=True)
    amount = models.IntegerField()
    status = models.BooleanField(default=False) 
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.amount}      {self.reciever}"
    
class History(models.Model):
    choice  =  (
        ('Withdrawal', 'Withdrawal'),
        ('Deposit', 'Deposit'),
        ('Transfer', 'Transfer'),
        ('Investment', 'Investment'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, blank=True, null=True)
    withdraw = models.ForeignKey(Withdrawal, on_delete=models.CASCADE, blank=True, null=True)
    invest = models.ForeignKey(Investment, on_delete=models.CASCADE, blank=True, null=True)
    action =  models.CharField(max_length=200, choices=choice, blank=True, null=True, editable=False)
    currency = models.CharField(max_length=20, blank=True, null=True)
    amount = models.CharField(max_length=20)
    status = models.BooleanField(default=False) 
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural ='Histories'
        ordering = ('-date_created',)

    def __str__(self):
        return f"{self.currency}   {self.amount}"







    







    




   
        
    

    
    


    



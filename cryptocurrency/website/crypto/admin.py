from django.contrib import admin
from .models import CustomUser, Payment,Currency, History, Withdrawal, Investment, Transfer

admin.site.register(CustomUser)
admin.site.register(Payment)
admin.site.register(Currency)
admin.site.register(History)
admin.site.register(Withdrawal)
admin.site.register(Investment)
admin.site.register(Transfer)






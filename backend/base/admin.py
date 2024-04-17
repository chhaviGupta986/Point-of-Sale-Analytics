from django.contrib import admin
from .models import User, Links, Test, DemandForecasting

admin.site.register(User)
admin.site.register(Links)
admin.site.register(Test)
admin.site.register(DemandForecasting)
from django.contrib import admin

from users.models import Profile, User

# Register your models here.

admin.site.register(User,list_display=['username','email','profile_picture','profile','noms','email_verified'])
admin.site.register(Profile,list_display=['id','name'])

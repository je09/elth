from django.contrib import admin
from .models import Lesson, Lesson_Name

class Lesson_Admin(admin.ModelAdmin):
    list_display = ['date', 'weekday', 'group', 'time']

admin.site.register(Lesson, Lesson_Admin)
admin.site.register(Lesson_Name)
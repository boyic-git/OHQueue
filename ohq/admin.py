from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Student, Instructor, Course, Queue

class UserAdmin(admin.ModelAdmin):
    fields = ["user", "first_name"]

class InstructorAdmin(admin.ModelAdmin):
    fields = []

class CourseAdmin(admin.ModelAdmin):
    fields = ["code", "course_name", "semester", "status", ]

class QueueAdmin(admin.ModelAdmin):
    fields = ["course", "student", "question", ]

# Register your models here.
admin.site.unregister(Group)
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
admin.site.register(Student)
admin.site.register(Instructor)
admin.site.register(Course, CourseAdmin)
admin.site.register(Queue, QueueAdmin)
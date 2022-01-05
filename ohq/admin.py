from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Student, Instructor, Course, Queue

# class UserAdmin(admin.ModelAdmin):
#     fields = ["user", "first_name"]

class UserAdmin(admin.ModelAdmin):
    # readonly_fields = ["user__last_name"]
    # ordering = ["user__last_name"]
    list_display = ["full_name", "email"]
    search_fields = ["user__first_name", "user__last_name", "user__email"]

    def full_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name

    def email(self, obj):
        return obj.user.email

class CourseAdmin(admin.ModelAdmin):
    search_fields = ["code", "course_name", ]
    list_display = ["full_course_name", "code", "course_name", "semester", ]
    fields = ["code", "course_name", "semester", "status", ]
    
    def full_course_name(self, obj):
        return str(obj)

class QueueAdmin(admin.ModelAdmin):
    list_display = ["course__code", "student", "question", "invited", "joined_time"]
    fields = ["course", "student", "question", "joined_time", "invited", "instructor"]
    readonly_fields = ["joined_time"]

    def course__code(self, obj):
        return obj.course.code

# Register your models here.
admin.site.unregister(Group)
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
admin.site.register(Student, UserAdmin)
admin.site.register(Instructor, UserAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Queue, QueueAdmin)
from django.contrib import admin
from .models import Student, Instructor, TA, Course, Queue

class CourseAdmin(admin.ModelAdmin):
    fields = ["code", "course_name", "semester", "status", ]

class QueueAdmin(admin.ModelAdmin):
    fields = ["course", "student", "question", ]

# Register your models here.
admin.site.register(Student)
admin.site.register(Instructor)
admin.site.register(TA)
admin.site.register(Course, CourseAdmin)
admin.site.register(Queue, QueueAdmin)
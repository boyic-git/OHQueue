from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Student, Instructor, TA, Course, Queue
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate

# Create your views here.
class CourseListView(generic.ListView):
    template_name = "course_list.html"
    context_object_name = "course_list"

    def get_queryset(self):
        courses = Course.objects.all()
        return courses


def search(request):
    template = "ohq/search.html"

    return render(request, template)

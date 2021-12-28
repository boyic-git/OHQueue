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
    model = Course
    template_name = "course_list.html"
    context_object_name = "course_list"

    # def get_queryset(self):
    #     courses = Course.objects.all()
    #     return courses

def search(request):
    template = "ohq/search.html"

    return render(request, template)

class CourseQueueView(generic.DetailView):
    model = Course
    template_name = "ohq/course_queue_instructor.html"

# Different views for different user types
# https://stackoverflow.com/questions/54158999/django-show-different-content-based-on-user

def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST["user[username]"]
        password = request.POST["user[password]"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            # http://localhost:8000/login_request
            if request.META['HTTP_REFERER'][-13:] == "login_request":
                return redirect("ohq:index")
            return redirect(request.META['HTTP_REFERER'])
        else:
            context["message"] = "Invalid username or password!"
            return render(request, "ohq/login.html", context)
    else:
        return render(request, "ohq/login.html", context)

def logout_request(request):
    logout(request)
    return redirect("ohq:index")
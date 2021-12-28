from django.db.models import constraints
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


def check_is_instructor(user, course):
    is_instructor = False
    if user.id is not None:
        results = Instructor.objects.filter(user=user, course=course).count()
        if results > 0:
            is_instructor = True
    return is_instructor

class CourseQueueView(generic.DetailView):
    model = Course
    template_name = "ohq/course_queue.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = get_object_or_404(Course, pk=self.kwargs["pk"])
        context["is_instructor"] = check_is_instructor(self.request.user, course)
        # print(context)
        return context

def change_queue_status(request, pk):
    if request.method == "POST":
        course = get_object_or_404(Course, pk=pk)
        is_instructor = check_is_instructor(request.user, course)
        if is_instructor:
            course.status = not course.status
            course.save()
    return redirect(request.META['HTTP_REFERER'])
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
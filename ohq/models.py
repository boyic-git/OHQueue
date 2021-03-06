from django.db import models
from django.contrib.auth.models import User
from django.db.models.lookups import In

# Subject code
CPEN = "CPEN"
CPSC = "CPSC"
EECE = "EECE"
ELEC = "ELEC"
SUBJECT_CODE = [(CPEN, "CPEN"),
                (CPSC, "CPSC"),
                (EECE, "EECE"),
                (ELEC, "ELEC")]

# semester
W1 = "W1"
W2 = "W2"
S = "S"
SEMESTER = [(W1, "W1"),
            (W2, "W2"),
            (S, "S")]

def get_name_and_email_for_user(self):
    return self.first_name + " " + self.last_name + " (" + self.email + ")"
User.add_to_class("__str__", get_name_and_email_for_user)

class Course(models.Model):
    code = models.CharField(max_length=10)
    subject = models.CharField(null=False,
        max_length=5,
        choices=SUBJECT_CODE,
        default=CPEN)
    number = models.IntegerField(default=0)
    session = models.CharField(max_length=5, default="")
    semester = models.CharField(null=False,
        max_length=2,
        choices=SEMESTER,
        default=W1)
    course_name = models.CharField(max_length=100, default="")
    status = models.BooleanField(default=False)
    meeting_link = models.URLField(default="")
    teaching_instructor = models.ManyToManyField("Instructor")

    def __str__(self):
        if self.course_name:
            return self.code + ": " + self.course_name
        return self.code

# Student
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_name = models.CharField(max_length=200, default="")
    starred_course = models.ManyToManyField(Course, blank=True)

    def save(self, *args, **kwargs):
        if not self.preferred_name:
            self.preferred_name = self.user.first_name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

# Instructor (not including TAs)
class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    teaching_course = models.ManyToManyField(Course)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

class Queue(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    instructor = models.ManyToManyField(Instructor)
    question = models.CharField(max_length=500, default="")
    joined_time = models.DateTimeField(auto_now_add=True)
    ## if invited, not showing in instructor's waiting student queue,
    ## but showing in the serving queue
    invited = models.BooleanField(default=False)

    def __str__(self):
        return self.course.code + ": " + self.student.user.first_name \
            + " " + self.student.user.last_name


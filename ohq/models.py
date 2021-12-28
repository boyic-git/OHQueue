from django.db import models
from django.contrib.auth.models import User

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

    def __str__(self):
        if self.course_name:
            return self.code + ": " + self.course_name
        return self.code

# Student
class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20, default="")
    last_name = models.CharField(max_length=20, default="")
    preferred_name = models.CharField(max_length=20, default="")

    def __str__(self):
        return self.first_name + " " + self.last_name

# Instructor (not including TAs)
class Instructor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20, default="")
    last_name = models.CharField(max_length=20, default="")
    preferred_name = models.CharField(max_length=20, default="")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.first_name + " " + self.last_name

# TA (also a student)
class TA(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20, default="")
    last_name = models.CharField(max_length=20, default="")
    preferred_name = models.CharField(max_length=20, default="")

    def __str__(self):
        return self.first_name + " " + self.last_name



class Queue(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ManyToManyField(Student)
    instructor = models.ManyToManyField(Instructor)
    ta = models.ManyToManyField(TA)
    question = models.CharField(max_length=500, default="")

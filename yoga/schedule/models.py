import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from datetime import date
from yogaapp.models import RegisteredInstructor, Courses, RegisteredStudent
from django.utils import timezone
from yogaapp.purchase import CoursePurchase


class ClassSchedule(models.Model):
    STATUS_C = (
        ('Upcoming', 'Upcoming'),
        ('Ongoing', 'Ongoing'),
        ('Ended', 'Ended'),
    )
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    meeting_url = models.URLField()
    instructor = models.ForeignKey(RegisteredInstructor, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_C, default='Upcoming')
    course_purchase = models.ForeignKey(CoursePurchase, on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return f"{self.course.course} - {self.start_time}"
    def update_status(self):
        now = timezone.now()
        start_time = self.start_time.astimezone(timezone.get_current_timezone())
        end_time = self.end_time.astimezone(timezone.get_current_timezone())

        if now < start_time:
            self.status = 'Upcoming'
        elif start_time <= now <= end_time:
            self.status = 'Ongoing'
        else:
            self.status = 'Ended'

        self.save()

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('ABSENT', 'Absent'),
        ('PRESENT', 'Present')
    )
    student = models.ForeignKey(RegisteredStudent, on_delete=models.CASCADE)
    class_schedule = models.ForeignKey(ClassSchedule, on_delete=models.CASCADE)
    is_present = models.CharField(choices=STATUS_CHOICES, max_length=10, default='ABSENT')

    def __str__(self):
        return f"{self.student} - {self.class_schedule}"



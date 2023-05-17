from django.db import models
from django.contrib.auth.models import User

from yogaapp.models import Courses


class CoursePurchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    purchase_date = models.DateField(auto_now=True)
    end_date = models.DateField(null=True)

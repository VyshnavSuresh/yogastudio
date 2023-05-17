from django.db import models
from yogaapp.models import RegisteredInstructor


class YogaPoseData(models.Model):
    name = models.CharField(max_length=100)
    data = models.JSONField()
    instructor = models.ForeignKey(RegisteredInstructor, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='audio/',default='')

    def __str__(self):
        return self.name
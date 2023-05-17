from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import ClassSchedule
from django import forms
from django.utils.html import format_html



class ClassScheduleForm(forms.ModelForm):
    class Meta:
        model = ClassSchedule
        fields = ['start_time', 'end_time', 'meeting_url']
        widgets = {
            'start_time': forms.TextInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.TextInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'meeting_url': forms.TextInput(attrs={'class': 'form-control'}),
        }




    # def clean(self):
    #     cleaned_data = super().clean()
    #     start_time = cleaned_data.get('start_time')
    #     end_time = cleaned_data.get('end_time')
    #
    #     if start_time and end_time:
    #         tz = timezone.get_current_timezone()
    #         start_time_str = start_time.strftime('%Y-%m-%dT%H:%M')
    #         end_time_str = end_time.strftime('%Y-%m-%dT%H:%M')
    #         start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
    #         end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
    #         if start_time.tzinfo is None:
    #             start_time = timezone.make_aware(start_time, tz)
    #         if end_time.tzinfo is None:
    #             end_time = timezone.make_aware(end_time, tz)
    #
    #         now = timezone.now()
    #         if start_time < now:
    #             raise ValidationError('Start time cannot be in the past.')
    #         if end_time < now:
    #             raise ValidationError('End time cannot be in the past.')
    #         if start_time >= end_time:
    #             raise ValidationError('End time must be after start time.')
    #         duration = end_time - start_time
    #         if duration < timedelta(hours=1) or duration > timedelta(hours=3):
    #             raise ValidationError('Class duration must be between 1 and 3 hours.')





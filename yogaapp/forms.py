import re

from django import forms
from django.utils.html import format_html
from .models import Videos, DeliveryAddress, Courses, RegisteredInstructor, Salary


class VideoForm(forms.ModelForm):
    title = forms.CharField(label='Title of the Video', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    video = forms.FileField(label='Video', widget=forms.FileInput(attrs={'accept': 'video/*'}))
    course = forms.ModelChoiceField(label='Course', queryset=None, widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, ins, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Courses.objects.filter(user_id=ins)

    class Meta:
        model = Videos
        fields = ['title', 'video', 'course']




class DeliveryAddressForm(forms.ModelForm):
    recipient_name = forms.CharField(label='Full Name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(label='Address', max_length=255, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))
    city = forms.CharField(label='City', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    state = forms.CharField(label='State', max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    zip_code = forms.CharField(label='Zip Code', max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = DeliveryAddress
        fields = ('recipient_name', 'address', 'city', 'state', 'zip_code')



    def clean_recipient_name(self):
        recipient_name = self.cleaned_data.get('recipient_name')
        if not recipient_name:
            raise forms.ValidationError('<span style="color:red;">This field is required</span>')
        name_parts = recipient_name.strip().split(' ')
        if len(name_parts) != 2 or not all(part.isalpha() for part in name_parts):
            error_message = 'Enter your first and last name with a space in between, using only alphabetic characters'
            raise forms.ValidationError(format_html('<span style="color:red;">{}</span>', error_message))
        return recipient_name

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address:
            raise forms.ValidationError('This field is required.')
        if len(address) < 10:
            raise forms.ValidationError('Address is too short.')
        if len(address) > 100:
            raise forms.ValidationError('Address is too long.')
        if not re.match(r'^[a-zA-Z0-9\s\.,#-]+$', address):
            raise forms.ValidationError('Address contains invalid characters.')
        # add any additional validations as needed for your specific use case
        return address

    def clean_city(self):
        city = self.cleaned_data.get('city')
        if not city:
            raise forms.ValidationError('This field is required.')
        if not re.match(r'^[a-zA-Z\s]+$', city):
            raise forms.ValidationError('City name should only contain alphabetic characters.')
        return city

    def clean_state(self):
        state = self.cleaned_data.get('state')
        if not state:
            raise forms.ValidationError('This field is required.')
        if not re.match(r'^[a-zA-Z\s]+$', state):
            raise forms.ValidationError('State name should only contain alphabetic characters.')
        return state

    def clean_zip_code(self):
        zip_code = self.cleaned_data.get('zip_code')
        if not zip_code:
            raise forms.ValidationError('This field is required.')
        if not re.match(r'^\d{6}$', zip_code):
            raise forms.ValidationError('Zip code should be 6 digits long.')
        return zip_code



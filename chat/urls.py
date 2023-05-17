from django.urls import path
from .import views

app_name="chat"

urlpatterns=[
    path("<int:c_id>",views.Sentmessage,name="sentmsg")
]
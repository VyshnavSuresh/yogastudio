from django.urls import path
from .import views

app_name="posecollection"

urlpatterns=[

    path('capture_pose', views.capture_pose, name='capture_pose'),
    path('inFrame', views.inFrame, name='inFrame'),
    path('train_model', views.train_model, name='train_model'),
    path('inf', views.inf, name='inf'),
    path('pose_list', views.pose_list, name='pose_list')
]
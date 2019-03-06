from django.urls import path

from oauth import views

app_name = 'oauth'

urlpatterns = [
    path('autologin/', views.AutoLogin.as_view(), name='autologin'),
    path('callback/', views.Callback.as_view(), name='auth_callback'),
]

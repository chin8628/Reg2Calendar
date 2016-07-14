from django.conf.urls import url, include
from genclass import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^success/', views.success, name="success"),
    url(r'^help/', views.help, name="help"),
]

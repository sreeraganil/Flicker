from django.urls import path
from . import views

app_name = "wallpapers"

urlpatterns = [
    path("", views.home, name="home"),
    path("upload/", views.upload, name="upload"),
    path("w/<slug:slug>/", views.detail, name="detail"),
    path("w/<slug:slug>/download/", views.download, name="download"),
]

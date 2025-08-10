from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate/', views.generate_story, name='generate_story'),
    path('story/<int:story_id>/', views.story_detail, name='story_detail'),
]
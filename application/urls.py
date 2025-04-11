from django.urls import path
from application import views
#Set-ExecutionPolicy Unrestricted -Scope Process

urlpatterns = [
    path('club/', views.clubPage, name='clubPage'),
    path('event/create/', views.create_event, name='create_event'),
    path('event/event_list', views.event_list, name='event_list'),
    path('event/update/<int:event_id>/', views.update_event, name='update_event'),
    path('event/delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('create_club/', views.create_club, name='create_club'),
    path('join_club/', views.join_club, name='join_club'),
    path('event/register_event/<int:event_id>/', views.register_event, name ="register_event"),
    path('event/event_details/<int:event_id>/', views.event_details, name = "event_details"),
    path('event/user_events', views.user_events, name = "user_events"),
    path('virtual-payment/', views.virtual_payment, name='virtual_payment'),

]


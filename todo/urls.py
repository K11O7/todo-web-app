from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('toggle/<int:todo_id>/', views.toggle_complete, name='toggle'),
    path('delete/<int:todo_id>', views.delete_todo, name='delete'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('edit/<int:todo_id>/', views.edit_todo, name='edit'),
]
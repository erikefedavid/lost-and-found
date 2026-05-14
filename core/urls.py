from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('report/lost/', views.report_lost, name='report_lost'),
    path('report/found/', views.report_found, name='report_found'),
    path('browse/', views.browse, name='browse'),
    path('item/<str:item_type>/<int:item_id>/', views.item_detail, name='item_detail'),
    path('notifications/', views.notifications, name='notifications'),
    path('profile/', views.profile, name='profile'),
]

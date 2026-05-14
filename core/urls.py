from django.urls import path
from django.contrib.auth import views as auth_views
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
    
    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='core/registration/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/registration/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='core/registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='core/registration/password_reset_complete.html'), name='password_reset_complete'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Custom Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-dashboard/api/user/<int:user_id>/detail/', views.admin_user_detail_api, name='admin_user_detail_api'),
    path('admin-dashboard/api/user/<int:user_id>/toggle-active/', views.admin_user_toggle_active_api, name='admin_user_toggle_active_api'),
    path('admin-dashboard/api/user/<int:user_id>/toggle-staff/', views.admin_user_toggle_staff_api, name='admin_user_toggle_staff_api'),
    path('admin-dashboard/api/user/<int:user_id>/reset-quota/', views.admin_user_reset_quota_api, name='admin_user_reset_quota_api'),
    path('admin-dashboard/api/user/<int:user_id>/change-password/', views.admin_user_change_password_api, name='admin_user_change_password_api'),
]
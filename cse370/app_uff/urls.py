from django.urls import path
from . import views

app_name = 'app_uff'

urlpatterns = [
    path('', views.home, name='home'), 
    path('register/', views.registration_view, name="register"),
    path('logout/', views.logout_view, name="logout"),
    path('login/', views.login_view, name="login"),
    path('jobs', views.freelancer_view, name="freelancer_home"),
    path('add_job/', views.add_job, name="add_job"),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('job/<int:job_id>/manage_application/<int:applicant_id>/', views.manage_application, name='manage_application'),
    path('freelancer/<int:freelancer_id>/', views.freelancer_profile, name='freelancer_profile'),
    path('employer/<int:employer_id>/', views.employer_profile, name='employer_profile'),
    path('profile/edit_freelancer/', views.edit_freelancer_profile, name='edit_freelancer_profile'),
    path('profile/edit_employer/', views.edit_employer_profile, name='edit_employer_profile'),
    path('profile/job_offers/', views.job_offers, name='job_offers'),
    path('admin_panel/', views.admin_view, name='admin_panel'),
    path('admin_panel/edit_job/<int:job_id>/', views.edit_job_admin, name='edit_job_admin'),
    path('admin_panel/delete_job/<int:job_id>/', views.delete_job_admin, name='delete_job_admin'),
    path('admin_panel/suspend_user/<int:user_id>/', views.suspend_user_admin, name='suspend_user_admin'),
    path('admin_panel/activate_user/<int:user_id>/', views.activate_user_admin, name='activate_user_admin'),
    # ...

]
from django.contrib import admin
from .models import Account, EmployerProfile, FreelancerProfile, Job, JobApplication
# Register your models here.


admin.site.register(Account)
admin.site.register(EmployerProfile)
admin.site.register(FreelancerProfile)
admin.site.register(Job)
admin.site.register(JobApplication)
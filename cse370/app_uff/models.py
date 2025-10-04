from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.
class MyAccountManager(BaseUserManager):
	def create_user(self, email, username, password=None, is_employer=False, is_freelancer=False):
		if not email:
			raise ValueError('Users must have an email address')
		if not username:
			raise ValueError('Users must have a username')

		user = self.model(
			email=self.normalize_email(email),
			username=username,
			is_employer=is_employer,
			is_freelancer=is_freelancer,
		)

		user.set_password(password)
		user.save(using=self._db)
		
		return user

	def create_superuser(self, email, username, password):
		user = self.create_user(
			email=self.normalize_email(email),
			password=password, 
			username=username,
		)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user
	

class Account(AbstractBaseUser):
	email = models.EmailField(verbose_name="email", max_length=50, unique=True)
	username = models.CharField(max_length=50)
	date_joined				= models.DateTimeField(verbose_name='date joined', auto_now_add=True)
	last_login				= models.DateTimeField(verbose_name='last login', auto_now=True)
	is_admin				= models.BooleanField(default=False)
	is_active				= models.BooleanField(default=True)
	is_staff				= models.BooleanField(default=False)
	is_superuser			= models.BooleanField(default=False)
	

	is_employer = models.BooleanField(default=False)
	is_freelancer = models.BooleanField(default=False)

	 
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']

	objects = MyAccountManager()
	
	def __str__(self):
		return self.email

	# For checking permissions. to keep it simple all admin have ALL permissons
	def has_perm(self, perm, obj=None):
		return self.is_admin

	# Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY) 
	def has_module_perms(self, app_label):
		return True
	


class EmployerProfile(models.Model):
	user = models.OneToOneField(Account, on_delete=models.CASCADE)
	company_name = models.CharField(max_length=255, blank=True)
	company_description = models.TextField(blank=True)
	website = models.URLField(blank=True)
	industry = models.CharField(max_length=100, blank=True)  # e.g., "Technology", "Finance", "Healthcare"
	company_size = models.CharField(max_length=50, blank=True)  # e.g., "1-10 employees", "50-200 employees"
	location = models.CharField(max_length=100, blank=True)  # City, State or Region
	contact_email = models.EmailField(blank=True)  # Public contact email for the company
	#logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)  # Optional company logo
	#For the logo and resume fields, you'll need to configure Django to handle file uploads properly. This involves setting MEDIA_URL and MEDIA_ROOT in your settings.py and using request.FILES in your views when handling forms with file uploads.
	def __str__(self):
		return self.user.username
class FreelancerProfile(models.Model):
	user = models.OneToOneField(Account, on_delete=models.CASCADE)
	skills = models.CharField(max_length=255, blank=True)
	first_name = models.CharField(max_length=50, blank=True)
	last_name = models.CharField(max_length=50, blank=True)

	age = models.PositiveIntegerField(
		null=True,
		blank=True,
		validators=[
			MinValueValidator(18, message="You must be at least 18 years old."),
			MaxValueValidator(100, message="Age cannot exceed 100 years.")
		]
	)
	experience = models.PositiveIntegerField(
		null=True,
		blank=True,
		validators=[
			MinValueValidator(0, message="Experience cannot be negative."),
			MaxValueValidator(82, message="Experience cannot exceed 82 years.")
		]
	)
	bio = models.TextField(blank=True)
	portfolio_url = models.URLField(blank=True)
	skills = models.CharField(max_length=255, blank=True)
	hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)  # Optional hourly rate
	location = models.CharField(max_length=100, blank=True)  # City, State or Region
	education = models.CharField(max_length=255, blank=True)  # e.g., "Bachelor's in Computer Science"
	resume = models.FileField(upload_to='resumes/', blank=True, null=True)  # Optional resume upload

	def __str__(self):
		return self.user.username


class Job(models.Model):
	employer_profile = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='jobs')
	title = models.CharField(max_length=255)
	location = models.CharField(max_length=255)
	salary = models.CharField(max_length=100, blank=True)  # Or DecimalField, etc.
	vacancies = models.IntegerField(default=1)
	applicants = models.ManyToManyField(FreelancerProfile, related_name='applied_jobs', blank=True)

	is_active = models.BooleanField(default=True)
	date_posted = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title
	
class JobApplication(models.Model):
	STATUS_CHOICES = (
		('pending', 'Pending'),
		('accepted', 'Accepted'),
		('rejected', 'Rejected'),
	)
	freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE)
	job = models.ForeignKey(Job, on_delete=models.CASCADE)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
	applied_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('freelancer', 'job')  # Ensure unique applications
from django.shortcuts import render
#from projects.models import Project
from .models import EmployerProfile, FreelancerProfile, Job, JobApplication, Account
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from app_uff.forms import RegistrationForm, AccountAuthenticationForm, JobForm, FreelancerProfileForm, EmployerProfileForm
from django.db import IntegrityError  # Import IntegrityError
from django.contrib import messages  # Import messages
from django.contrib.auth.decorators import login_required
# Create your views here.


def home(request):
	context = {}
	projects = Job.objects.all()
	context["projects"] = projects
	if request.user.is_authenticated:	
		if request.user.is_employer:
			employer_profile = EmployerProfile.objects.get(user=request.user)
			jobs = Job.objects.filter(employer_profile=employer_profile)
			context['jobs'] = jobs
			return render(request, 'app_uff/employer_home.html', context)
		elif request.user.is_freelancer:
			print(request.user.is_freelancer)
			return render(request, 'app_uff/freelancer_home.html', context)
	
	return render(request, 'app_uff/home.html', context)




def registration_view(request):
	context = {}
	if request.POST:
		form = RegistrationForm(request.POST)
		if form.is_valid():
			new_user = form.save(commit=False)
			if form.cleaned_data['user_type'] == 'employer':
					new_user.is_employer = True

			elif form.cleaned_data['user_type'] == 'freelancer':
					new_user.is_freelancer = True
			new_user.save()
			email = form.cleaned_data.get('email')
			raw_password = form.cleaned_data.get('password1')
			account = authenticate(email=email, password=raw_password)
			if account is not None:

				login(request, account)
				
				if form.cleaned_data['user_type'] == 'employer':
					EmployerProfile.objects.create(user=new_user)


				elif form.cleaned_data['user_type'] == 'freelancer':
					FreelancerProfile.objects.create(user=new_user)

					return redirect('app_uff:freelancer_home')
				

			return redirect('app_uff:home')
		else:
			context['registration_form'] = form
			
			# context = {'registration_form':form}
	else: #GET request
		form = RegistrationForm()
		context['registration_form'] = form
	return render(request, 'app_uff/register.html', context)



def logout_view(request):
	logout(request)
	return redirect('app_uff:home')
	

def login_view(request):
	context = {}
	
	if request.method == "POST":
		form = AccountAuthenticationForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data.get('email')
			password = form.cleaned_data.get('password')
			user = authenticate(email=email, password=password)
			if user:
				if user.is_active:
					login(request, user)
					if user.is_superuser:
						return redirect('app_uff:admin_panel')
					else:
						return redirect('app_uff:home')
				else:
					messages.error(request, "Your account has been suspended. Please contact the administrator.")
			else:
				messages.error(request, "Invalid login credentials.")
		
	else:
		form = AccountAuthenticationForm()

	context['login_form'] = form
	return render(request, 'app_uff/login.html', context)

		

def freelancer_view(request):
	context = {}

	projects = Job.objects.all()
	context["projects"] = projects
	if request.user.is_authenticated:
		if request.user.is_freelancer:
			try:
				freelancer_profile = FreelancerProfile.objects.get(user=request.user)
				JobApplication.objects.filter(freelancer=freelancer_profile)
				# applied_job_ids = freelancer_profile.applied_jobs.values_list('id', flat=True)
				# print('lmao',applied_job_ids)
				# projects.exclude(applied_job_ids)
				#context['applied_job_ids'] = applied_job_ids
			except FreelancerProfile.DoesNotExist:
				pass
				#context['applied_job_ids'] = []
		return render(request, 'app_uff/freelancer_home.html', context)
	
def add_job(request):
	if not request.user.is_employer:
		return redirect('app_uff:home')
	
	employer_profile = EmployerProfile.objects.get(user=request.user)

	if request.method == 'POST':
		form = JobForm(request.POST)
		if form.is_valid():
			job = form.save(commit=False)
			job.employer_profile = employer_profile
			job.save()
			return redirect('app_uff:home')
	else:
		form = JobForm()
		
	context = {'form': form}
	return render(request, 'app_uff/add_job.html', context)

def job_detail(request, job_id):
	job = get_object_or_404(Job, id=job_id)
	applied = False
	is_accepted = False
	employer = job.employer_profile
	accepted_freelancers = []
	if request.user.is_authenticated and request.user.is_freelancer:
		
			freelancer_profile = FreelancerProfile.objects.get(user=request.user)
			applied = job in freelancer_profile.applied_jobs.all()
			
	if request.user.is_employer:
		accepted_applications = JobApplication.objects.filter(job=job, status='accepted')
		accepted_freelancers = [application.freelancer for application in accepted_applications]
		# Get the FreelancerProfiles from the accepted applications
			#accepted_freelancers = [application.freelancer for application in accepted_applications]

		# Or, in a single query (more efficient):
			#accepted_freelancers = FreelancerProfile.objects.filter(jobapplication__job=job, jobapplication__status='accepted')
			
		
	context = {
		'job': job,
		'applied':applied,
		'employer':employer,
		'lmao':accepted_freelancers
	

	}
	return render(request, 'app_uff/job_detail.html', context)



def apply_job(request, job_id):
	job = get_object_or_404(Job, id=job_id)

	if not request.user.is_freelancer:
		return redirect('app_uff:home')
	try:
		freelancer_profile = FreelancerProfile.objects.get(user=request.user)
	except FreelancerProfile.DoesNotExist:
		return redirect('app_view:error_view')
	
	if request.method == "POST":
		try:
			# Create a JobApplication object
			JobApplication.objects.create(freelancer=freelancer_profile, job=job)
			messages.success(request, "Successfully applied to the job!")
		except IntegrityError:
			messages.error(request, "You have already applied for this job.")
		if freelancer_profile not in job.applicants.all():
			job.applicants.add(freelancer_profile)
			job.save()

		return redirect('app_uff:job_detail', job_id=job_id)
	return redirect('app_uff:home')

def manage_application(request, job_id, applicant_id):
	job = get_object_or_404(Job, id=job_id)
	if not request.user.is_employer or job.employer_profile.user != request.user:
		return redirect('app_uff:home')

	applicant = get_object_or_404(FreelancerProfile, id=applicant_id)
	
	if request.method == "POST":
		action = request.POST.get('action')
		job_application = get_object_or_404(JobApplication, job=job, freelancer=applicant)
		
		if action == 'accept':
			job_application.status = 'accepted'
			job_application.save() 
			job.applicants.remove(applicant)
			job.vacancies -= 1
			job.save()
			messages.success(request, f"Application for {applicant.user.username} accepted.")


		elif action == 'reject':
			job_application.status = 'rejected'
			job_application.save()
			job.applicants.remove(applicant)
			messages.success(request, f"Application for {applicant.user.username} rejected.")

		return redirect('app_uff:job_detail', job_id=job_id)
	
	return redirect('app_uff:home')

def job_offers(request):
	# ...
	# Get job applications for the freelancer
	freelancer_profile = FreelancerProfile.objects.get(user=request.user)
	job_applications = JobApplication.objects.filter(freelancer=freelancer_profile)
	print(job_applications)
	applications = []
	for application in job_applications:
		print('lol', application)
		applications.append({'job': application.job, 'status': application.status})

	context = {
		'applications': applications,
	}
	return render(request, 'app_uff/job_offers.html', context)


def freelancer_profile(request, freelancer_id):
	freelancer_profile = get_object_or_404(FreelancerProfile, id=freelancer_id)
	context = {'freelancer_profile': freelancer_profile}
	return render(request, 'app_uff/freelancer_profile.html', context)

def employer_profile(request, employer_id):
	employer_profile = get_object_or_404(EmployerProfile, id=employer_id)
	context = {'employer_profile': employer_profile}
	return render(request, 'app_uff/employer_profile.html', context)

def edit_freelancer_profile(request):

	freelancer_profile = FreelancerProfile.objects.get(user=request.user)


	if request.method == 'POST':
		form = FreelancerProfileForm(request.POST, instance=freelancer_profile)
		if form.is_valid():
			form.save()
			return redirect('app_uff:freelancer_profile', freelancer_id=freelancer_profile.id)
	else:
		form = FreelancerProfileForm(instance=freelancer_profile)

	context = {'form': form}
	return render(request, 'app_uff/edit_freelancer_profile.html', context)

def edit_employer_profile(request):

	employer_profile = EmployerProfile.objects.get(user=request.user)


	if request.method == 'POST':
		form = EmployerProfileForm(request.POST, instance=employer_profile)
		if form.is_valid():
			form.save()
			return redirect('app_uff:employer_profile', employer_id=employer_profile.id)
	else:
		form = EmployerProfileForm(instance=employer_profile)

	context = {'form': form}
	return render(request, 'app_uff/edit_employer_profile.html', context)

def error_view(request):
	return render(request, 'app_uff/error_view.html')


@login_required
def admin_view(request):
	if not request.user.is_superuser:
		return redirect('app_uff:home')  # Or show a "permission denied" error

	employers = EmployerProfile.objects.all()
	freelancers = FreelancerProfile.objects.all()
	job_applications = JobApplication.objects.all()
	jobs = Job.objects.all()
	users = Account.objects.all()

	context = {
		'employers': employers,
		'freelancers': freelancers,
		'job_applications': job_applications,
		'jobs' : jobs,
		'users' : users,
	}
	return render(request, 'app_uff/admin_panel.html', context)

@login_required
def edit_job_admin(request, job_id):
	if not request.user.is_superuser:
		return redirect('app_uff:home')  # Or permission denied

	job = get_object_or_404(Job, id=job_id)

	if request.method == 'POST':
		form = JobForm(request.POST, instance=job)
		if form.is_valid():
			form.save()
			return redirect('app_uff:admin_panel')  # Redirect to admin panel
	else:
		form = JobForm(instance=job)

	context = {'form': form, 'job': job}
	return render(request, 'app_uff/edit_job_admin.html', context)

@login_required
def delete_job_admin(request, job_id):
	if not request.user.is_superuser:
		return redirect('app_uff:home')  # Or permission denied

	job = get_object_or_404(Job, id=job_id)

	if request.method == 'POST':
		job.delete()
		return redirect('app_uff:admin_panel')

	context = {'job': job}
	return render(request, 'app_uff/delete_job_admin.html', context)

@login_required
def suspend_user_admin(request, user_id):
	if not request.user.is_superuser:
		return redirect('app_uff:home')

	user = get_object_or_404(Account, id=user_id)
	user.is_active = False
	user.save()
	return redirect('app_uff:admin_panel')

@login_required
def activate_user_admin(request, user_id):
	if not request.user.is_superuser:
		return redirect('app_uff:home')

	user = get_object_or_404(Account, id=user_id)
	user.is_active = True
	user.save()
	return redirect('app_uff:admin_panel')

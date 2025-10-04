from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from projects.models import Project
from .models import FreelancerProfile, EmployerProfile
from app_uff.models import Account, Job

class RegistrationForm(UserCreationForm):
    
    USER_TYPES = (
        ('employer', 'Employer'),
        ('freelancer', 'Freelancer'),
    )

    email = forms.EmailField(max_length=50, help_text='Required. Add valid email address.')
    user_type = forms.ChoiceField(choices=USER_TYPES)



    class Meta:
        model = Account
        fields = ("email", "username", "password1", "password2")

# class AccountAuthenticationForm(forms.ModelForm):

#     password = forms.CharField(label="password", widget=forms.PasswordInput)

#     class Meta:
#         model = Account
#         fields = ('email', 'password') 

#     def clean(self):
#         email = self.cleaned_data['email']
#         password = self.cleaned_data['password']
#         if not authenticate(email=email, password=password):
#             raise forms.ValidationError("Invalid login")
class AccountAuthenticationForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise forms.ValidationError("Invalid login credentials.", code='invalid_login')

        return cleaned_data

        

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'location', 'salary', 'vacancies']

class FreelancerProfileForm(forms.ModelForm):
    class Meta:
        model = FreelancerProfile
        exclude = ['user']  # Exclude the 'user' field
  # Add other fields you want to be editable

class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        exclude = ['user']  # Exclude the 'user' field

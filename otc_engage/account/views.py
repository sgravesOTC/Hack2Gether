from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, ProfileRegistrationForm

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = ProfileRegistrationForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('account:login')
    else:
        user_form = UserRegistrationForm()
        profile_form = ProfileRegistrationForm()
    return render(
        request,
        'account/register.html',
        {'user_form':user_form, 'profile_form':profile_form, 'section':'account'}
    )

def profile(request):
    return render(request, 'account/profile.html')

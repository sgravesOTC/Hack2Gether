from django.shortcuts import render


def register(request):
    return render(request, 'account/register.html')


def profile(request):
    return render(request, 'account/profile.html')

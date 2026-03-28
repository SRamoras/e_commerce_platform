from django.contrib.auth.models import User
from django.shortcuts import render, redirect


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email    = request.POST.get('email')
        password = request.POST.get('password')
        role     = request.POST.get('role', 'buyer')

        if not all([username, email, password]):
            return render(request, 'users/register.html', {'error': 'All fields are required.'})

        if User.objects.filter(email=email).exists():
            return render(request, 'users/register.html', {'error': 'Email already registered.'})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.profile_set.update(role=role)

        return redirect('login')

    return render(request, 'users/register.html')
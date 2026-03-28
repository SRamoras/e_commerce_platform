from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def profile_view(request):
    profile = request.user.profile_set.first()
    context = {
        'username': request.user.username,
        'email':    request.user.email,
        'role':     profile.role if profile else '-',
    }

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            email = request.POST.get('email', '').strip()
            if email:
                request.user.email = email
                request.user.save()
            context['success'] = 'Profile updated successfully!'

        elif action == 'change_password':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')

            if not request.user.check_password(old_password):
                context['error_password'] = 'Old password is incorrect.'
            else:
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                context['success_password'] = 'Password changed successfully!'

        context['email'] = request.user.email

    return render(request, 'users/profile.html', context)
from users.models import Profile


def user_role(request):
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user=request.user).first()
        return {"user_role": profile.role if profile else None}
    return {"user_role": None}

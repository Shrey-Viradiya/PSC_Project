from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegisterForm, MemberUpdateForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Member


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}! You are now able to log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})



@login_required
def profile(request):
    try:
        profile_ = request.user.member
    except Member.DoesNotExist:
        profile_ = Member(user=request.user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = MemberUpdateForm(request.POST, request.FILES, instance=profile_)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = MemberUpdateForm(instance=request.user.member)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'users/profile.html', context)

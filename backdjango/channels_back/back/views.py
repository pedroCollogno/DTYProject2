from django.shortcuts import render


def user_list(request):
    return render(request, 'back/user_list.html')
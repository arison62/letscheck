from inertia import render as render_inertia
from django.shortcuts import render


def home(request):
    return render_inertia(request, "Home")

def index(request):
    return render(
        request,
        "base.html",
    )

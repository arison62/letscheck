from inertia import render

def home_page(request):
    """Renders the home page using Inertia."""
    return render(request, 'Home', {})

def faq_page(request):
    """Renders the FAQ page using Inertia."""
    return render(request, 'FAQ', {})

def verify_page(request):
    """Renders the document verification page using Inertia."""
    return render(request, 'Verify', {})

def index(request):
    """Renders the index page."""
    return render(request, 'Home', {})

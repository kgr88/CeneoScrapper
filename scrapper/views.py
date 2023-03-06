from django.shortcuts import render

# Create your views here.
def home_page(request):
    return render(request, 'scrapper/index.html')

def ekstrakcja(request):
    return render(request, 'scrapper/ekstrakcja.html')

def lista(request):
    return render(request, 'scrapper/index.html')

def autor(request):
    return render(request, 'scrapper/index.html')
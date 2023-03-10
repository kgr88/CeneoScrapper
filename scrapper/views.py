from django.shortcuts import render
from .forms import SearchForm
from django.http import HttpResponseRedirect
from .models import Opinion, Pros, Cons, Product
from bs4 import BeautifulSoup
import requests


# Create your views here.
def home_page(request):
    return render(request, 'scrapper/index.html')

def ekstrakcja(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid() and int(request.POST['query']) >= 0:
            url = '/produkt/?query=' + request.POST['query']
            return HttpResponseRedirect(url)
        else:
            form = SearchForm()
            return render(request, 'scrapper/ekstrakcja.html', {'form': form, "error": "Błedny kod"})

    else:
        form = SearchForm()

    return render(request, 'scrapper/ekstrakcja.html', {'form': form, "error": ""})

def lista(request):
    return render(request, 'scrapper/index.html')

def autor(request):
    return render(request, 'scrapper/index.html')

def produkt(request):
    id = request.GET.get('query')
    url = f"https://www.ceneo.pl/{id}#tab=reviews"
    ran = False
    while url:
        response = requests.get(url)
        print(url)
        soup = BeautifulSoup(response.text, "html.parser")
        opinions = soup.select("div.js_product-review")

        if not ran:
            title = soup.find('div', {'class': 'product-top__title'})
            product = Product()
            product.id = id
            product.name = title.text.strip()
            product.save()
            ran = True

        for opinion in opinions:
            opinion_object = Opinion()
            opinion_object.extract_values(opinion, id)
            opinion_object.save()
            #print(opinion_object)
        try:
            next_url = soup.find('a', {'class': 'pagination__next'})
            url = "https://www.ceneo.pl" + next_url.get('href')
        except AttributeError:
            url = None
    return render(request, 'scrapper/index.html')
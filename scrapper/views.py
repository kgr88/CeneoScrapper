from django.shortcuts import render
from .forms import SearchForm
from django.http import HttpResponseRedirect
from .models import Opinion, Product
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
    query_id = request.GET.get('query')
    url = f"https://www.ceneo.pl/{query_id}#tab=reviews"
    ran = False
    while url:
        response = requests.get(url)
        print(response)
        soup = BeautifulSoup(response.text, "html.parser")
        print(soup.find('a', {'class': 'pagination__next'}))
        opinions = soup.select("div.js_product-review")

        if not ran:
            title = soup.find('div', {'class': 'product-top__title'})
            product_object = Product()
            product_object.id = query_id
            product_object.name = title.text.strip()
            product_object.save()
            ran = True

        for opinion in opinions:
            opinion_object = Opinion(product=product_object)
            opinion_object.extract_values(opinion)
            opinion_object.save()

        try:
            next_url = soup.find('a', {'class': 'pagination__next'})
           # print(next_url)
            url = "https://www.ceneo.pl" + next_url.get('href')
            #print(url)
        except AttributeError:
            #print(soup.beautify())
            url = None
            #print(url)

    opinie = product_object.opinion_set.all()

    return render(request, 'scrapper/produkt.html', {'opinie': opinie})
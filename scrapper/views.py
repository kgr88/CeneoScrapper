from django.shortcuts import render
from .forms import SearchForm
from django.http import HttpResponseRedirect
from .models import Opinion, Product
from bs4 import BeautifulSoup
import requests
from django.db.models import Avg
from django.http import HttpResponse
from django.core import serializers
import json

# Create your views here.

def download_opinions(request, product_id):
    product = Product.objects.get(id=product_id)
    opinions = Opinion.objects.filter(product=product)
    data = serializers.serialize('json', opinions)
    data = data.replace('"model": "scrapper.opinion",', '')  # deletes field with model name
    formatted_data = json.dumps(json.loads(data), indent=4, ensure_ascii=False)  # reformats data to make it more human readable
    response = HttpResponse(formatted_data, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{product.id}.json"'
    return response

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
    products = Product.objects.all()
    for product in products:
        product.null_pros = Opinion.objects.filter(product=product, pros__exact='').count()
        product.null_cons = Opinion.objects.filter(product=product, cons__exact='').count()
        average = Opinion.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
        if average:
            product.average = format(average, '.2f')
        else:
            product.average = 'brak opinii'
    return render(request, 'scrapper/lista.html', {'products': products})


def autor(request):
    return render(request, 'scrapper/index.html')


def produkt(request):
    query_id = request.GET.get('query')
    url = f"https://www.ceneo.pl/{query_id}#tab=reviews"
    ran = False
    while url:
        response = requests.get(url)
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
            url = "https://www.ceneo.pl" + next_url.get('href')
        except AttributeError:
            url = None

    opinions_count = Opinion.objects.filter(product=product_object).count()
    opinie = product_object.opinion_set.all()
    return render(request, 'scrapper/produkt.html', {'opinie': opinie, 'produkt': produkt, 'opinions_count': opinions_count})
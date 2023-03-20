from django.shortcuts import render, get_object_or_404
from .forms import SearchForm
from django.http import HttpResponseRedirect, HttpResponse
from .models import Opinion, Product
from bs4 import BeautifulSoup
import requests
from django.db.models import Avg
from django.core import serializers
import json
import matplotlib.pyplot as plt
from io import BytesIO
import base64


# Create your views here.
def show_graphs(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    opinions = Opinion.objects.filter(product=product)
    if not opinions:
        return render(request, 'scrapper/wykresy.html')
    # Calculate the count of recommended and not recommended opinions
    recommended_count = opinions.filter(recommended=True).count()
    not_recommended_count = opinions.filter(recommended=False).count()

    # Create the pie chart for recommended vs not recommended
    fig, ax = plt.subplots()
    ax.pie([recommended_count, not_recommended_count], labels=['Polecam', 'Nie Polecam'], autopct='%1.1f%%',
           startangle=90)
    ax.legend(loc='center right', bbox_to_anchor=(1.25, 0.5))  # adds legend with positioning
    ax.axis('equal')
    buffer1 = BytesIO()
    plt.savefig(buffer1, format='png', bbox_inches='tight')
    buffer1.seek(0)
    pie_chart = base64.b64encode(buffer1.getvalue()).decode('utf-8')
    buffer1.close()

    # Create the column chart for rating occurrences count
    ratings = list(opinions.values_list('rating', flat=True))
    unique_ratings = sorted(set(ratings))
    ratings_count = [ratings.count(rating) for rating in unique_ratings]
    fig, ax = plt.subplots()
    ax.bar(unique_ratings, ratings_count, width=0.4)
    ax.set_xlabel('Ocena')
    ax.set_ylabel('Ilość')
    ax.set_xlim([-0.5, 5.5])
    buffer2 = BytesIO()
    plt.savefig(buffer2, format='png')
    buffer2.seek(0)
    column_chart = base64.b64encode(buffer2.getvalue()).decode('utf-8')
    buffer2.close()

    # Pass the chart images to the template
    data = {
        'pie_chart': pie_chart,
        'column_chart': column_chart,
        'product': product,
    }
    return render(request, 'scrapper/wykresy.html', data)


def download_opinions(request, product_id):
    product = Product.objects.get(id=product_id)
    opinions = Opinion.objects.filter(product=product)
    data = serializers.serialize('json', opinions)
    data = data.replace('"model": "scrapper.opinion",', '')  # deletes field with model name
    # reformats data to make it more human readable
    formatted_data = json.dumps(json.loads(data), indent=4, ensure_ascii=False)
    response = HttpResponse(formatted_data, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{product.id}.json"'
    return response


def home_page(request):
    return render(request, 'scrapper/index.html')


def ekstrakcja(request):
    if request.method == "GET":
        form = SearchForm()
        return render(request, 'scrapper/ekstrakcja.html', {'form': form, "error": ""})
    form = SearchForm(request.POST)
    if not form.is_valid() or int(request.POST['query']) <= 0:
        form = SearchForm()
        return render(request, 'scrapper/ekstrakcja.html', {'form': form, "error": "Wprowadziłeś błędne dane"})
    query_id = request.POST['query']
    url = f"https://www.ceneo.pl/{query_id}#tab=reviews"
    ran = False
    while url:
        response = requests.get(url)
        if response.status_code == 404:
            form = SearchForm()
            return render(request, 'scrapper/ekstrakcja.html', {'form': form, "error": "Produkt o podanym ID nie istnieje"})
        soup = BeautifulSoup(response.text, "html.parser")
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
    url = '/produkt/' + request.POST['query']
    return HttpResponseRedirect(url)


def lista(request):
    products = Product.objects.all()
    for product in products:
        product.opinions_count = Opinion.objects.filter(product=product).count()
        product.pros_count = Opinion.objects.filter(product=product).count() - Opinion.objects.filter(product=product, pros__exact='').count()
        product.cons_count = Opinion.objects.filter(product=product).count() - Opinion.objects.filter(product=product, cons__exact='').count()
        average = Opinion.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
        if average:
            product.average = format(average, '.2f')
        else:
            product.average = 'brak opinii'
    return render(request, 'scrapper/lista.html', {'products': products})


def autor(request):
    return render(request, 'scrapper/autor.html')


def produkt(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    opinie = product.opinion_set.all()
    return render(request, 'scrapper/produkt.html', {'opinie': opinie, 'product': product})

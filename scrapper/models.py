from django.db import models
from bs4 import BeautifulSoup
import requests


# Create your models here.
class Product(models.Model):
    id = models.PositiveIntegerField
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"

class Opinion(models.Model):
    id = models.PositiveIntegerField
    product_id = models.PositiveIntegerField
    author = models.CharField(max_length=128)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    recommended = models.BooleanField
    purchase_confirmation = models.BooleanField
    opinion_date = models.DateField
    purchase_date = models.DateField
    likes = models.PositiveIntegerField
    dislikes = models.PositiveIntegerField
    description = models.TextField

    def extract_values(self, data, product_id):
        self.id = int(data["data-entry-id"])
        self.product_id = product_id
        self.author = data.find('span', {'class': 'user-post__author-name'}).text.strip()
        try:
            recomendation = data.find('span', {'class': 'user-post__author-recomendation'}).text.strip()
            print(recomendation)
            if recomendation == "Polecam":
                self.recommended = True
            else:
                self.recommended = False
        except AttributeError:
            self.recommended = None
        self.rating = float(data.find('span', {'class': 'user-post__score-count'}).text[:-2].replace(",", "."))

    def __str__(self):
        if self.recommended:
            return f"{self.id} true"
        if not self.recommended:
            return "false"
        return "none"

    def __repr__(self):
        return f"{self.id}<br>{self.author}<br>{self.recommended}<br>{self.rating}"


class Pros(models.Model):
    id = models.PositiveIntegerField
    pro = models.CharField(max_length=255)


class Cons(models.Model):
    id = models.PositiveIntegerField
    con = models.CharField(max_length=255)

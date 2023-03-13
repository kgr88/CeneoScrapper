from django.db import models
from bs4 import BeautifulSoup
import requests
from datetime import datetime


# Create your models here.
class Product(models.Model):
    id = models.PositiveIntegerField
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"

class Opinion(models.Model):
    id = models.PositiveIntegerField
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    author = models.CharField(max_length=128)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    recommended = models.BooleanField(null=True)
    purchase_confirmation = models.BooleanField(default=False)
    opinion_date = models.DateTimeField(null=True)
    purchase_date = models.DateTimeField(null=True)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    description = models.TextField(default="brak")

    def extract_values(self, data):
        self.id = int(data["data-entry-id"])
        self.author = data.find('span', {'class': 'user-post__author-name'}).text.strip()
        try:
            recomendation = data.find('span', {'class': 'user-post__author-recomendation'}).text.strip()
            #print(recomendation)
            if recomendation == "Polecam":
                self.recommended = True
                #print(self.recommended)
            else:
                self.recommended = False
                #print(self.recommended)
        except AttributeError:
            self.recommended = None
            #print(self.recommended)
        self.rating = float(data.find('span', {'class': 'user-post__score-count'}).text[:-2].replace(",", "."))
        try:
            data.find('div', {'class': 'review-pz'})
            self.purchase_confirmation = True
        except AttributeError:
            pass
        dates = data.findAll('time')
        opinion_date_unformatted = dates[0]['datetime']
        self.opinion_date = datetime.strptime(opinion_date_unformatted, "%Y-%m-%d %H:%M:%S")

        try:
            self.purchase_date = dates[1]['datetime']
        except IndexError:
            pass

        self.likes = int(data.find('button', {'class': 'vote-yes'})['data-total-vote'])
        print(type(self.likes))
        self.dislikes = int(data.find('button', {'class': 'vote-no'})['data-total-vote'])
        self.description = data.find('div', {'class': 'user-post__text'}).text.strip()
        #print(self)

    #def __str__(self):
        #return f"{self.id} {str(self.recommended)} {self.purchase_date} {str(self.opinion_date)} {self.likes} {self.dislikes} {self.description}"
        #return self.opinion_date



class Pros(models.Model):
    id = models.PositiveIntegerField
    pro = models.CharField(max_length=255)


class Cons(models.Model):
    id = models.PositiveIntegerField
    con = models.CharField(max_length=255)

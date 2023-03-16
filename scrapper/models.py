from django.db import models


# Create your models here.
class Product(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Opinion(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    author = models.CharField(max_length=128)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    recommended = models.BooleanField(null=True)
    purchase_confirmation = models.BooleanField(default=False)
    opinion_date = models.DateTimeField(null=True)
    purchase_date = models.DateTimeField(null=True)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    description = models.TextField(null=True)
    pros = models.TextField(null=True)
    cons = models.TextField(null=True)

    def extract_values(self, data):
        self.id = int(data["data-entry-id"])
        self.author = data.find('span', {'class': 'user-post__author-name'}).text.strip()
        try:
            recomendation = data.find('span', {'class': 'user-post__author-recomendation'}).text.strip()
            if recomendation == "Polecam":
                self.recommended = True
            else:
                self.recommended = False
        except AttributeError:
            self.recommended = None
        self.rating = float(data.find('span', {'class': 'user-post__score-count'}).text[:-2].replace(",", "."))
        try:
            data.find('div', {'class': 'review-pz'})
            self.purchase_confirmation = True
        except AttributeError:
            pass
        dates = data.findAll('time')
        self.opinion_date = dates[0]['datetime']
        try:  # for opinions that don't have purchase date
            self.purchase_date = dates[1]['datetime']
        except IndexError:
            pass

        self.likes = int(data.find('button', {'class': 'vote-yes'})['data-total-vote'])
        self.dislikes = int(data.find('button', {'class': 'vote-no'})['data-total-vote'])
        self.description = data.find('div', {'class': 'user-post__text'}).text.strip()
        for feature_type in ['positives', 'negatives']:
            features = data.select(f"div.review-feature__col:has(> div[class$=\'{feature_type}\']) > div.review-feature__item")
            features_list = []
            try:
                for feature in features:
                    features_list.append(feature.text.strip())
            except AttributeError:
                pass
            features_list.sort()
            features_str = ', '.join(features_list)
            if feature_type == 'positives':
                self.pros = features_str
            else:
                self.cons = features_str
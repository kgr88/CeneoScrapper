from django.contrib import admin
from .models import Opinion, Pros, Cons, Product
# Register your models here.
admin.site.register(Opinion)
admin.site.register(Pros)
admin.site.register(Cons)
admin.site.register(Product)
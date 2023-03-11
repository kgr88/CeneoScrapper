from django.contrib import admin
from .models import Opinion, Pros, Cons, Product
# Register your models here.
@admin.register(Opinion)
class OpinionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Opinion._meta.fields]


#admin.site.register(Opinion)
admin.site.register(Pros)
admin.site.register(Cons)
admin.site.register(Product)
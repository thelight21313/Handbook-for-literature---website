from django.contrib import admin

from Litra.models import Writers, Works, Facts

# Register your models here.
admin.site.register(Writers)
admin.site.register(Works)
admin.site.register(Facts)
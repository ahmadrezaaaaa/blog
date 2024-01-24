from django.contrib import admin
from django.apps import apps

for key, model in apps.get_app_config("blog").models.items():
    admin.site.register(model)

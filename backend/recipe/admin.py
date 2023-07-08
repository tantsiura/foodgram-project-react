import csv

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse

from recipe.models import Favorite, Ingredient, IngredientUnits, Recipe, Tag

from .forms import (IngredientImportForm, IngredientUnitsImportForm,
                    RecipeImportForm, TagImportForm)
from .models import (IngredientImport, IngredientUnitsImport, RecipeImport,
                     TagImport)


@admin.site.register(Favorite)
@admin.register(TagImport)
class TagImportAdmin(admin.ModelAdmin):
    list_display = ('csv_file', 'date_added')


admin.site.register(Tag)


class TagAdmin(admin.ModelAdmin):
    '''Model for adding data by tag.'''
    list_display = (
        'name',
        'slug',
        'color'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-empty-'

    def get_urls(self):
        urls = super().get_urls()
        urls.insert(-1, path('csv-upload/', self.upload_csv))
        return urls

    def upload_csv(self, request):
        if request.method == 'POST':
            form = TagImportForm(request.POST, request.FILES)
            if form.is_valid():
                form_object = form.save()
                with form_object.csv_file.open('r') as csv_file:
                    rows = csv.reader(csv_file, delimiter=',')
                    if next(rows) != ['id', 'name', 'slug', 'color']:
                        messages.warning(request, 'Invalid file headers')
                        return HttpResponseRedirect(request.path_info)
                    for row in rows:
                        print(row[2])
                        Tag.objects.update_or_create(
                            id=row[0],
                            name=row[1],
                            slug=row[2]
                        )
                url = reverse('admin:index')
                messages.success(request, 'File imported successfully')
                return HttpResponseRedirect(url)
        form = TagImportForm()
        return render(request, 'admin/csv_import_page.html', {'form': form})


@admin.register(RecipeImport)
class RecipeImportAdmin(admin.ModelAdmin):
    list_display = ('csv_file', 'date_added')


admin.site.register(Recipe)


class RecipeAdmin(admin.ModelAdmin):
    '''Model for adding data by recipe.'''
    list_display = (
        'name',
        'text',
        'ingredients',
        'tags',
        'cooking_time',
        'author',
        'pub_date'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-empty-'

    def get_urls(self):
        urls = super().get_urls()
        urls.insert(-1, path('csv-upload/', self.upload_csv))
        return urls

    def upload_csv(self, request):
        if request.method == 'POST':
            form = RecipeImportForm(request.POST, request.FILES)
            if form.is_valid():
                form_object = form.save()
                with form_object.csv_file.open('r') as csv_file:
                    rows = csv.reader(csv_file, delimiter=',')
                    if next(rows) != [
                        'id', 'name', 'text',
                        'ingredients', 'tags',
                        'cooking_time', 'author', 'pub_date'
                    ]:
                        messages.warning(request, 'Invalid file headers')
                        return HttpResponseRedirect(request.path_info)
                    for row in rows:
                        print(row[2])
                        Tag.objects.update_or_create(
                            id=row[0],
                            name=row[1],
                            slug=row[2]
                        )
                url = reverse('admin:index')
                messages.success(request, 'File imported successfully')
                return HttpResponseRedirect(url)
        form = RecipeImportForm()
        return render(request, 'admin/csv_import_page.html', {'form': form})


@admin.register(IngredientImport)
class IngredientImportAdmin(admin.ModelAdmin):
    list_display = ('csv_file', 'date_added')


admin.site.register(Ingredient)


class IngredientAdmin(admin.ModelAdmin):
    '''Model for adding data by ingredients.'''
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-empty-'

    def get_urls(self):
        urls = super().get_urls()
        urls.insert(-1, path('csv-upload/', self.upload_csv))
        return urls

    def upload_csv(self, request):
        if request.method == 'POST':
            form = IngredientImportForm(request.POST, request.FILES)
            if form.is_valid():
                form_object = form.save()
                with form_object.csv_file.open('r') as csv_file:
                    rows = csv.reader(csv_file, delimiter=',')
                    if next(rows) != ['id', 'name', 'measurement_unit']:
                        messages.warning(request, 'Invalid file headers')
                        return HttpResponseRedirect(request.path_info)
                    for row in rows:
                        print(row[2])
                        Tag.objects.update_or_create(
                            id=row[0],
                            name=row[1],
                            slug=row[2]
                        )
                url = reverse('admin:index')
                messages.success(request, 'File imported successfully')
                return HttpResponseRedirect(url)
        form = IngredientImportForm()
        return render(request, 'admin/csv_import_page.html', {'form': form})


@admin.register(IngredientUnitsImport)
class IngredientUnitsImportAdmin(admin.ModelAdmin):
    list_display = ('csv_file', 'date_added')


admin.site.register(IngredientUnits)


class IngredientUnitsAdmin(admin.ModelAdmin):
    '''Model for adding data by ingredients units.'''
    list_display = (
        'recipe',
        'ingredient',
        'amount'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-empty-'

    def get_urls(self):
        urls = super().get_urls()
        urls.insert(-1, path('csv-upload/', self.upload_csv))
        return urls

    def upload_csv(self, request):
        if request.method == 'POST':
            form = IngredientUnitsImportForm(request.POST, request.FILES)
            if form.is_valid():
                form_object = form.save()
                with form_object.csv_file.open('r') as csv_file:
                    rows = csv.reader(csv_file, delimiter=',')
                    if next(rows) != ['id', 'recipe', 'ingredient', 'amount']:
                        messages.warning(request, 'Invalid file headers')
                        return HttpResponseRedirect(request.path_info)
                    for row in rows:
                        print(row[2])
                        Tag.objects.update_or_create(
                            id=row[0],
                            name=row[1],
                            slug=row[2]
                        )
                url = reverse('admin:index')
                messages.success(request, 'File imported successfully')
                return HttpResponseRedirect(url)
        form = IngredientUnitsImportForm()
        return render(request, 'admin/csv_import_page.html', {'form': form})

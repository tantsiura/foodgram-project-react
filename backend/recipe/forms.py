import models
from django.forms import ModelForm


class TagImportForm(ModelForm):
    class Meta:
        model = models.TagImport
        fields = ('csv_file',)


class RecipeImportForm(ModelForm):
    class Meta:
        model = models.RecipeImport
        fields = ('csv_file',)


class IngredientImportForm(ModelForm):
    class Meta:
        model = models.IngredientImport
        fields = ('csv_file',)


class IngredientUnitsImportForm(ModelForm):
    class Meta:
        model = models.IngredientUnitsImport
        fields = ('csv_file',)

# python backend/manage.py import_csv
# --paths static/data/ingredients.csv --tables recipe_ingredient

import csv
import os

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from foodgram.settings import BASE_DIR


def read_model(model_name, path):
    '''The function checks the type of the model.'''
    model_type = ContentType.objects.filter(model=model_name.lower()).first()
    if not model_type:
        return

    model = model_type.model_class()
    items = []
    path = os.path.join(BASE_DIR, path)
    with open(path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            items.append(model(**row))

        if items:
            model.objects.bulk_create(items)


def read_table(table, path, cursor):
    '''The function adds data to the database.'''
    path = os.path.join(BASE_DIR, path)
    with open(path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        header = reader.fieldnames
        fields = ', '.join(header)
        values = ', '.join(['%s' for _ in header])
        for row in reader:
            cursor.execute(
                f'INSERT INTO {table}({fields}) VALUES({values})',
                [row[item] for item in header]
            )


class Command(BaseCommand):
    '''Command to load data into database.'''
    help = 'Data import'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--paths',
            dest='paths',
            nargs='+',
            help='List of file paths',
            type=str,
        )
        parser.add_argument(
            '--models',
            dest='models',
            nargs='+',
            help='List of model names',
            type=str,
        )
        parser.add_argument(
            '--tables',
            dest='tables',
            nargs='+',
            help='List of names nf,kbw',
            type=str,
        )

    def handle(self, *args, **options):
        paths = options.get('paths')
        models = options.get('models')
        tables = options.get('tables')

        if not models and not tables or models and tables:
            raise CommandError(
                'Incorrect specification of parameters'
            )

        if models and paths:
            if len(models) != len(paths):
                raise CommandError('Number of paths and models do not match')

            for model_name, path in zip(models, paths):
                read_model(model_name, path)

        elif tables and paths:
            if len(tables) != len(paths):
                raise CommandError('Number of paths and tables do not match')

            cursor = connection.cursor()
            for table, path in zip(tables, paths):
                read_table(table, path, cursor)

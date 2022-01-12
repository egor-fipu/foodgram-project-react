import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Creates entries with ingredients'

    def handle(self, *args, **options):
        count = 0
        with open('data/ingredients.json', 'r', encoding='UTF-8') as ingr:
            for ingredient in json.load(ingr):
                try:
                    ing, crt = Ingredient.objects.get_or_create(
                        name=ingredient.get('name'),
                        measurement_unit=ingredient.get('measurement_unit')
                    )
                except Exception as ex:
                    print(f'Error add ingredient: {ex}')
                print(f'Created {ing}' if crt is True else f'Skipped {ing}')
                count += 1
        print(f'Processed {count} elements!')

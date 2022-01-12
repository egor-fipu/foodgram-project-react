import json

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Creates entries with tags'

    def handle(self, *args, **options):
        count = 0
        with open('data/tag.json', 'r', encoding='UTF-8') as tags:
            for tag in json.load(tags):
                try:
                    tg, crt = Tag.objects.get_or_create(
                        name=tag.get('name'),
                        color=tag.get('color'),
                        slug=tag.get('slug')
                    )
                    print(f'Created {tg}' if crt is True else f'Skipped {tg}')
                except Exception as ex:
                    print(print(f'Error add tag: {ex}'))
                count += 1
        print(f'Processed {count} elements!')

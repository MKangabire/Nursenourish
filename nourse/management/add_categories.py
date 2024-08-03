from django.core.management.base import BaseCommand
from nourse.models import Category

class Command(BaseCommand):
    help = 'Add default categories to the database'

    def handle(self, *args, **kwargs):
        categories = ['Mental Health', 'Wellness']
        for category in categories:
            Category.objects.get_or_create(name=category)
        self.stdout.write(self.style.SUCCESS('Categories added successfully.'))

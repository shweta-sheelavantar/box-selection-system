"""
Management command: seed_data

Populates the database with the 3 canonical boxes and 4 sample products
used in the assignment. Safe to run multiple times — uses get_or_create
so it never duplicates rows.

Usage:
    python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from packaging.models import Box, Product


BOXES = [
    # (name, length, width, height, max_weight, cost)
    ('Small',  35, 25, 10, 5,  20),
    ('Medium', 40, 30, 15, 10, 30),
    ('Large',  50, 40, 30, 20, 50),
]

PRODUCTS = [
    # (name, length, width, height, weight)
    ('Phone Case', 16,  8,   1,   0.1),
    ('Book',       22,  15,  3,   0.5),
    ('Shoes',      32,  20,  12,  1.2),
    ('Laptop',     30,  20,  5,   2.0),
]


class Command(BaseCommand):
    help = 'Seed the database with sample boxes and products.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding boxes...')
        for name, length, width, height, max_weight, cost in BOXES:
            obj, created = Box.objects.get_or_create(
                name=name,
                defaults={
                    'length': length,
                    'width': width,
                    'height': height,
                    'max_weight': max_weight,
                    'cost': cost,
                },
            )
            status = 'created' if created else 'already exists'
            self.stdout.write(f'  Box "{name}" — {status}')

        self.stdout.write('Seeding products...')
        for name, length, width, height, weight in PRODUCTS:
            obj, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'length': length,
                    'width': width,
                    'height': height,
                    'weight': weight,
                },
            )
            status = 'created' if created else 'already exists'
            self.stdout.write(f'  Product "{name}" — {status}')

        self.stdout.write(self.style.SUCCESS('Done. Database seeded successfully.'))

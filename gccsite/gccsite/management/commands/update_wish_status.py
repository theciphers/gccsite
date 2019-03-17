from django.core.management.base import BaseCommand

import gcc.models as models


class Command(BaseCommand):

    def handle(self, *args, **options):
        for wish in models.EventWish.objects.all():
            wish.status = wish.default_status_for_migration()
            wish.save()

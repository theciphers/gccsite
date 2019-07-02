from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone, dateparse
import datetime

from gcc.models import Edition, Form


class Command(BaseCommand):
    help = "Manage Prologin editions."

    def add_arguments(self, parser):
        """
        :type parser: argparse.ArgumentParser
        """
        sp = parser.add_subparsers(dest="cmd")
        sp.add_parser(name="create", help="create a new Prologin edition")

    def _ask_for(self, question, default=None, validate=None, coerce=None):
        while True:
            answer = input(
                "{}{}: ".format(
                    question,
                    "" if default is None else " [{}]".format(default),
                )
            )
            if not answer and default is not None:
                answer = default
            if validate is None or validate(answer):
                return answer if coerce is None else coerce(answer)
            self.stdout.write("enter a valid choice!")

    def handle(self, *args, **options):
        cmd = options['cmd']
        if cmd == 'create':

            def date_with_year(year):
                def coerce(value):
                    value = "{}-{}".format(year, value.split("-", 1)[1])
                    self.stdout.write(value)
                    return dateparse.parse_date(value)

                return coerce

            now = timezone.now()
            year = now.year

            year = self._ask_for("Edition year", default=year, coerce=int)
            try:
                edition = Edition.objects.get(year=year)
                self.stdout.write("Edition {} already exists:".format(year))
                self._print_begin_end(edition)
                self.stdout.write("You can update it in the admin if needed.")

            except Edition.DoesNotExist:
                form = None
                try:
                    form = Form.objects.get(name="empty")
                except:
                    form = Form(name="empty")
                    form.save()

                edition = Edition(year=year)
                edition.signup_form = form
                edition.save()
                self.stdout.write(
                    "Edition {} created with an empty form.".format(year)
                )

            return


# raise CommandError("Unknown edition sub-command")

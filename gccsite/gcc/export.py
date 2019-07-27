import csv

from django.http import HttpResponse


class ExportCsvMixin:
    """
    Snippet from https://books.agiliq.com/projects/django-admin-cookbook/en/latest/export.html

    Exports data into CSV, useful for giving data back to users and exploiting big
    amount of datas in dedicated softs

    The model must implement get_export_data methods
    """

    def export_as_csv(self, request, queryset):

        mod = self.model
        meta = mod._meta
        fieldnames = []

        all_keys = set()

        datas = []

        # check all the cols names and perform SQL queries
        for obj in queryset:
            data = obj.get_export_data()
            datas.append(data)

            for key in data:
                if key not in all_keys:
                    fieldnames.append(key)
                    all_keys.add(key)

        # create the response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(
            meta
        )
        writer = csv.DictWriter(response, fieldnames=fieldnames)
        writer.writeheader()

        for data in datas:
            row = writer.writerow(data)

        return response

    export_as_csv.short_description = "Export selected as csv"


def export_queryset_as_csv(queryset, filename):
    fieldnames = []

    all_keys = set()

    datas = []

    # check all the cols names and perform SQL queries
    for obj in queryset:
        data = obj.get_export_data()
        datas.append(data)
        for key in data:
            if key not in all_keys:
                fieldnames.append(key)
                all_keys.add(key)

    # create the response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=' + filename + '.csv'
    )
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()

    for data in datas:
        row = writer.writerow(data)

    return response

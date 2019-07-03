import csv

from django.http import HttpResponse


def export_queryset_as_csv(queryset, mod):
    if len(queryset) == 0:
        return

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

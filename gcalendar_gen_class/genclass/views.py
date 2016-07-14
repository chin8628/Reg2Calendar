from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .reg2cal_func import UploadText, convert2calendar, get_time, create_ical_download

import csv

def index(request):
    if request.method == 'POST':
        form = UploadText(request.POST)
        if form.is_valid():
            data = convert2calendar(form.cleaned_data['regHtml'])

            if data == 0 :
                error = '<div class="alert alert-danger" role="alert"><b>Error :</b> Wrong html source code!</div>'
                return render(request, 'genclass/index.html', {'form': form, 'error': error})

            open_day = form.cleaned_data['open_date_semester']
            end_day = form.cleaned_data['end_date_semester']

            content = create_ical_download(open_day, end_day, data)

            response = HttpResponse(content_type='text/ics')
            response['Content-Disposition'] = 'attachment; filename="export.ics"'
            response.write(content)
            return response

    else:
        form = UploadText()
    return render(request, 'genclass/index.html', {'form': form})
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .reg2cal_func import UploadText, convert2calendar, get_time, create_ical_download

import csv
import base64

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
            content = str(base64.b64encode(bytes(content, 'utf-8')))[2:-1]
            download_data = '<a id="ical_link" href="data:text/calendar;charset=utf-8;base64,' + content + '" download="export.ics" style="display: hidden">A</a>'
            download_script = "$(document).ready(function(){ $('#ical_link')[0].click(); $('#ical_link').remove(); window.location.href = '/success'; });"

            return render(request, 'genclass/index.html', {'form': form, 'download_script': download_script, 'download_data': download_data})
    else:
        form = UploadText()
    return render(request, 'genclass/index.html', {'form': form})

def success(request):
    return render(request, 'genclass/success.html')

def help(request):
    return render(request, 'genclass/help.html')
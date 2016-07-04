from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .forms import UploadFile, handle_uploaded_file

def index(request):
    if request.method == 'POST':
        form = UploadFile(request.POST, request.FILES)
        if form.is_valid():
            html = handle_uploaded_file(request.FILES['file'])
            return HttpResponse(html)
    else:
        form = UploadFile()
    return render(request, 'genclass/index.html', {'form': form})
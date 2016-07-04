from django import forms
from bs4 import BeautifulSoup

class UploadFile(forms.Form):
    file = forms.FileField()

def convert(content):
    #print content
    result = ''
    for char in content:
        asciichar = char.encode('ascii',errors="backslashreplace")[2:]
        if asciichar =='':
            utf8char = char.encode('utf8')
        else:
            try:
                hexchar =  asciichar.decode('hex')
            except:
                #print asciichar
                utf8char = ' '
            try:
                utf8char = hexchar.encode('utf-8')
            except:
                #print hexchar
                utf8char = ' '
            #print utf8char

        result = result + utf8char
        #print result
    return result

def handle_uploaded_file(f):
    html = ""
    exclude = [
                "b'",
                "\\n",
                "\\n\\n",
                "\\n\\n\\n",
                "\\n\\t\\n",
                "\\n\\t\\t\\t",
                "\\n\\t\\t\\t\\n",
                "\\nfunction Go2Edit(Command)\\n{ \\n\\tdocument.edit.command.value = Command;\\n}\\n"
            ]
    for chunk in f.chunks():
        html = html + str(chunk)
    soup = BeautifulSoup(html, from_encoding="tis-620")
    html = ""
    for i in soup.stripped_strings:
        if i not in exclude:
            html = html + i
    return html

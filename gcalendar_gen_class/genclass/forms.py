from django.http import HttpResponse
from django import forms

import html5.forms.widgets as html5_widgets
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

class UploadText(forms.Form):
    open_date_semester = forms.CharField(widget=html5_widgets.DateInput(), label="Opening day")
    end_date_semester = forms.CharField(widget=html5_widgets.DateInput(), label="Ending day")
    regHtml = forms.CharField(widget=forms.Textarea(attrs={'style': 'width:100%'}), label="Reg.kmitl source code")

def convert2calendar(text):
    soup = BeautifulSoup(text, "html.parser")

    # Todo: check None type in case Non-html input before

    subTD = soup.find('table' ,attrs={'align':'center'}).find_all('td')
    pure_text = list()
    for i in subTD:
        if i.text != "":
            pure_text.append(str(i.text))
    return pure_text

def get_time(date_input):
    date_input = date_input.split(" ")
    time = date_input[1].split("-")

    start_time = datetime.strptime(time[0], "%H:%M")
    start_time = start_time.strftime("T%H%M%S")

    end_time = datetime.strptime(time[1], "%H:%M")
    end_time = end_time.strftime("T%H%M%S")

    return {'start': start_time, 'end': end_time}

def get_DOW(date_str):
    dow = date_str.split(" ")[0][:-1]
    th2en = {
            "จ": "Mon",
            "อ": "Tue",
            "พ": "Wed",
            "พฤ": "Thu",
            "ศ": "Fri",
            "ส": "Sat",
            "อา": "Sun",
        }
    return th2en[dow]

def create_csv_download(open_day, end_day, data):

    open_day = datetime.strptime(open_day, "%Y-%m-%d")
    end_day = datetime.strptime(end_day, "%Y-%m-%d")

    description_list = {
                    'code': 'รหัสวิชา',
                    'subject': 'ชื่อวิชา',
                    'unit': 'หน่วยกิต',
                    'group': 'กลุ่ม',
                    'datetime': 'วัน-เวลาเรียน',
                    'class': 'ห้องเรียน',
                    'building': 'ตึก'
                }

    field_name = ['Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'All Day Event', 'Description', 'Location', 'Private']
    subject = list()
    cnt = 13
    while (cnt < len(data) - 13):
        time = get_time(data[cnt + 5])
        day_of_week = get_DOW(data[cnt + 5])
        subject.append({
                        'content': {
                            'Subject': data[cnt + 2],
                            'Start Date': '',
                            'Start Time': time['start'],
                            'End Date': '',
                            'End Time': time['end'],
                            'All Day Event': 'False',
                            'Description': '',
                            'Location': "King Mongkut's Institute of Technology Ladkrabang, 1 Chalong Krung, Thanon Chalong Krung, Lat Krabang, Bangkok 10520",
                            'Private': 'True'
                        },
                        'Day of Week': day_of_week
                    })
        cnt += 8

    table = list()
    table.append({
                    'Subject': 'Subject',
                    'Start Date': 'Start Date',
                    'Start Time': 'Start Time',
                    'End Date': 'End Date',
                    'End Time': 'End Time',
                    'All Day Event': 'All Day Event',
                    'Description': 'Description',
                    'Location': 'Location',
                    'Private': 'Private'
                })
    del_days = end_day - open_day
    for day in range(del_days.days + 1):
        for s in subject:
            if (open_day + timedelta(day)).strftime("%a") == s['Day of Week']:
                s['content']['Start Date'] = (open_day + timedelta(day)).strftime("%Y%m%d")
                s['content']['End Date'] = (open_day + timedelta(day)).strftime("%Y%m%d")
                table.append(s['content'].copy())
    return {'content':table, 'field_name': field_name}

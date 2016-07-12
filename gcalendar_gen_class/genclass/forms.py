from django.http import HttpResponse
from django import forms

from icalendar import Calendar, Event
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import html5.forms.widgets as html5_widgets

class UploadText(forms.Form):
    open_date_semester = forms.CharField(widget=html5_widgets.DateInput(), label="Opening semester day")
    end_date_semester = forms.CharField(widget=html5_widgets.DateInput(), label="Ending semester day")
    regHtml = forms.CharField(widget=forms.Textarea(attrs={'style': 'width:100%'}), label="report_studytable_show.php's source code")

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
            "จ": "MO",
            "อ": "TU",
            "พ": "WE",
            "พฤ": "TH",
            "ศ": "FR",
            "ส": "SA",
            "อา": "SU",
        }
    return th2en[dow]

def display(text):
    return text.decode("utf-8").replace('\r\n', '\n').replace("\;", ";").replace('("', '').replace('("', '').replace('\,', ',').replace('",)', '').strip()

def create_csv_download(open_day, end_day, data):

    open_day = datetime.strptime(open_day, "%Y-%m-%d").strftime("%Y%m%d")
    end_day = (datetime.strptime(end_day, "%Y-%m-%d") + timedelta(1)).strftime("%Y%m%d")

    description_list = {
                    'code': 'รหัสวิชา',
                    'subject': 'ชื่อวิชา',
                    'unit': 'หน่วยกิต',
                    'group': 'กลุ่ม',
                    'datetime': 'วัน-เวลาเรียน',
                    'class': 'ห้องเรียน',
                    'building': 'ตึก'
                }

    cal = Calendar()
    cal.add('PRODID', '-//Google Inc//Google Calendar 70.9054//EN')
    cal.add('VERSION', '2.0')
    cal.add('TZID', 'Asia/Bangkok')
    cal.add('X-LIC-LOCATION', 'Asia/Bangkok')
    cal.add('TZOFFSETFROM', timedelta(hours=7))
    cal.add('TZOFFSETTO', timedelta(hours=7))
    cal.add('TZNAME', 'ICT')
    cal.add('DTSTART', datetime(1970, 1, 1))

    cnt = 13
    while (cnt < len(data) - 13):
        event = Event()
        time = get_time(data[cnt + 5])
        day_of_week = get_DOW(data[cnt + 5])

        first_date = datetime.strptime(open_day, "%Y%m%d")
        while first_date.strftime("%a").upper()[:2] != day_of_week:
            first_date = first_date + timedelta(1)
        first_date = first_date.strftime("%Y%m%d")

        event['summary'] = data[cnt + 2]
        event['dtstart'] = first_date + time['start']
        event['dtend'] = first_date + time['end']
        event['rrule'] = 'FREQ=WEEKLY;UNTIL=' + end_day + ';BYDAY=' + day_of_week
        event['description'] = "Just test"
        event['location'] = "King Mongkut's Institute of Technology Ladkrabang, 1 Chalong Krung, Thanon Chalong Krung, Lat Krabang, Bangkok 10520"

        cal.add_component(event)
        cnt += 8

    return display(cal.to_ical())

# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django import forms
from django.utils.encoding import smart_text

from icalendar import Calendar, Event
from bs4 import BeautifulSoup
from datetime import datetime as Datetime, timedelta
import html5.forms.widgets as html5_widgets

class UploadText(forms.Form):
    open_date_semester = forms.CharField(widget=html5_widgets.DateInput(), label="Opening semester day")
    end_date_semester = forms.CharField(widget=html5_widgets.DateInput(), label="Ending semester day")
    regHtml = forms.CharField(widget=forms.Textarea(attrs={'style': 'width:100%'}), label="report_studytable_show.php's source code")

def convert2calendar(text):
    soup = BeautifulSoup(text, "html.parser")

    try:
        subTD = soup.find_all('td')
    except AttributeError:
        return 0

    pure_text = list()
    for i in subTD:
        if i.text != "":
            pure_text.append(smart_text(i.text, encoding='tis-620', strings_only=False, errors='strict').encode("utf-8"))
    return pure_text

def get_time(date_input):
    date_input = date_input.split(" ")
    time = date_input[1].split("-")

    start_time = Datetime.strptime(time[0], "%H:%M")
    start_time = start_time.strftime("T%H%M%S")

    end_time = Datetime.strptime(time[1], "%H:%M")
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
    return text.decode("utf-8").replace('\r\n', '\n').replace("\;", ";").replace('("', '').replace('\,', ',').replace('",)', '').strip()

def create_ical_download(open_day, end_day, data):

    semester_open_day = Datetime.strptime(open_day, "%Y-%m-%d").strftime("%Y%m%d")
    semester_end_day = (Datetime.strptime(end_day, "%Y-%m-%d") + timedelta(1)).strftime("%Y%m%d")

    # Add header of iCalendar
    cal = Calendar()
    cal.add('PRODID', '-//Google Inc//Google Calendar 70.9054//EN')
    cal.add('VERSION', '2.0')
    cal.add('TZID', 'Asia/Bangkok')
    cal.add('X-LIC-LOCATION', 'Asia/Bangkok')
    cal.add('TZOFFSETFROM', timedelta(hours=7))
    cal.add('TZOFFSETTO', timedelta(hours=7))
    cal.add('TZNAME', 'ICT')
    cal.add('DTSTART', Datetime(1970, 1, 1))

    subjects = getSubject(semester_open_day, semester_end_day, data)

    for subject in subjects:
        event = Event()
        event['summary'] = subject['subject']
        event['dtstart'] = subject['date_start'] + subject['time_start']
        event['dtend'] = subject['date_start'] + subject['time_end']
        event['rrule'] = 'FREQ=WEEKLY;UNTIL=' + semester_end_day + ';BYDAY=' + subject['day_of_week']
        event['description'] = subject['description']
        event['location'] = subject['location']
        cal.add_component(event)

    return display(cal.to_ical())

def getSubject(semester_open_day, semester_end_day, data):

    # Pattern of index data's list
    # cnt + 0 -> No. subject's row
    # cnt + 1 -> ID subject
    # cnt + 2 -> Subject's name
    # cnt + 3 -> Unit
    # cnt + 4 -> Sec(Group)
    # cnt + 5-> lab section
    # cnt + 6 -> Datetime
    # cnt + 7 -> Room
    # cnt + 8 -> Building

    header_amount = 17
    table_row = 9

    # Crop only subject data, Remove Header of table and page
    data = data[header_amount:]
    subject_list = list()

    cnt = 0
    while (cnt < len(data)):
        subject = dict()

        # Get dict of time (look at get_time to find key's name)
        time = get_time(data[cnt + 6])

        # Get day of week to 2 upper character
        day_of_week = get_DOW(data[cnt + 6])

        # first_date is date that subject is begin first time
        # loop run until found date that day of week equal day of week from student's table
        first_date = Datetime.strptime(semester_open_day, "%Y%m%d")
        while first_date.strftime("%a").upper()[:2] != day_of_week:
            first_date = first_date + timedelta(1)
        first_date = first_date.strftime("%Y%m%d")

        # Date time data get from loop above here
        subject['date_start'] = first_date
        subject['time_start'] = time['start']
        subject['date_end'] = first_date
        subject['time_end'] = time['end']
        subject['day_of_week'] = day_of_week

        subject['no'] = data[cnt]
        subject['id_subject'] = data[cnt+1]
        subject['subject'] = data[cnt+2]
        subject['unit'] = data[cnt+3]
        subject['group'] = data[cnt+4]
        subject['room'] = data[cnt+7]
        subject['building'] = data[cnt+8]
        subject['location'] = "King Mongkut's Institute of Technology Ladkrabang, 1 Chalong Krung, Thanon Chalong Krung, Lat Krabang, Bangkok 10520"

        subject['description'] = getDescription(subject, data[cnt + 6])

        subject_list.append(subject)
        cnt += table_row

    return subject_list

def getDescription(subject, origin_datetime):

    # origin_datetime is text of datetime from table html that isn't process

    description_list = {
                    'subject': subject['id_subject'] + ": " + subject['subject'],
                    'group': subject['group'],
                    'unit': subject['unit'],
                    'datetime': origin_datetime,
                    'class': subject['room'],
                    'building': subject['building']
                }

    desc_text = description_list['subject'] + "\n"
    desc_text += "Group (Sec): " + description_list['group'] + "\n"
    desc_text += "Unit: " + description_list['unit'] + "\n"
    desc_text += "Time: " + description_list['datetime'] + "\n"
    desc_text += "Room: " + description_list['class'] + "(" + description_list['building'] + ")\n"

    return desc_text
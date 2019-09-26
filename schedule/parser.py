from datetime import datetime, date
from .models import Lesson, Lesson_Timing, Lesson_Name, Teacher_Name, Group

import requests
from bs4 import BeautifulSoup

WEEKDAY = {
        'Понедельник' : 'mon',
        'Вторник' : 'tue',
        'Среда' : 'wed',
        'Четверг' : 'thu',
        'Пятница' : 'fri',
        'Суббота': 'sat',
    }

MONTH = {
        'января' : 1,
        'февраля' : 2,
        'марта' : 3,
        'апреля': 4,
        'мая' : 5,
        'июня' : 6,
        'июля' : 7,
        'августа' : 8,
        'сентября'  : 9,
        'октября' : 10,
        'ноября' : 11,
        'декаюря' : 12,
    }


def date_maker(date_title, year=datetime.now().year):
    month = ''
    try:
        month = MONTH[(date_title.split(' ')[1])]
    except KeyError:
        print('Can\'t parse a month')
    day = int(date_title.split(' ')[0])

    return date(year, month, day)

class Student:
    def __init__(self, student_id, group):
        self.student_id = student_id
        self.group = group

class Etis_Schedule_Parser:
    """
    Provides parsing of the schedule
    """

    def __init__(self, end_point, user_agent, session_id):
        self.end_point = end_point
        self.schedule_url = end_point.format('stu.timetable?p_cons=n&p_week={0}')
        self.headers = {
            'user-agent': user_agent
        }
        self.jar = requests.cookies.RequestsCookieJar()
        self.jar.set(
            'session_id', # Cookie name
            session_id, # Id of client
            domain='.student.psu.ru',
            path='/'
        )

        if not self.__session_check__():
            raise ValueError('Wrong session id')

        self.__create_student__()

    def __session_check__(self):
        result = True

        r = self.__etis_request__()

        if '<form action="https://student.psu.ru/pls/stu_cus_et/stu.login" method="post" id="form">' in r.raw:
            result = False

        return result

    def __etis_request__(self, url=None):
        if url is None:
            url = self.schedule_url.format(0) # HACK: Couldn't set through arguments

        r = requests.get(
            url=url,
            headers=self.headers,
            cookies=self.jar,
        )

        return r

    def __create_student__(self):
        r = self.__etis_request__(self.end_point.format('stu.signs?p_mode=current'))
        soup = BeautifulSoup(r.content)
        group = soup.find('div', 'span12').span.span.text # USE GROUP ID INSTEAD!!!!
        group += ' ' + soup.find('div', 'span12').span.find_all('span')[2].text

        student_id = soup.table.find_all('tr')[2].find_all('td')[3].get('data-url')

        if student_id is None:
            raise ValueError('Can\'t get a student_id')

        self.student = Student(student_id, group)

    def __end_time__(self, start_time, time_length=95):
        minutes = 0
        if ':' in start_time:
            hour = int(start_time.split(':')[0])
            min = int(start_time.split(':')[1])

            minutes = hour * 60 + min + time_length

        return '{0}:{1}'.format(
            minutes // 60,
            minutes % 60)

    def __update_schedule__(
            self, weekday,
            date,lesson_start_time,
            lesson_number, lesson_teacher,
            lesson_name, lesson_auditory):

        if Group.objects.filter(group_name=)


    def __parse_day__(self, day):
        day_meta = day.h3.text.split(', ')
        weekday = WEEKDAY[day_meta[0]]
        date = date_maker(day_meta[1])

        lessons_meta = day.table.find_all('tr') # Dictionary of every lessons
        for lesson in lessons_meta:
            # Not a final one! Just parsing!
            lesson_meta = lessons_meta.find_all('td') # Dictionary of meta of a current lesson

            lesson_start_time = lessons_meta[0].font.text
            lesson_end_time = self.__end_time__(lesson_start_time)
            lesson_number = lessons_meta[0].replace(lesson_start_time).split(' ')[0]

            lesson_teacher = lessons_meta[1].find('span', {'class' : 'teacher'}).text.strip()
            lesson_name = lessons_meta[1].find('span', {'class' : 'dis'}).text.strip()
            lesson_auditory = lessons_meta[1].find('span', {'class' : 'aud'}).text



    def parse_week(self, week_number):
        if week_number < 0:
            raise ValueError('Incorrect week number')

        r = self.__etis_request__()
        soup = BeautifulSoup(r.content)
        timetable = soup.find('div',
                             {'class': 'timetable'}
                             ).find_all(
                             'div',
                                {'class': 'day'}
                             )

        for day in timetable:
            self.__parse_day__(day)





class Etis_Tool:
    """
    Provides access to the general ETIS functions
    """
    END_POINT = 'https://student.psu.ru/pls/stu_cus_et/{0}'
    SCHEDULE_URL = END_POINT.format('stu.timetable?p_cons=n&p_week={0}')
    USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; de-DE) AppleWebKit/534.17 (KHTML, like Gecko) Chrome/10.0.649.0 Safari/534.17'


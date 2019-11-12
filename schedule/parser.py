from datetime import datetime, date, timedelta
from .models import Lesson, Lesson_Timing, Lesson_Name, Group, Student

import requests
from bs4 import BeautifulSoup

# There is need to be some kind of converter
# from ETIS's text to a short one
# So that's there are those lists
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
        'декабря' : 12,
    }


def date_maker(date_title, year=datetime.now().year):
    """
    Converter from ETIS date to a serialized one
    """

    month = ''
    try:
        month = MONTH[(date_title.split(' ')[1])]
    except KeyError:
        print('Can\'t parse a month')
    day = int(date_title.split(' ')[0])

    return date(year, month, day)


def end_time(start_time, time_length=95):
    """
    Calculates end time of the lesson
    """

    return datetime.strptime(start_time, '%H:%M') + timedelta(minutes=time_length)

class EtisStudent:
    def __init__(self, student_id, group):
        self.student_id = student_id
        self.group = int(group)

        if not self.__group_check__(group): # Checking for the existence of the group in model
            new_group = Group(group_id=group)
            new_group.save()
            del new_group # Just in case. I'm not sure about this.

        if not self.__student_check__(student_id): # Checking for the existence of the student in model
            group_model = Group.objects.get(group_id=group)
            new_student = Student(
                student_id=student_id,
                group=group_model
            )
            new_student.save()
            del new_student # Just in case. I'm not sure about this.

        self.group_model = Group.objects.get(group_id=group)
        self.student_model = Student.objects.get(
            student_id=student_id,
            group=self.group_model
        )

    def update_schedule(
            self, weekday, date, lesson_start_time, number,
            teacher, name, auditory):
        lesson_end_time = end_time(lesson_start_time)
        self.__time_check__(lesson_start_time, lesson_end_time)
        self.__check_lesson_name__(name)

        lesson_name = Lesson_Name.objects.get(lesson_name=name)
        time_model = Lesson_Timing.objects.get(
            start=lesson_start_time,
            end=lesson_end_time
        )

        # WARNING! THERE IS A PROBLEM WITH A LESSON UPDATES!
        # SHOULD THINK HOW TO FIX IT!

        new_lesson = Lesson(
            date=date,
            weekday=weekday,
            group=self.group_model,
            time=time_model,
            name=lesson_name,
            teacher_name=teacher,
            number=number,
            audience=auditory
        )
        new_lesson.save()
        del new_lesson


    def update_marks(self, marks):
        self.marks = marks

    def __group_check__(self, group):
        return Group.objects.filter(group_id=group).exists()

    def __student_check__(self, student_id):
        return Student.objects.filter(student_id=student_id).exists()

    def __time_check__(self, start, end):
        """
        Stores time periods in models
        """
        if not Lesson_Timing.objects.filter(
            start=start,
            end=end
        ).exists():
            time = Lesson_Timing(
                start=start,
                end=end
            )
            time.save()
            del time

    def __check_lesson_name__(self, name):
        """
        Stores lesson names in models
        """
        if not Lesson_Name.objects.filter(lesson_name=name).exists():
            lesson = Lesson_Name(lesson_name=name)
            lesson.save()
            del lesson

class EtisScheduleParser:
    """
    Provides parsing of a schedule
    """

    def __init__(self, end_point, user_agent, session_id):
        self.end_point = end_point
        self.schedule_url = end_point.format('stu.timetable?p_cons=n&p_week={0}')
        self.headers = {
            'user-agent': user_agent
        }
        self.jar = requests.cookies.RequestsCookieJar()
        self.jar.set(
            'session_id', # Cookies name
            session_id, # Id of a client
            domain='.student.psu.ru',
            path='/'
        )

        if not self.__session_check__():
            raise ValueError('Wrong session id')

        self.__create_student__()
        self.max_week = self.__parse_week_number__()

    def __session_check__(self):
        result = True

        r = self.__etis_request__()

        if '<form action="https://student.psu.ru/pls/stu_cus_et/stu.login" method="post" id="form">' in r.raw:
            # Looks like a DIRTY HACK
            result = False

        return result

    def __parse_week_number__(self):
        r = self.__etis_request__()
        soup = BeautifulSoup(r.text, "html.parser") # Doesn't work with a standard parser
        number = soup.find_all('li', {'class': 'week'})[-1].text.strip()

        return int(number)

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
        r = self.__etis_request__(self.end_point.format('stu.timetable'))
        soup = BeautifulSoup(r.content, "html.parser")

        group = soup.find('td', {'class': 'pair_jour'}).a.get('href').split('p_ng_id=')[1]

        r = self.__etis_request__(self.end_point.format('stu.signs?p_mode=current'))
        soup = BeautifulSoup(r.content, "html.parser") # Doesn't work with a standard parser

        student_id = soup.table.find_all('tr')[2].find_all('td')[3].get('data-url').split('p_stu_id=')[1]

        if student_id is None:
            raise ValueError('Can\'t get a student_id')

        self.student = EtisStudent(student_id, group)

    def __parse_day__(self, day):
        day_meta = day.h3.text.split(', ') # Consists of <Day name>, date
        weekday = WEEKDAY[day_meta[0]] # Weekday of the processing day
        date = date_maker(day_meta[1]) # Date of the processing day

        if not day.find('div', {'class': 'no_pairs'}):
            lessons_meta = day.table.find_all('tr') # Dictionary of every lessons of the day
            for lesson in lessons_meta:
                # Not a final result! Just tmp parse dictionary!
                lesson_meta = lesson.find_all('td') # Dictionary of meta of a processing lesson

                if lesson_meta[1].find('span', {'class' : 'dis'}): # Just in case
                    lesson_start_time = lesson_meta[0].font.text
                    lesson_number = lesson_meta[0].text.split(' ')[0]

                    lesson_teacher = lesson_meta[1].find('span', {'class' : 'teacher'}).text.strip().split('\n')[0]
                    lesson_name = lesson_meta[1].find('span', {'class' : 'dis'}).text.strip()
                    lesson_auditory = lesson_meta[1].find('span', {'class' : 'aud'}).text

                    self.student.update_schedule(
                        weekday=weekday,
                        date=date,
                        lesson_start_time=lesson_start_time,
                        number=lesson_number,
                        teacher=lesson_teacher,
                        name=lesson_name,
                        auditory=lesson_auditory
                    )

    def parse_week(self, week_number):
        if week_number < 0:
            raise ValueError('Incorrect week number')

        r = self.__etis_request__(self.end_point.format(
            'stu.timetable?p_cons=n&p_week={0}'.format(week_number))
        )
        soup = BeautifulSoup(r.text, "lxml")
        timetable = soup.find_all('div', {'class': 'day'})

        for day in timetable:
            self.__parse_day__(day)


class EtisTool:
    """
    Provides access to the general ETIS functions
    """
    END_POINT = 'https://student.psu.ru/pls/stu_cus_et/{0}'
    SCHEDULE_URL = END_POINT.format('stu.timetable?p_cons=n&p_week={0}')
    USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; de-DE) AppleWebKit/534.17 (KHTML, like Gecko) Chrome/10.0.649.0 Safari/534.17'

    def __init__(self, session_id):
        self.parser = EtisScheduleParser(
            end_point=self.END_POINT,
            user_agent=self.USER_AGENT,
            session_id=session_id
        )

    def parse_week(self, week_number):
        self.parser.parse_week(week_number)

    def full_parse(self):
        for week in range(1, self.parser.max_week):
            self.parser.parse_week(week)

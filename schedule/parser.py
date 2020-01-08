from datetime import datetime, date, timedelta
from string import digits

import requests
from bs4 import BeautifulSoup

from .models import Lesson, Lesson_Timing, Lesson_Name, Group, Student, Week_Period

# There is need to be some kind of converter
# from ETIS's text to a short one
# So that's there are those lists
WEEKDAY = {
        'Понедельник': 'mon',
        'Вторник': 'tue',
        'Среда': 'wed',
        'Четверг': 'thu',
        'Пятница': 'fri',
        'Суббота': 'sat',
    }

WEEKDAY_REVERSE = {
        'mon': 'Понедельник',
        'tue': 'Вторник',
        'wed' : 'Среда',
        'thu' : 'Четверг',
        'fri' : 'Пятница',
        'sat' : 'Суббота',
    }

MONTH = {
        'января': 1,
        'февраля': 2,
        'марта': 3,
        'апреля': 4,
        'мая': 5,
        'июня': 6,
        'июля': 7,
        'августа': 8,
        'сентября': 9,
        'октября': 10,
        'ноября': 11,
        'декабря': 12,
    }

MONTH_REVERSE = [None, 'января', 'февраля', 'марта',
                 'апреля', 'мая', 'июня', 'июля', 'августа',
                 'сентября', 'октября', 'ноября', 'декабря']

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

def remove_all_chars(string):
    return ''.join([i for i in string if i in digits or i == '.'])

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
            self, weekday, week, date, lesson_start_time,
            number, teacher, name, auditory):
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
            week=week,
            group=self.group_model,
            time=time_model,
            name=lesson_name,
            teacher_name=teacher,
            number=number,
            audience=auditory
        )
        new_lesson.save()
        del new_lesson


    def update_week_preiod(self, week, period_start, period_end):
        new_period = Week_Period(
            week=week,
            period_start=datetime.strptime(period_start[0:10], '%d.%m.%Y'),
            period_end=datetime.strptime(period_end[0:10], '%d.%m.%Y')
        )
        new_period.save()
        del new_period



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

        self.first_week = self.__get_first_week__()
        self.max_week = self.__parse_week_number__()
        self.__create_student__()

    def __session_check__(self):
        result = True

        r = self.__etis_request__()

        if '<form action="https://student.psu.ru/pls/stu_cus_et/stu.login" method="post" id="form">' in r.text:
            # Looks like a DIRTY HACK
            result = False

        return result

    def __parse_week_number__(self):
        r = self.__etis_request__()
        soup = BeautifulSoup(r.text, "lxml") # Doesn't work with a standard parser
        number = soup.find_all('li', {'class': 'week'})[-1].text.strip()

        return int(number)

    def __get_first_week__(self):
        r = self.__etis_request__()
        soup = BeautifulSoup(r.text, "lxml")
        number = soup.find_all('li', {'class': 'week'})[0].text.strip()

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
        r = self.__etis_request__(self.schedule_url.format(self.first_week))  # HACK: Looks like a bad practice
        soup = BeautifulSoup(r.content, "lxml")

        try:
            group = soup.find('td', {'class': 'pair_jour'}).a.get('href').split('p_ng_id=')[1]
        except IndexError:
            raise ValueError('Can\'t get a group')

        r = self.__etis_request__(self.end_point.format('stu.signs?p_mode=current'))
        soup = BeautifulSoup(r.content, "lxml") # Doesn't work with a standard parser

        student_id = soup.table.find_all('tr')[2].find_all('td')[3].get('data-url').split('p_stu_id=')[1]

        if student_id is None:
            raise ValueError('Can\'t get a student_id')

        self.student = EtisStudent(student_id, group)

    def __parse_day__(self, day, week_number):
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
                        week=week_number,
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
            self.__parse_day__(day, week_number)

    def __parse_week_period__(self, week_number):
        if week_number < 0:
            raise ValueError('Incorrect week number')

        r = self.__etis_request__(self.end_point.format(
            'stu.timetable?p_cons=n&p_week={0}'.format(week_number))
        )
        soup = BeautifulSoup(r.text, "lxml")
        period = soup.find('div', {'style': 'margin-top: 5px;text-align:center;'})
        period = period.span.text.strip().split(' по ') # DIRTY FUCKING HACK!
        self.student.update_week_preiod(week_number, remove_all_chars(period[0]), remove_all_chars(period[1]))

    def parse_every_week_period(self):
        for week in range(self.first_week, self.max_week):
            self.__parse_week_period__(week)

    def get_student_info(self):
        r = self.__etis_request__(self.end_point.format('stu.teach_plan'))
        soup = BeautifulSoup(r.text, "lxml")

        return soup.find('div', {'class': 'span12'}).text

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

    def student_info(self):
        student_info = self.parser.get_student_info().split('\n') # FUCKING DISGUSTING DIRTY HACK!!!
        result = {
            'student_id' : int(self.parser.student.student_id),
            'student_group_id' : self.parser.student.group,
            'student_group_name' : student_info[2].strip(),
            'student_name' : student_info[1].strip(),
            'student_year' : int(student_info[4].strip()),
            'student_type' : student_info[3].strip()
        }

        return result

    def return_week(self, week_number, formated=False):
        group_model = Group.objects.get(group_id=int(self.parser.student.group))
        objects = Lesson.objects.filter(week=week_number, group=group_model)
        if not objects.exists():
            self.parse_week(week_number)
        result = []
        if not formated:
            for day in objects:
                result.append(
                    {
                        'date' : day.date,
                        'name' : day.name.lesson_name,
                        'time' : str(day.time),
                        'weekday': day.weekday,
                        'teacher_name' : day.teacher_name,
                        'number' : day.number,
                        'audience' : day.audience,
                    }
                )

        if formated:
            for day in objects:
                result.append(
                    {
                        'title' : '{0}, {1} {2}'.format(
                            WEEKDAY_REVERSE[day.weekday],
                            str(day.date).split('-')[2],
                            MONTH_REVERSE[int(str(day.date).split('-')[1])]
                        ),
                        'date' : day.date,
                        'name' : day.name.lesson_name,
                        'time' : str(day.time),
                        'weekday': day.weekday,
                        'teacher_name' : day.teacher_name,
                        'number' : day.number,
                        'audience' : day.audience,
                    }
                )

        return result

    def week_periods(self):
        objects = Week_Period.objects.all()
        if not objects.exists():
            self.parser.parse_every_week_period()

        result = {}
        for week in objects:
            result[week.week] = [
                str(week.period_start),
                str(week.period_end)
            ]

        return result
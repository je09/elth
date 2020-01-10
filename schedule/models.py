from django.db import models, migrations


class Group(models.Model):
    group_id = models.IntegerField(blank=False, default=0)
    date_updated = models.DateTimeField(blank=False, auto_now=True)

    def __str__(self):
        return str(self.group_id)


class Lesson_Name(models.Model):
    lesson_name = models.CharField(blank=False, default='Lesson Name', max_length=100)
    date_updated = models.DateTimeField(blank=False, auto_now=True)

    def __str__(self):
        return self.lesson_name

class Week_Period(models.Model):
    week = models.IntegerField(blank=False, default=0)
    period_start = models.DateField(blank=False)
    period_end = models.DateField(blank=False)

class Lesson_Timing(models.Model):
    start = models.TimeField(blank=False)
    end = models.TimeField(blank=False)

    def __str__(self):
        return '{0} – {1}'.format(
            self.start, self.end)


class Lesson(models.Model):
    WEEKDAYS = (
        ('mon', 'Monday',),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
    )

    date = models.DateField(blank=False)
    weekday = models.CharField(blank=False, max_length=3, choices=WEEKDAYS)
    week = models.IntegerField(blank=False)
    group = models.ForeignKey(Group, null=True, on_delete=models.SET_NULL)
    time = models.ForeignKey(Lesson_Timing, null=True, on_delete=models.SET_NULL)
    name = models.ForeignKey(Lesson_Name, null=True, on_delete=models.SET_NULL)
    teacher_name = models.CharField(blank=False, default="Teacher name", max_length=40)
    number = models.IntegerField(blank=False)
    audience = models.CharField(blank=False, max_length=50)
    date_updated = models.DateTimeField(blank=False, auto_now=True)


class Student(models.Model):
    student_id = models.IntegerField(blank=False, default=0, primary_key=True)
    group = models.ForeignKey(Group, null=True, on_delete=models.SET_NULL)
    date_updated = models.DateTimeField(blank=False, auto_now=True)

    def __str__(self):
        return str(self.student_id)

class Mark(models.Model):
    pass


class Lesson_Choiced_Name(models.Model):
    lesson_name = models.CharField(blank=False, default='Lesson Name', max_length=100)
    date_updated = models.DateTimeField(blank=False, auto_now=True)

    def __str__(self):
        return self.lesson_name


class Lesson_Choiced(models.Model):
    lesson_name = models.ForeignKey(Lesson_Choiced_Name, null=True, on_delete=models.SET_NULL)
    student = models.ForeignKey(Student, null=True, on_delete=models.SET_NULL)
    date_updated = models.DateTimeField(blank=False, auto_now=True)

    def __str__(self):
        return self.lesson_name

class Duration(models.Model):
    name = models.CharField(blank=False, max_length=50)
    duration = models.TimeField(blank=False)

    def __str__(self):
        return self.name

# def default_duration(apps):
#     Duration = apps.get_model('schedule', 'Duration')
#     Duration.objects.bulk_create([
#         Duration(name='Lesson', duration='0:0:15'),
#         Duration(name='Mark', duration='0:0:15'),
#     ])
#
# class Migration(migrations.Migration):
#     dependencies = [
#         ('schedule', '0001_initial'),
#     ]
#
#     operations = [
#         migrations.RunPython(default_duration),
#     ]
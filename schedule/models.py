from django.db import models

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
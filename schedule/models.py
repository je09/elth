from django.db import models

class Group(models.Model):
    group_name = models.CharField(blank=False, default='Group Name', max_length=100)
    date_updated = models.DateTimeField(blank=False)

    def __str__(self):
        return self.group_name

class Teacher_Name(models.Model):
    name = models.CharField(blank=False, default='Teacher Name', max_length=100)

    def __str__(self):
        return self.name

class Lesson_Name(models.Model):
    lesson_name = models.CharField(blank=False, default='Lesson Name', max_length=100)

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
    number = models.IntegerField(blank=False)
    audience = models.CharField(blank=False, max_length=50)

class Student(models.Model):
    student_id = models.IntegerField(blank=False, default=0, max_length=6, primary_key=True)
    group_name = models.ForeignKey(Group, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.student_id
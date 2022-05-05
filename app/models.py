from django.db import models

# Create your models here.

from django.db import models


class Curriculum(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    class Meta:
        db_table = "curriculum"

class Classes(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=20)
    class Meta:
        db_table = 'classes'

class Students(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    classes = models.OneToOneField(Classes,on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "student"

class Teachers(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)

    class Meta:
        db_table = "teacher"

class TeacherToClass(models.Model):
    id = models.AutoField(primary_key=True)
    teacher = models.OneToOneField(Teachers,on_delete=models.DO_NOTHING)
    classes = models.OneToOneField(Classes,on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "teacher2class"



class CurriculumToClasses(models.Model):
    id = models.AutoField(primary_key=True)
    curriculum = models.OneToOneField(Curriculum,on_delete=models.DO_NOTHING)
    classes = models.OneToOneField(Classes,on_delete=models.DO_NOTHING)
    class Meta:
        db_table = "curriculum2classes"

class TeacherCurriculumToClasses(models.Model):
    curriculumToClasses =models.OneToOneField(CurriculumToClasses,on_delete=models.DO_NOTHING)
    teacher = models.OneToOneField(Teachers, on_delete=models.DO_NOTHING)
    class Meta:
        db_table = "teacherCurriculumToClasses"
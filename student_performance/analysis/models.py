from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Student(models.Model):
    name = models.CharField(max_length=100)
    student_class = models.CharField(max_length=20, verbose_name="Class")
    email = models.EmailField()
    enrollment_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.student_class})"

    def get_average_marks(self):
        marks = self.marks_set.all()
        if marks.exists():
            return round(marks.aggregate(avg=models.Avg('marks'))['avg'], 2)
        return 0

    def get_attendance_percentage(self):
        attendance = self.attendance_set.first()
        if attendance:
            return attendance.attendance_percentage
        return 0


class Subject(models.Model):
    subject_name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['subject_name']

    def __str__(self):
        return self.subject_name


class Marks(models.Model):
    EXAM_CHOICES = [
        ('midterm', 'Midterm'),
        ('final', 'Final'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    max_marks = models.IntegerField(default=100, validators=[MinValueValidator(1)])
    exam_type = models.CharField(max_length=20, choices=EXAM_CHOICES, default='final')

    class Meta:
        verbose_name_plural = "Marks"
        unique_together = ['student', 'subject', 'exam_type']

    def __str__(self):
        return f"{self.student.name} - {self.subject.subject_name}: {self.marks}/{self.max_marks}"

    def get_percentage(self):
        if self.max_marks > 0:
            return round((self.marks / self.max_marks) * 100, 2)
        return 0


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendance_percentage = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        verbose_name_plural = "Attendance"

    def __str__(self):
        return f"{self.student.name} - {self.attendance_percentage}%"
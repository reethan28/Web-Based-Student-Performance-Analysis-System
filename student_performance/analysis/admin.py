from django.contrib import admin
from .models import Student, Subject, Marks, Attendance


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_class', 'email', 'enrollment_date')
    search_fields = ('name', 'email')
    list_filter = ('student_class',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_name',)
    search_fields = ('subject_name',)


@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'marks', 'max_marks', 'exam_type')
    list_filter = ('subject', 'exam_type')
    search_fields = ('student__name',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'attendance_percentage')
    list_filter = ('attendance_percentage',)
    search_fields = ('student__name',)
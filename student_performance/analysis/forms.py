from django import forms
from .models import Student, Subject, Marks, Attendance


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'student_class', 'email']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter student name'
            }),
            'student_class': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 10th A'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'student@example.com'
            }),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['subject_name']
        widgets = {
            'subject_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter subject name'
            }),
        }


class MarksForm(forms.ModelForm):
    class Meta:
        model = Marks
        fields = ['student', 'subject', 'marks', 'max_marks', 'exam_type']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Marks obtained',
                'min': 0,
                'max': 100,
            }),
            'max_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maximum marks',
                'min': 1,
            }),
            'exam_type': forms.Select(attrs={'class': 'form-select'}),
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'attendance_percentage']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'attendance_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Attendance %',
                'min': 0,
                'max': 100,
                'step': '0.1',
            }),
        }

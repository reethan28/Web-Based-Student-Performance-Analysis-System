from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg, Count, Sum, Max, Min, Q
from django.contrib import messages
from .models import Student, Subject, Marks, Attendance
from .forms import StudentForm, SubjectForm, MarksForm, AttendanceForm
import json


def dashboard(request):
    """Main dashboard with summary statistics."""
    total_students = Student.objects.count()
    total_subjects = Subject.objects.count()
    total_marks_entries = Marks.objects.count()

    # Average marks across all students
    avg_marks = Marks.objects.aggregate(avg=Avg('marks'))['avg'] or 0

    # Average attendance
    avg_attendance = Attendance.objects.aggregate(avg=Avg('attendance_percentage'))['avg'] or 0

    # Top 5 performers
    students = Student.objects.all()
    student_averages = []
    for student in students:
        avg = student.get_average_marks()
        student_averages.append({'student': student, 'avg_marks': avg})
    student_averages.sort(key=lambda x: x['avg_marks'], reverse=True)
    top_performers = student_averages[:5]

    # Subject-wise average for chart
    subjects = Subject.objects.all()
    subject_names = [s.subject_name for s in subjects]
    subject_avgs = []
    for subject in subjects:
        avg = Marks.objects.filter(subject=subject).aggregate(avg=Avg('marks'))['avg'] or 0
        subject_avgs.append(round(avg, 2))

    # Pass/fail ratio (marks >= 40 is pass)
    total_pass = Marks.objects.filter(marks__gte=40).count()
    total_fail = Marks.objects.filter(marks__lt=40).count()

    context = {
        'total_students': total_students,
        'total_subjects': total_subjects,
        'total_marks_entries': total_marks_entries,
        'avg_marks': round(avg_marks, 2),
        'avg_attendance': round(avg_attendance, 2),
        'top_performers': top_performers,
        'subject_names': json.dumps(subject_names),
        'subject_avgs': json.dumps(subject_avgs),
        'total_pass': total_pass,
        'total_fail': total_fail,
    }
    return render(request, 'analysis/dashboard.html', context)


# ──────────────────── Student CRUD ────────────────────

def student_list(request):
    """List all students with search."""
    query = request.GET.get('q', '')
    students = Student.objects.all()
    if query:
        students = students.filter(
            Q(name__icontains=query) | Q(student_class__icontains=query) | Q(email__icontains=query)
        )

    for student in students:
        student.avg_marks = student.get_average_marks()
        student.attendance = student.get_attendance_percentage()

    return render(request, 'analysis/student_list.html', {
        'students': students,
        'query': query,
    })


def student_add(request):
    """Add a new student."""
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student added successfully!')
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'analysis/student_form.html', {
        'form': form,
        'title': 'Add Student',
    })


def student_edit(request, pk):
    """Edit an existing student."""
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully!')
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'analysis/student_form.html', {
        'form': form,
        'title': 'Edit Student',
    })


def student_delete(request, pk):
    """Delete a student."""
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully!')
        return redirect('student_list')
    return render(request, 'analysis/student_confirm_delete.html', {
        'student': student,
    })


def student_detail(request, pk):
    """Individual student report with marks breakdown."""
    student = get_object_or_404(Student, pk=pk)
    marks = Marks.objects.filter(student=student).select_related('subject')
    attendance = Attendance.objects.filter(student=student).first()

    # Data for chart
    subject_names = [m.subject.subject_name for m in marks]
    marks_values = [m.marks for m in marks]

    avg_marks = student.get_average_marks()

    # Grade calculation
    if avg_marks >= 90:
        grade = 'A+'
    elif avg_marks >= 80:
        grade = 'A'
    elif avg_marks >= 70:
        grade = 'B+'
    elif avg_marks >= 60:
        grade = 'B'
    elif avg_marks >= 50:
        grade = 'C'
    elif avg_marks >= 40:
        grade = 'D'
    else:
        grade = 'F'

    context = {
        'student': student,
        'marks': marks,
        'attendance': attendance,
        'avg_marks': avg_marks,
        'grade': grade,
        'subject_names': json.dumps(subject_names),
        'marks_values': json.dumps(marks_values),
    }
    return render(request, 'analysis/student_detail.html', context)


# ──────────────────── Marks ────────────────────

def add_marks(request):
    """Add marks for a student."""
    if request.method == 'POST':
        form = MarksForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marks added successfully!')
            return redirect('add_marks')
    else:
        form = MarksForm()

    recent_marks = Marks.objects.select_related('student', 'subject').order_by('-id')[:10]
    return render(request, 'analysis/add_marks.html', {
        'form': form,
        'recent_marks': recent_marks,
    })


def edit_marks(request, pk):
    """Edit existing marks entry."""
    mark = get_object_or_404(Marks, pk=pk)
    if request.method == 'POST':
        form = MarksForm(request.POST, instance=mark)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marks updated successfully!')
            return redirect('add_marks')
    else:
        form = MarksForm(instance=mark)
    return render(request, 'analysis/add_marks.html', {
        'form': form,
        'editing': True,
    })


def delete_marks(request, pk):
    """Delete a marks entry."""
    mark = get_object_or_404(Marks, pk=pk)
    if request.method == 'POST':
        mark.delete()
        messages.success(request, 'Marks entry deleted!')
    return redirect('add_marks')


# ──────────────────── Attendance ────────────────────

def attendance_view(request):
    """Record and view attendance."""
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            # Update existing or create new
            att, created = Attendance.objects.update_or_create(
                student=student,
                defaults={'attendance_percentage': form.cleaned_data['attendance_percentage']}
            )
            action = 'recorded' if created else 'updated'
            messages.success(request, f'Attendance {action} for {student.name}!')
            return redirect('attendance')
    else:
        form = AttendanceForm()

    records = Attendance.objects.select_related('student').order_by('-attendance_percentage')
    return render(request, 'analysis/attendance.html', {
        'form': form,
        'records': records,
    })


# ──────────────────── Reports ────────────────────

def class_report(request):
    """Class-wide performance analytics."""
    students = Student.objects.all()
    subjects = Subject.objects.all()

    # Build student performance data
    student_data = []
    for student in students:
        avg = student.get_average_marks()
        att = student.get_attendance_percentage()
        student_data.append({
            'name': student.name,
            'class': student.student_class,
            'avg_marks': avg,
            'attendance': att,
        })

    # Subject-wise statistics
    subject_stats = []
    for subject in subjects:
        marks_qs = Marks.objects.filter(subject=subject)
        stats = marks_qs.aggregate(
            avg=Avg('marks'),
            highest=Max('marks'),
            lowest=Min('marks'),
            total_students=Count('student', distinct=True),
        )
        subject_stats.append({
            'subject': subject.subject_name,
            'avg': round(stats['avg'] or 0, 2),
            'highest': stats.get('highest') or 0,
            'lowest': stats.get('lowest') or 0,
            'total_students': stats.get('total_students') or 0,
        })

    # Grade distribution
    grade_counts = {'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    for sd in student_data:
        avg = sd['avg_marks']
        if avg >= 90:
            grade_counts['A+'] += 1
        elif avg >= 80:
            grade_counts['A'] += 1
        elif avg >= 70:
            grade_counts['B+'] += 1
        elif avg >= 60:
            grade_counts['B'] += 1
        elif avg >= 50:
            grade_counts['C'] += 1
        elif avg >= 40:
            grade_counts['D'] += 1
        elif avg > 0:
            grade_counts['F'] += 1

    # Chart data
    student_names = [sd['name'] for sd in student_data]
    student_avgs = [sd['avg_marks'] for sd in student_data]
    subject_chart_names = [ss['subject'] for ss in subject_stats]
    subject_chart_avgs = [ss['avg'] for ss in subject_stats]

    context = {
        'student_data': student_data,
        'subject_stats': subject_stats,
        'grade_labels': json.dumps(list(grade_counts.keys())),
        'grade_values': json.dumps(list(grade_counts.values())),
        'student_names': json.dumps(student_names),
        'student_avgs': json.dumps(student_avgs),
        'subject_chart_names': json.dumps(subject_chart_names),
        'subject_chart_avgs': json.dumps(subject_chart_avgs),
    }
    return render(request, 'analysis/class_report.html', context)


# ──────────────────── Subjects ────────────────────

def subject_list(request):
    """List and add subjects."""
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject added successfully!')
            return redirect('subject_list')
    else:
        form = SubjectForm()

    subjects = Subject.objects.annotate(student_count=Count('marks__student', distinct=True))
    return render(request, 'analysis/subject_list.html', {
        'form': form,
        'subjects': subjects,
    })


def subject_delete(request, pk):
    """Delete a subject."""
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted!')
    return redirect('subject_list')
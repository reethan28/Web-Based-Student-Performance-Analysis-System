from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Students
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_add, name='student_add'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),

    # Marks
    path('marks/add/', views.add_marks, name='add_marks'),
    path('marks/<int:pk>/edit/', views.edit_marks, name='edit_marks'),
    path('marks/<int:pk>/delete/', views.delete_marks, name='delete_marks'),

    # Attendance
    path('attendance/', views.attendance_view, name='attendance'),

    # Subjects
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),

    # Reports
    path('report/', views.class_report, name='class_report'),
]
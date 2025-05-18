from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from info.models import (
    Dept, Class, Student, Teacher, Course, Assign, 
    AssignTime, AttendanceClass, Attendance, AttendanceTotal,
    StudentCourse, Marks, MarksClass
)
from django.utils import timezone
from datetime import timedelta, date

User = get_user_model()

class InfoViewsTest(TestCase):
    def setUp(self):
        # Create test data
        self.client = Client()
        
        # Create departments
        self.dept = Dept.objects.create(name="Informatique", id="INFO")
        
        # Create classes
        self.class_obj = Class.objects.create(
            id="INFO2023",
            dept=self.dept,
            section="A",
            sem=3
        )
        
        # Create users without is_student/is_teacher properties
        self.student_user = User.objects.create_user(
            username="student1",
            password="password123",
            email="student1@example.com"
        )
        
        self.teacher_user = User.objects.create_user(
            username="teacher1",
            password="password123",
            email="teacher1@example.com"
        )
        
        self.admin_user = User.objects.create_user(
            username="admin1",
            password="password123",
            email="admin1@example.com",
            is_superuser=True
        )
        
        # Create student - this will set is_student property on user
        self.student = Student.objects.create(
            USN="INFO2023001",
            name="John Doe",
            sex="Male",
            DOB="2000-01-01",
            class_id=self.class_obj,
            user=self.student_user
        )
        
        # Create teacher - this will set is_teacher property on user
        self.teacher = Teacher.objects.create(
            id="TEACHER001",
            name="Prof Smith",
            sex="Male",
            DOB="1980-01-01",
            dept=self.dept,
            user=self.teacher_user
        )
        
        # Create course
        self.course = Course.objects.create(
            id="CS101",
            name="Introduction to Programming",
            shortname="IntroProgram",
            dept=self.dept
        )
        
        # Create assignment
        self.assign = Assign.objects.create(
            class_id=self.class_obj,
            course=self.course,
            teacher=self.teacher
        )
        
        # Create student course
        self.student_course = StudentCourse.objects.create(
            student=self.student,
            course=self.course
        )
        
        # Create attendance total
        self.attendance_total = AttendanceTotal.objects.create(
            student=self.student,
            course=self.course,
            attendance=85
        )
        
        # Create attendance
        self.attendance = Attendance.objects.create(
            student=self.student,
            course=self.course,
            date=timezone.now().date(),
            status='Present'
        )
    
    def test_index_view_student(self):
        self.client.login(username='student1', password='password123')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/homepage.html')
    
    def test_index_view_teacher(self):
        self.client.login(username='teacher1', password='password123')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/t_homepage.html')
    
    def test_index_view_admin(self):
        self.client.login(username='admin1', password='password123')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/admin_page.html')
    
    def test_index_view_unauthenticated(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302)  # Redirect to login page
    
    def test_attendance_view(self):
        self.client.login(username='student1', password='password123')
        response = self.client.get(reverse('attendance', args=[self.student.USN]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/attendance.html')
        self.assertIn('att_list', response.context)
        self.assertEqual(len(response.context['att_list']), 1)
    
    def test_attendance_detail_view(self):
        self.client.login(username='student1', password='password123')
        response = self.client.get(reverse('attendance_detail', args=[self.student.USN, self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/att_detail.html')
        self.assertIn('att_list', response.context)
        self.assertEqual(len(response.context['att_list']), 1)
        self.assertIn('cr', response.context)
        self.assertEqual(response.context['cr'], self.course)
    
    def test_attendance_view_unauthorized(self):
        # Test that a teacher cannot access a student's attendance
        self.client.login(username='teacher1', password='password123')
        response = self.client.get(reverse('attendance', args=[self.student.USN]))
        self.assertEqual(response.status_code, 302)  # Should redirect or return 403
    
    def test_attendance_detail_view_nonexistent(self):
        self.client.login(username='student1', password='password123')
        response = self.client.get(reverse('attendance_detail', args=[self.student.USN, 'NONEXISTENT']))
        self.assertEqual(response.status_code, 404)  # Should return 404 for non-existent course

class TeacherViewsTest(TestCase):
    def setUp(self):
        # Create test data
        self.client = Client()
        
        # Create departments
        self.dept = Dept.objects.create(name="Informatique", id="INFO")
        
        # Create classes
        self.class_obj = Class.objects.create(
            id="INFO2023",
            dept=self.dept,
            section="A",
            sem=3
        )
        
        # Create teacher user without is_teacher property
        self.teacher_user = User.objects.create_user(
            username="teacher1",
            password="password123",
            email="teacher1@example.com"
        )
        
        # Create teacher - this will set is_teacher property on user
        self.teacher = Teacher.objects.create(
            id="TEACHER001",
            name="Prof Smith",
            sex="Male",
            DOB="1980-01-01",
            dept=self.dept,
            user=self.teacher_user
        )
        
        # Create course
        self.course = Course.objects.create(
            id="CS101",
            name="Introduction to Programming",
            shortname="IntroProgram",
            dept=self.dept
        )
        
        # Create assignment
        self.assign = Assign.objects.create(
            class_id=self.class_obj,
            course=self.course,
            teacher=self.teacher
        )
    
    def test_teacher_home_view(self):
        self.client.login(username='teacher1', password='password123')
        response = self.client.get(reverse('t_home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/t_home.html')
        self.assertIn('teacher', response.context)
        self.assertEqual(response.context['teacher'], self.teacher)
    
    def test_teacher_home_view_unauthorized(self):
        # Create a student user
        student_user = User.objects.create_user(
            username="student1",
            password="password123",
            email="student1@example.com"
        )
        
        # Create student to set is_student property
        student = Student.objects.create(
            USN="INFO2023001",
            name="John Doe",
            sex="Male",
            DOB="2000-01-01",
            class_id=self.class_obj,
            user=student_user
        )
        
        # Try to access teacher home with student account
        self.client.login(username='student1', password='password123')
        response = self.client.get(reverse('t_home'))
        self.assertEqual(response.status_code, 302)  # Should redirect or return 403
    
    def test_teacher_home_view_unauthenticated(self):
        response = self.client.get(reverse('t_home'))
        self.assertEqual(response.status_code, 302)  # Redirect to login page


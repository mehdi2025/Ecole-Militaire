from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from info.models import (
    Dept, Class, Student, Teacher, Course, Assign, 
    StudentCourse, AttendanceTotal, Attendance
)

User = get_user_model()

class APIViewsTest(APITestCase):
    def setUp(self):
        # Create test data
        self.client = APIClient()
        
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
            date="2023-01-15",
            status='Present'
        )
        
        # Create tokens for authentication
        self.student_token = Token.objects.create(user=self.student_user)
        self.teacher_token = Token.objects.create(user=self.teacher_user)
    
    def test_detail_view_authenticated(self):
        # Test DetailView with authenticated student
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(reverse('api_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['USN'], self.student.USN)
        self.assertEqual(response.data['data']['name'], self.student.name)
    
    def test_detail_view_unauthenticated(self):
        # Test DetailView without authentication
        response = self.client.get(reverse('api_detail'))
        self.assertEqual(response.status_code, 401)  # Unauthorized
    
    def test_attendance_view_authenticated(self):
        # Test AttendanceView with authenticated student
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(reverse('api_attendance'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(len(response.data['data']), 1)  # Should have one course
        self.assertEqual(response.data['data'][0]['course_name'], self.course.name)
        self.assertEqual(response.data['data'][0]['attendance'], 85)
    
    def test_attendance_view_unauthenticated(self):
        # Test AttendanceView without authentication
        response = self.client.get(reverse('api_attendance'))
        self.assertEqual(response.status_code, 401)  # Unauthorized
    
    def test_attendance_detail_view_authenticated(self):
        # Test AttendanceDetailView with authenticated student
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(reverse('api_attendance_detail', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(len(response.data['data']), 1)  # Should have one attendance record
        self.assertEqual(response.data['data'][0]['date'], '2023-01-15')
        self.assertEqual(response.data['data'][0]['status'], 'Present')
    
    def test_attendance_detail_view_unauthenticated(self):
        # Test AttendanceDetailView without authentication
        response = self.client.get(reverse('api_attendance_detail', args=[self.course.id]))
        self.assertEqual(response.status_code, 401)  # Unauthorized
    
    def test_attendance_detail_view_invalid_course(self):
        # Test AttendanceDetailView with invalid course ID
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(reverse('api_attendance_detail', args=['INVALID']))
        self.assertEqual(response.status_code, 400)  # Bad Request
    
    def test_teacher_detail_view_authenticated(self):
        # Test TeacherDetailView with authenticated teacher
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher_token.key)
        response = self.client.get(reverse('api_teacher_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['id'], self.teacher.id)
        self.assertEqual(response.data['data']['name'], self.teacher.name)
    
    def test_teacher_detail_view_unauthorized(self):
        # Test TeacherDetailView with student (should not be allowed)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(reverse('api_teacher_detail'))
        self.assertEqual(response.status_code, 400)  # Bad Request
    
    def test_teacher_detail_view_unauthenticated(self):
        # Test TeacherDetailView without authentication
        response = self.client.get(reverse('api_teacher_detail'))
        self.assertEqual(response.status_code, 401)  # Unauthorized


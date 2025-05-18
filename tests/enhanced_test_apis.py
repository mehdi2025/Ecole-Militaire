from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from info.models import (
    Dept, Class, Student, Teacher, Course, Assign,
    StudentCourse, AttendanceTotal, Attendance, Marks, MarksClass
)
import uuid
import json

User = get_user_model()

class EnhancedAPIViewsTest(APITestCase):
    def setUp(self):
        # Create test data
        self.client = APIClient()

        # Generate unique identifiers for this test run
        self.unique_id = str(uuid.uuid4())[:8]

        # Create departments
        self.dept, _ = Dept.objects.get_or_create(
            id=f"INFO_{self.unique_id}",
            defaults={"name": f"Informatique_{self.unique_id}"}
        )

        # Create classes
        self.class_obj, _ = Class.objects.get_or_create(
            id=f"INFO2023_{self.unique_id}",
            defaults={
                "dept": self.dept,
                "section": "A",
                "sem": 3
            }
        )

        # Create users without is_student/is_teacher properties
        self.student_user, _ = User.objects.get_or_create(
            username=f"student1_{self.unique_id}",
            defaults={
                "email": f"student1_{self.unique_id}@example.com"
            }
        )
        self.student_user.set_password("password123")
        self.student_user.save()

        self.teacher_user, _ = User.objects.get_or_create(
            username=f"teacher1_{self.unique_id}",
            defaults={
                "email": f"teacher1_{self.unique_id}@example.com"
            }
        )
        self.teacher_user.set_password("password123")
        self.teacher_user.save()

        self.admin_user, _ = User.objects.get_or_create(
            username=f"admin1_{self.unique_id}",
            defaults={
                "email": f"admin1_{self.unique_id}@example.com",
                "is_superuser": True,
                "is_staff": True
            }
        )
        self.admin_user.set_password("password123")
        self.admin_user.save()

        # Create student - this will set is_student property on user
        self.student, _ = Student.objects.get_or_create(
            USN=f"INFO2023001_{self.unique_id}",
            defaults={
                "name": f"John Doe_{self.unique_id}",
                "sex": "Male",
                "DOB": "2000-01-01",
                "class_id": self.class_obj,
                "user": self.student_user
            }
        )

        # Create another student for testing
        self.student_user2, _ = User.objects.get_or_create(
            username=f"student2_{self.unique_id}",
            defaults={
                "email": f"student2_{self.unique_id}@example.com"
            }
        )
        self.student_user2.set_password("password123")
        self.student_user2.save()

        self.student2, _ = Student.objects.get_or_create(
            USN=f"INFO2023002_{self.unique_id}",
            defaults={
                "name": f"Jane Smith_{self.unique_id}",
                "sex": "Female",
                "DOB": "2001-02-15",
                "class_id": self.class_obj,
                "user": self.student_user2
            }
        )

        # Create teacher - this will set is_teacher property on user
        self.teacher, _ = Teacher.objects.get_or_create(
            id=f"TEACHER001_{self.unique_id}",
            defaults={
                "name": f"Prof Smith_{self.unique_id}",
                "sex": "Male",
                "DOB": "1980-01-01",
                "dept": self.dept,
                "user": self.teacher_user
            }
        )

        # Create another teacher for testing
        self.teacher_user2, _ = User.objects.get_or_create(
            username=f"teacher2_{self.unique_id}",
            defaults={
                "email": f"teacher2_{self.unique_id}@example.com"
            }
        )
        self.teacher_user2.set_password("password123")
        self.teacher_user2.save()

        self.teacher2, _ = Teacher.objects.get_or_create(
            id=f"TEACHER002_{self.unique_id}",
            defaults={
                "name": f"Prof Johnson_{self.unique_id}",
                "sex": "Female",
                "DOB": "1985-05-15",
                "dept": self.dept,
                "user": self.teacher_user2
            }
        )

        # Create course
        self.course, _ = Course.objects.get_or_create(
            id=f"CS101_{self.unique_id}",
            defaults={
                "name": f"Introduction to Programming_{self.unique_id}",
                "shortname": f"IntroProgram_{self.unique_id}",
                "dept": self.dept
            }
        )

        # Create another course
        self.course2, _ = Course.objects.get_or_create(
            id=f"CS102_{self.unique_id}",
            defaults={
                "name": f"Data Structures_{self.unique_id}",
                "shortname": f"DataStruct_{self.unique_id}",
                "dept": self.dept
            }
        )

        # Create assignment
        self.assign, _ = Assign.objects.get_or_create(
            class_id=self.class_obj,
            course=self.course,
            defaults={
                "teacher": self.teacher
            }
        )

        # Create another assignment
        self.assign2, _ = Assign.objects.get_or_create(
            class_id=self.class_obj,
            course=self.course2,
            defaults={
                "teacher": self.teacher2
            }
        )

        # Create student course - using get_or_create to avoid duplicates
        self.student_course, _ = StudentCourse.objects.get_or_create(
            student=self.student,
            course=self.course
        )

        # Create another student course
        self.student_course2, _ = StudentCourse.objects.get_or_create(
            student=self.student,
            course=self.course2
        )

        # Create attendance total
        self.attendance_total, _ = AttendanceTotal.objects.get_or_create(
            student=self.student,
            course=self.course,
            defaults={
                "attendance": 85
            }
        )

        # Create another attendance total
        self.attendance_total2, _ = AttendanceTotal.objects.get_or_create(
            student=self.student,
            course=self.course2,
            defaults={
                "attendance": 75
            }
        )

        # Create attendance
        self.attendance, _ = Attendance.objects.get_or_create(
            student=self.student,
            course=self.course,
            date="2023-01-15",
            defaults={
                "status": 'Present'
            }
        )

        # Create another attendance
        self.attendance2, _ = Attendance.objects.get_or_create(
            student=self.student,
            course=self.course,
            date="2023-01-16",
            defaults={
                "status": 'Absent'
            }
        )

        # Create marks class
        self.marks_class, _ = MarksClass.objects.get_or_create(
            assign=self.assign,
            name="Midterm",
            defaults={
                "status": True
            }
        )

        # Create marks
        self.marks, _ = Marks.objects.get_or_create(
            student=self.student,
            marks_class=self.marks_class,
            defaults={
                "marks": 85
            }
        )

        # Create tokens for authentication
        self.student_token, _ = Token.objects.get_or_create(user=self.student_user)
        self.student2_token, _ = Token.objects.get_or_create(user=self.student_user2)
        self.teacher_token, _ = Token.objects.get_or_create(user=self.teacher_user)
        self.teacher2_token, _ = Token.objects.get_or_create(user=self.teacher_user2)
        self.admin_token, _ = Token.objects.get_or_create(user=self.admin_user)

    def test_login_api(self):
        """Test login API with various scenarios"""
        url = reverse('api_login')
        
        # Test with valid credentials
        data = {
            'username': self.student_user.username,
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertIn('user_type', response.data)
        self.assertEqual(response.data['user_type'], 'student')
        
        # Test with teacher credentials
        data = {
            'username': self.teacher_user.username,
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertIn('user_type', response.data)
        self.assertEqual(response.data['user_type'], 'teacher')
        
        # Test with admin credentials
        data = {
            'username': self.admin_user.username,
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertIn('user_type', response.data)
        self.assertEqual(response.data['user_type'], 'admin')
        
        # Test with invalid credentials
        data = {
            'username': self.student_user.username,
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 401)
        
        # Test with missing credentials
        data = {
            'username': self.student_user.username
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        
        data = {
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        
        # Test with empty request
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_student_detail_view(self):
        """Test student detail view with various scenarios"""
        url = reverse('api_detail')
        
        # Test with authenticated student
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['USN'], self.student.USN)
        self.assertEqual(response.data['data']['name'], self.student.name)
        
        # Test with another student
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student2_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['USN'], self.student2.USN)
        self.assertEqual(response.data['data']['name'], self.student2.name)
        
        # Test with teacher (should fail or return teacher data)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher_token.key)
        response = self.client.get(url)
        # Either it returns 400 (bad request) or 200 with teacher data
        if response.status_code == 200:
            self.assertIn('data', response.data)
        else:
            self.assertEqual(response.status_code, 400)
        
        # Test without authentication
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_teacher_detail_view(self):
        """Test teacher detail view with various scenarios"""
        url = reverse('api_teacher_detail')
        
        # Test with authenticated teacher
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['id'], self.teacher.id)
        self.assertEqual(response.data['data']['name'], self.teacher.name)
        
        # Test with another teacher
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher2_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['id'], self.teacher2.id)
        self.assertEqual(response.data['data']['name'], self.teacher2.name)
        
        # Test with student (should fail)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)  # Bad Request
        
        # Test without authentication
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_attendance_view(self):
        """Test attendance view with various scenarios"""
        url = reverse('api_attendance')
        
        # Test with authenticated student
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(len(response.data['data']), 2)  # Should have two courses
        
        # Verify course data
        course_ids = [course['course_id'] for course in response.data['data']]
        self.assertIn(self.course.id, course_ids)
        self.assertIn(self.course2.id, course_ids)
        
        # Test with another student
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student2_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        
        # Test with teacher (should fail)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)  # Bad Request
        
        # Test without authentication
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_attendance_detail_view(self):
        """Test attendance detail view with various scenarios"""
        url = reverse('api_attendance_detail', args=[self.course.id])
        
        # Test with authenticated student
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertEqual(len(response.data['data']), 2)  # Should have two attendance records
        
        # Verify attendance data
        dates = [att['date'] for att in response.data['data']]
        self.assertIn('2023-01-15', dates)
        self.assertIn('2023-01-16', dates)
        
        # Test with invalid course ID
        url = reverse('api_attendance_detail', args=['INVALID'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)  # Bad Request
        
        # Test with course student is not enrolled in
        # First create a new course
        new_course, _ = Course.objects.get_or_create(
            id=f"CS999_{self.unique_id}",
            defaults={
                "name": f"Advanced Topics_{self.unique_id}",
                "shortname": f"AdvTopics_{self.unique_id}",
                "dept": self.dept
            }
        )
        url = reverse('api_attendance_detail', args=[new_course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)  # Bad Request
        
        # Test without authentication
        self.client.credentials()
        url = reverse('api_attendance_detail', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_marks_view(self):
        """Test marks view with various scenarios"""
        url = reverse('api_marks')
        
        # Test with authenticated student
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        
        # Verify marks data
        if len(response.data['data']) > 0:
            course_ids = [mark['course_id'] for mark in response.data['data']]
            self.assertIn(self.course.id, course_ids)
        
        # Test with teacher (should fail)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)  # Bad Request
        
        # Test without authentication
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_marks_detail_view(self):
        """Test marks detail view with various scenarios"""
        url = reverse('api_marks_detail', args=[self.course.id])
        
        # Test with authenticated student
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        
        # Test with invalid course ID
        url = reverse('api_marks_detail', args=['INVALID'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)  # Bad Request
        
        # Test with course student is not enrolled in
        # First create a new course
        new_course, _ = Course.objects.get_or_create(
            id=f"CS999_{self.unique_id}",
            defaults={
                "name": f"Advanced Topics_{self.unique_id}",
                "shortname": f"AdvTopics_{self.unique_id}",
                "dept": self.dept
            }
        )
        url = reverse('api_marks_detail', args=[new_course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)  # Bad Request
        
        # Test without authentication
        self.client.credentials()
        url = reverse('api_marks_detail', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_teacher_attendance_view(self):
        """Test teacher attendance view with various scenarios"""
        url = reverse('api_teacher_attendance')
        
        # Test with authenticated teacher
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        
        # Verify course data
        if len(response.data['data']) > 0:
            course_ids = [course['course_id'] for course in response.data['data']]
            self.assertIn(self.course.id, course_ids)
        
        # Test with student (should fail)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)  # Bad Request
        
        # Test without authentication
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_teacher_attendance_detail_view(self):
        """Test teacher attendance detail view with various scenarios"""
        url = reverse('api_teacher_attendance_detail', args=[self.course.id])
        
        # Test with authenticated teacher
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        
        # Test with invalid course ID
        url = reverse('api_teacher_attendance_detail', args=['INVALID'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)  # Bad Request
        
        # Test with course teacher is not assigned to
        # Test with teacher2 trying to access course1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher2_token.key)
        url = reverse('api_teacher_attendance_detail', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)  # Bad Request
        
        # Test without authentication
        self.client.credentials()
        url = reverse('api_teacher_attendance_detail', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_teacher_marks_view(self):
        """Test teacher marks view with various scenarios"""
        url = reverse('api_teacher_marks')
        
        # Test with authenticated teacher
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        
        # Verify course data
        if len(response.data['data']) > 0:
            course_ids = [course['course_id'] for course in response.data['data']]
            self.assertIn(self.course.id, course_ids)
        
        # Test with student (should fail)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)  # Bad Request
        
        # Test without authentication
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_teacher_marks_detail_view(self):
        """Test teacher marks detail view with various scenarios"""
        url = reverse('api_teacher_marks_detail', args=[self.course.id])
        
        # Test with authenticated teacher
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        
        # Test with invalid course ID
        url = reverse('api_teacher_marks_detail', args=['INVALID'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)  # Bad Request
        
        # Test with course teacher is not assigned to
        # Test with teacher2 trying to access course1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher2_token.key)
        url = reverse('api_teacher_marks_detail', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)  # Bad Request
        
        # Test without authentication
        self.client.credentials()
        url = reverse('api_teacher_marks_detail', args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_teacher_timetable_view(self):
        """Test teacher timetable view with various scenarios"""
        url = reverse('api_teacher_timetable')
        
        # Test with authenticated teacher
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        
        # Test with student (should fail)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)  # Bad Request
        
        # Test without authentication
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_student_timetable_view(self):
        """Test student timetable view with various scenarios"""
        url = reverse('api_student_timetable')
        
        # Test with authenticated student
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        
        # Test with teacher (should fail)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)  # Bad Request
        
        # Test without authentication
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_admin_student_list_view(self):
        """Test admin student list view with various scenarios"""
        url = reverse('api_admin_student_list')
        
        # Test with authenticated admin
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertGreaterEqual(len(response.data['data']), 2)  # At least our 2 test students
        
        # Test with teacher (should fail)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test with student (should fail)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test without authentication
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_admin_teacher_list_view(self):
        """Test admin teacher list view with various scenarios"""
        url = reverse('api_admin_teacher_list')
        
        # Test with authenticated admin
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertGreaterEqual(len(response.data['data']), 2)  # At least our 2 test teachers
        
        # Test with teacher (should fail)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test with student (should fail)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test without authentication
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_admin_course_list_view(self):
        """Test admin course list view with various scenarios"""
        url = reverse('api_admin_course_list')
        
        # Test with authenticated admin
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertGreaterEqual(len(response.data['data']), 2)  # At least our 2 test courses
        
        # Test with teacher (should fail)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test with student (should fail)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test without authentication
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_admin_class_list_view(self):
        """Test admin class list view with various scenarios"""
        url = reverse('api_admin_class_list')
        
        # Test with authenticated admin
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertGreaterEqual(len(response.data['data']), 1)  # At least our test class
        
        # Test with teacher (should fail)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test with student (should fail)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test without authentication
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_admin_department_list_view(self):
        """Test admin department list view with various scenarios"""
        url = reverse('api_admin_dept_list')
        
        # Test with authenticated admin
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.data)
        self.assertGreaterEqual(len(response.data['data']), 1)  # At least our test department
        
        # Test with teacher (should fail)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.teacher_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test with student (should fail)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.student_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test without authentication
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)  # Unauthorized


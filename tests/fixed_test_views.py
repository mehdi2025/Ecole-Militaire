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
import uuid

User = get_user_model()

class InfoViewsTest(TestCase):
    def setUp(self):
        # Create test data
        self.client = Client()
        
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
                "is_superuser": True
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

        # Create course
        self.course, _ = Course.objects.get_or_create(
            id=f"CS101_{self.unique_id}",
            defaults={
                "name": f"Introduction to Programming_{self.unique_id}",
                "shortname": f"IntroProgram_{self.unique_id}",
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

        # Create student course - using get_or_create to avoid duplicates
        self.student_course, _ = StudentCourse.objects.get_or_create(
            student=self.student,
            course=self.course
        )

        # Create attendance total
        self.attendance_total, _ = AttendanceTotal.objects.get_or_create(
            student=self.student,
            course=self.course,
            defaults={
                "attendance": 85
            }
        )

        # Create attendance with today's date
        today = timezone.now().date()
        self.attendance, _ = Attendance.objects.get_or_create(
            student=self.student,
            course=self.course,
            date=today,
            defaults={
                "status": 'Present'
            }
        )

    def test_index_view_student(self):
        self.client.login(username=self.student_user.username, password='password123')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/homepage.html')

    def test_index_view_teacher(self):
        self.client.login(username=self.teacher_user.username, password='password123')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/t_homepage.html')

    def test_index_view_admin(self):
        self.client.login(username=self.admin_user.username, password='password123')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/admin_page.html')

    def test_index_view_unauthenticated(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302)  # Redirect to login page

    def test_attendance_view(self):
        self.client.login(username=self.student_user.username, password='password123')
        response = self.client.get(reverse('attendance', args=[self.student.USN]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/attendance.html')
        self.assertIn('att_list', response.context)
        self.assertEqual(len(response.context['att_list']), 1)

    def test_attendance_detail_view(self):
        self.client.login(username=self.student_user.username, password='password123')
        response = self.client.get(reverse('attendance_detail', args=[self.student.USN, self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/att_detail.html')
        self.assertIn('att_list', response.context)
        self.assertEqual(len(response.context['att_list']), 1)
        self.assertIn('cr', response.context)
        self.assertEqual(response.context['cr'], self.course)

    def test_attendance_view_unauthorized(self):
        # Test that a teacher cannot access a student's attendance
        self.client.login(username=self.teacher_user.username, password='password123')
        response = self.client.get(reverse('attendance', args=[self.student.USN]))
        self.assertEqual(response.status_code, 302)  # Should redirect or return 403

    def test_attendance_detail_view_nonexistent(self):
        self.client.login(username=self.student_user.username, password='password123')
        response = self.client.get(reverse('attendance_detail', args=[self.student.USN, 'NONEXISTENT']))
        self.assertEqual(response.status_code, 404)  # Should return 404 for non-existent course

class TeacherViewsTest(TestCase):
    def setUp(self):
        # Create test data
        self.client = Client()
        
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

        # Create teacher user without is_teacher property
        self.teacher_user, _ = User.objects.get_or_create(
            username=f"teacher1_{self.unique_id}",
            defaults={
                "email": f"teacher1_{self.unique_id}@example.com"
            }
        )
        self.teacher_user.set_password("password123")
        self.teacher_user.save()

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

        # Create course
        self.course, _ = Course.objects.get_or_create(
            id=f"CS101_{self.unique_id}",
            defaults={
                "name": f"Introduction to Programming_{self.unique_id}",
                "shortname": f"IntroProgram_{self.unique_id}",
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

    def test_teacher_home_view(self):
        self.client.login(username=self.teacher_user.username, password='password123')
        response = self.client.get(reverse('t_home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/t_home.html')
        self.assertIn('teacher', response.context)
        self.assertEqual(response.context['teacher'], self.teacher)

    def test_teacher_home_view_unauthorized(self):
        # Create a student user with unique identifier
        student_user, _ = User.objects.get_or_create(
            username=f"student1_{self.unique_id}",
            defaults={
                "email": f"student1_{self.unique_id}@example.com"
            }
        )
        student_user.set_password("password123")
        student_user.save()

        # Create student to set is_student property
        student, _ = Student.objects.get_or_create(
            USN=f"INFO2023001_{self.unique_id}",
            defaults={
                "name": f"John Doe_{self.unique_id}",
                "sex": "Male",
                "DOB": "2000-01-01",
                "class_id": self.class_obj,
                "user": student_user
            }
        )

        # Try to access teacher home with student account
        self.client.login(username=student_user.username, password='password123')
        response = self.client.get(reverse('t_home'))
        self.assertEqual(response.status_code, 302)  # Should redirect or return 403

    def test_teacher_home_view_unauthenticated(self):
        response = self.client.get(reverse('t_home'))
        self.assertEqual(response.status_code, 302)  # Redirect to login page


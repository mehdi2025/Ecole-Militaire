from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from info.models import (
    Dept, Class, Student, Teacher, Course, Assign,
    AssignTime, AttendanceClass, Attendance, AttendanceTotal,
    StudentCourse, Marks, MarksClass, AttendanceRange
)
from django.utils import timezone
from datetime import timedelta, date
import uuid
import json

User = get_user_model()

class EnhancedInfoViewsTest(TestCase):
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
                "teacher": self.teacher
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

        # Create attendance for yesterday
        yesterday = today - timedelta(days=1)
        self.attendance_yesterday, _ = Attendance.objects.get_or_create(
            student=self.student,
            course=self.course,
            date=yesterday,
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

        # Create attendance class
        self.attendance_class, _ = AttendanceClass.objects.get_or_create(
            assign=self.assign,
            date=today,
            defaults={
                "status": True
            }
        )

        # Create attendance range
        self.attendance_range, _ = AttendanceRange.objects.get_or_create(
            start_date=today - timedelta(days=30),
            end_date=today
        )

    def test_student_dashboard(self):
        """Test student dashboard view"""
        self.client.login(username=self.student_user.username, password='password123')
        response = self.client.get(reverse('student_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/student_dashboard.html')
        self.assertIn('student', response.context)
        self.assertEqual(response.context['student'], self.student)

    def test_teacher_dashboard(self):
        """Test teacher dashboard view"""
        self.client.login(username=self.teacher_user.username, password='password123')
        response = self.client.get(reverse('teacher_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/teacher_dashboard.html')
        self.assertIn('teacher', response.context)
        self.assertEqual(response.context['teacher'], self.teacher)

    def test_admin_dashboard(self):
        """Test admin dashboard view"""
        self.client.login(username=self.admin_user.username, password='password123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/admin_dashboard.html')

    def test_student_marks_list(self):
        """Test student marks list view"""
        self.client.login(username=self.student_user.username, password='password123')
        response = self.client.get(reverse('marks_list', args=[self.student.USN]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/marks_list.html')
        self.assertIn('marks_list', response.context)
        self.assertEqual(len(response.context['marks_list']), 1)

    def test_teacher_marks_list(self):
        """Test teacher marks list view"""
        self.client.login(username=self.teacher_user.username, password='password123')
        response = self.client.get(reverse('t_marks_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/t_marks_list.html')
        self.assertIn('teacher', response.context)
        self.assertEqual(response.context['teacher'], self.teacher)

    def test_add_marks(self):
        """Test add marks view"""
        self.client.login(username=self.teacher_user.username, password='password123')
        response = self.client.get(reverse('add_marks', args=[self.assign.id, self.marks_class.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/add_marks.html')
        self.assertIn('students', response.context)
        
        # Test POST request to add marks
        post_data = {
            f'marks_{self.student.USN}': 90
        }
        response = self.client.post(reverse('add_marks', args=[self.assign.id, self.marks_class.id]), post_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful submission
        
        # Verify marks were updated
        updated_marks = Marks.objects.get(student=self.student, marks_class=self.marks_class)
        self.assertEqual(updated_marks.marks, 90)

    def test_add_marks_class(self):
        """Test add marks class view"""
        self.client.login(username=self.teacher_user.username, password='password123')
        response = self.client.get(reverse('t_add_marks_class', args=[self.assign.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/t_add_marks_class.html')
        
        # Test POST request to add marks class
        post_data = {
            'name': 'Final Exam',
            'status': 'True'
        }
        response = self.client.post(reverse('t_add_marks_class', args=[self.assign.id]), post_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful submission
        
        # Verify marks class was created
        self.assertTrue(MarksClass.objects.filter(assign=self.assign, name='Final Exam').exists())

    def test_edit_marks_class(self):
        """Test edit marks class view"""
        self.client.login(username=self.teacher_user.username, password='password123')
        response = self.client.get(reverse('t_edit_marks_class', args=[self.marks_class.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/t_edit_marks_class.html')
        
        # Test POST request to edit marks class
        post_data = {
            'name': 'Updated Midterm',
            'status': 'True'
        }
        response = self.client.post(reverse('t_edit_marks_class', args=[self.marks_class.id]), post_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful submission
        
        # Verify marks class was updated
        updated_marks_class = MarksClass.objects.get(id=self.marks_class.id)
        self.assertEqual(updated_marks_class.name, 'Updated Midterm')

    def test_teacher_attendance_list(self):
        """Test teacher attendance list view"""
        self.client.login(username=self.teacher_user.username, password='password123')
        response = self.client.get(reverse('t_attendance_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/t_attendance_list.html')
        self.assertIn('teacher', response.context)
        self.assertEqual(response.context['teacher'], self.teacher)

    def test_add_attendance_class(self):
        """Test add attendance class view"""
        self.client.login(username=self.teacher_user.username, password='password123')
        response = self.client.get(reverse('t_add_attendance', args=[self.assign.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/t_add_attendance.html')
        
        # Test POST request to add attendance class
        tomorrow = timezone.now().date() + timedelta(days=1)
        post_data = {
            'date': tomorrow.strftime('%Y-%m-%d'),
            'status': 'True'
        }
        response = self.client.post(reverse('t_add_attendance', args=[self.assign.id]), post_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful submission
        
        # Verify attendance class was created
        self.assertTrue(AttendanceClass.objects.filter(assign=self.assign, date=tomorrow).exists())

    def test_edit_attendance_class(self):
        """Test edit attendance class view"""
        self.client.login(username=self.teacher_user.username, password='password123')
        response = self.client.get(reverse('t_edit_attendance', args=[self.attendance_class.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/t_edit_attendance.html')
        
        # Test POST request to edit attendance class
        post_data = {
            'status': 'False'
        }
        response = self.client.post(reverse('t_edit_attendance', args=[self.attendance_class.id]), post_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful submission
        
        # Verify attendance class was updated
        updated_attendance_class = AttendanceClass.objects.get(id=self.attendance_class.id)
        self.assertEqual(updated_attendance_class.status, False)

    def test_mark_attendance(self):
        """Test mark attendance view"""
        self.client.login(username=self.teacher_user.username, password='password123')
        response = self.client.get(reverse('t_mark_attendance', args=[self.attendance_class.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/t_mark_attendance.html')
        self.assertIn('students', response.context)
        
        # Test POST request to mark attendance
        post_data = {
            f'status_{self.student.USN}': 'Absent'
        }
        response = self.client.post(reverse('t_mark_attendance', args=[self.attendance_class.id]), post_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful submission
        
        # Verify attendance was updated
        updated_attendance = Attendance.objects.get(student=self.student, date=self.attendance_class.date, course=self.attendance_class.assign.course)
        self.assertEqual(updated_attendance.status, 'Absent')

    def test_student_timetable(self):
        """Test student timetable view"""
        # Create assign time for testing
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        periods = [1, 2, 3, 4, 5, 6, 7, 8]
        
        # Create assign time for Monday period 1
        assign_time, _ = AssignTime.objects.get_or_create(
            assign=self.assign,
            period=1,
            day='Monday'
        )
        
        self.client.login(username=self.student_user.username, password='password123')
        response = self.client.get(reverse('timetable', args=[self.class_obj.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/timetable.html')
        self.assertIn('class_obj', response.context)
        self.assertEqual(response.context['class_obj'], self.class_obj)
        self.assertIn('monday_timetable', response.context)
        self.assertEqual(len(response.context['monday_timetable']), 8)  # 8 periods
        
        # Verify the course appears in the correct period
        self.assertEqual(response.context['monday_timetable'][0]['course'], self.course)

    def test_teacher_timetable(self):
        """Test teacher timetable view"""
        # Create assign time for testing
        assign_time, _ = AssignTime.objects.get_or_create(
            assign=self.assign,
            period=1,
            day='Monday'
        )
        
        self.client.login(username=self.teacher_user.username, password='password123')
        response = self.client.get(reverse('t_timetable', args=[self.teacher.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/t_timetable.html')
        self.assertIn('teacher', response.context)
        self.assertEqual(response.context['teacher'], self.teacher)
        self.assertIn('monday_timetable', response.context)
        self.assertEqual(len(response.context['monday_timetable']), 8)  # 8 periods
        
        # Verify the course appears in the correct period
        self.assertEqual(response.context['monday_timetable'][0]['course'], self.course)

    def test_teacher_assign_time(self):
        """Test teacher assign time view"""
        self.client.login(username=self.teacher_user.username, password='password123')
        response = self.client.get(reverse('t_add_timetable', args=[self.assign.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/t_add_timetable.html')
        
        # Test POST request to add assign time
        post_data = {
            'day': 'Tuesday',
            'period': '2'
        }
        response = self.client.post(reverse('t_add_timetable', args=[self.assign.id]), post_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful submission
        
        # Verify assign time was created
        self.assertTrue(AssignTime.objects.filter(assign=self.assign, day='Tuesday', period=2).exists())

    def test_admin_student_list(self):
        """Test admin student list view"""
        self.client.login(username=self.admin_user.username, password='password123')
        response = self.client.get(reverse('admin_student_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/admin_student_list.html')
        self.assertIn('students', response.context)
        self.assertGreaterEqual(len(response.context['students']), 2)  # At least our 2 test students

    def test_admin_teacher_list(self):
        """Test admin teacher list view"""
        self.client.login(username=self.admin_user.username, password='password123')
        response = self.client.get(reverse('admin_teacher_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/admin_teacher_list.html')
        self.assertIn('teachers', response.context)
        self.assertGreaterEqual(len(response.context['teachers']), 1)  # At least our test teacher

    def test_admin_add_student(self):
        """Test admin add student view"""
        self.client.login(username=self.admin_user.username, password='password123')
        response = self.client.get(reverse('admin_add_student'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/admin_add_student.html')
        
        # Test POST request to add student
        post_data = {
            'username': f'new_student_{self.unique_id}',
            'password': 'password123',
            'name': f'New Student_{self.unique_id}',
            'USN': f'INFO2023003_{self.unique_id}',
            'class_id': self.class_obj.id,
            'sex': 'Male',
            'DOB': '2002-03-15'
        }
        response = self.client.post(reverse('admin_add_student'), post_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful submission
        
        # Verify student was created
        self.assertTrue(Student.objects.filter(USN=f'INFO2023003_{self.unique_id}').exists())
        self.assertTrue(User.objects.filter(username=f'new_student_{self.unique_id}').exists())

    def test_admin_add_teacher(self):
        """Test admin add teacher view"""
        self.client.login(username=self.admin_user.username, password='password123')
        response = self.client.get(reverse('admin_add_teacher'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/admin_add_teacher.html')
        
        # Test POST request to add teacher
        post_data = {
            'username': f'new_teacher_{self.unique_id}',
            'password': 'password123',
            'name': f'New Teacher_{self.unique_id}',
            'id': f'TEACHER002_{self.unique_id}',
            'dept': self.dept.id,
            'sex': 'Female',
            'DOB': '1985-05-20'
        }
        response = self.client.post(reverse('admin_add_teacher'), post_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful submission
        
        # Verify teacher was created
        self.assertTrue(Teacher.objects.filter(id=f'TEACHER002_{self.unique_id}').exists())
        self.assertTrue(User.objects.filter(username=f'new_teacher_{self.unique_id}').exists())

    def test_admin_add_course(self):
        """Test admin add course view"""
        self.client.login(username=self.admin_user.username, password='password123')
        response = self.client.get(reverse('admin_add_course'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/admin_add_course.html')
        
        # Test POST request to add course
        post_data = {
            'name': f'Advanced Programming_{self.unique_id}',
            'id': f'CS103_{self.unique_id}',
            'shortname': f'AdvProg_{self.unique_id}',
            'dept': self.dept.id
        }
        response = self.client.post(reverse('admin_add_course'), post_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful submission
        
        # Verify course was created
        self.assertTrue(Course.objects.filter(id=f'CS103_{self.unique_id}').exists())

    def test_admin_add_class(self):
        """Test admin add class view"""
        self.client.login(username=self.admin_user.username, password='password123')
        response = self.client.get(reverse('admin_add_class'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/admin_add_class.html')
        
        # Test POST request to add class
        post_data = {
            'id': f'INFO2024_{self.unique_id}',
            'dept': self.dept.id,
            'section': 'B',
            'sem': 4
        }
        response = self.client.post(reverse('admin_add_class'), post_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful submission
        
        # Verify class was created
        self.assertTrue(Class.objects.filter(id=f'INFO2024_{self.unique_id}').exists())

    def test_admin_assign_course(self):
        """Test admin assign course view"""
        self.client.login(username=self.admin_user.username, password='password123')
        response = self.client.get(reverse('admin_assign_course'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/admin_assign_course.html')
        
        # Test POST request to assign course
        post_data = {
            'class_id': self.class_obj.id,
            'course': self.course.id,
            'teacher': self.teacher.id
        }
        response = self.client.post(reverse('admin_assign_course'), post_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful submission
        
        # Verify assign was created (or exists)
        self.assertTrue(Assign.objects.filter(class_id=self.class_obj, course=self.course, teacher=self.teacher).exists())

    def test_password_reset(self):
        """Test password reset view"""
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/password_reset.html')
        
        # Test POST request for password reset
        post_data = {
            'username': self.student_user.username
        }
        response = self.client.post(reverse('password_reset'), post_data)
        self.assertEqual(response.status_code, 200)  # Success page
        self.assertTemplateUsed(response, 'info/password_reset_done.html')

    def test_student_attendance_report(self):
        """Test student attendance report view"""
        self.client.login(username=self.student_user.username, password='password123')
        
        # Create attendance range for testing
        today = timezone.now().date()
        start_date = today - timedelta(days=30)
        end_date = today
        
        response = self.client.get(reverse('attendance_report', args=[self.student.USN]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/attendance_report.html')
        
        # Test POST request for attendance report
        post_data = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }
        response = self.client.post(reverse('attendance_report', args=[self.student.USN]), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/attendance_report.html')
        self.assertIn('att_list', response.context)
        
        # Verify attendance range was created
        self.assertTrue(AttendanceRange.objects.filter(start_date=start_date, end_date=end_date).exists())

    def test_teacher_class_list(self):
        """Test teacher class list view"""
        self.client.login(username=self.teacher_user.username, password='password123')
        response = self.client.get(reverse('t_class_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/t_class_list.html')
        self.assertIn('class_list', response.context)
        self.assertGreaterEqual(len(response.context['class_list']), 1)  # At least our test class

    def test_student_class_list(self):
        """Test student class list view"""
        self.client.login(username=self.student_user.username, password='password123')
        response = self.client.get(reverse('s_class_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/s_class_list.html')
        self.assertIn('class_list', response.context)
        self.assertEqual(len(response.context['class_list']), 1)  # Our test class

    def test_teacher_student_list(self):
        """Test teacher student list view"""
        self.client.login(username=self.teacher_user.username, password='password123')
        response = self.client.get(reverse('t_student_list', args=[self.assign.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info/t_student_list.html')
        self.assertIn('students', response.context)
        self.assertGreaterEqual(len(response.context['students']), 1)  # At least our test student

    def test_error_handling(self):
        """Test error handling for non-existent resources"""
        self.client.login(username=self.admin_user.username, password='password123')
        
        # Test non-existent student
        response = self.client.get(reverse('attendance', args=['NONEXISTENT']))
        self.assertEqual(response.status_code, 404)
        
        # Test non-existent teacher
        response = self.client.get(reverse('t_timetable', args=['NONEXISTENT']))
        self.assertEqual(response.status_code, 404)
        
        # Test non-existent class
        response = self.client.get(reverse('timetable', args=['NONEXISTENT']))
        self.assertEqual(response.status_code, 404)
        
        # Test non-existent course
        response = self.client.get(reverse('attendance_detail', args=[self.student.USN, 'NONEXISTENT']))
        self.assertEqual(response.status_code, 404)

    def test_permission_handling(self):
        """Test permission handling for unauthorized access"""
        # Student trying to access teacher views
        self.client.login(username=self.student_user.username, password='password123')
        response = self.client.get(reverse('t_home'))
        self.assertEqual(response.status_code, 302)  # Redirect to login or permission denied
        
        # Teacher trying to access admin views
        self.client.login(username=self.teacher_user.username, password='password123')
        response = self.client.get(reverse('admin_add_student'))
        self.assertEqual(response.status_code, 302)  # Redirect to login or permission denied
        
        # Student trying to access another student's data
        self.client.login(username=self.student_user.username, password='password123')
        response = self.client.get(reverse('attendance', args=[self.student2.USN]))
        self.assertEqual(response.status_code, 302)  # Redirect to login or permission denied


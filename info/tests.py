from django.test import TestCase
from info.models import Dept, Class, Course, User, Student, Teacher, Assign, AssignTime, AttendanceTotal, Attendance, StudentCourse, Marks, MarksClass
from django.urls import reverse
from django.test.client import Client
from django.db.utils import IntegrityError # Import IntegrityError for potential try-except blocks if needed

# Create your tests here.

class InfoTest(TestCase):

    # --- START: Corrected Helper Methods for Dependency Management ---
    def create_user(self, username='testuser', email='test@test.com', password='test_password', is_staff=False, is_superuser=False):
        # Ensure user creation is robust and handles potential duplicates in tests
        user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'password': password})
        if created: # Only set password if user was just created
            user.set_password(password)
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save()
        return user

    def create_dept(self, id='CS', name='Computer Science'):
        return Dept.objects.get_or_create(id=id, defaults={'name': name})[0] # Use get_or_create to avoid duplicates

    def create_class(self, id='CS5A', sem=5, section='A', dept_id='CS'):
        # Ensure department exists before creating class
        dept = self.create_dept(id=dept_id) # Use the helper to get/create department
        return Class.objects.get_or_create(id=id, defaults={'dept': dept, 'sem': sem, 'section': section})[0]

    def create_course(self, id='CS510', name='Data Structures', shortname='DS', dept_id='CS'):
        # Ensure department exists before creating course
        dept = self.create_dept(id=dept_id) # Use the helper to get/create department
        return Course.objects.get_or_create(id=id, defaults={'dept': dept, 'name': name, 'shortname': shortname})[0]

    def create_student(self, usn='STU001', name='Student Name', username='studentuser', class_id='CS5A'):
        user = self.create_user(username=username, email=f'{username}@example.com')
        # Ensure class exists before creating student
        cl = self.create_class(id=class_id) # Use the helper to get/create class
        return Student.objects.get_or_create(user=user, USN=usn, defaults={'name': name, 'class_id': cl})[0]

    def create_teacher(self, id='TCH001', name='Teacher Name', username='teacheruser', dept_id='CS'):
        user = self.create_user(username=username, email=f'{username}@example.com')
        # Ensure department exists before creating teacher
        dept = self.create_dept(id=dept_id) # Use the helper to get/create department
        return Teacher.objects.get_or_create(user=user, id=id, defaults={'name': name, 'dept': dept})[0]

    def create_assign(self, class_id='CS5A', course_id='CS510', teacher_obj=None, teacher_id='TCH001'):
        cl = self.create_class(id=class_id)
        cr = self.create_course(id=course_id)
        
        if teacher_obj is None:
            t = self.create_teacher(id=teacher_id)
        else:
            t = teacher_obj # Use the provided teacher object

        return Assign.objects.get_or_create(class_id=cl, course=cr, teacher=t)[0]

    # ... (rest of your InfoTest class) ...


    def create_attendance_class(self, assign_obj=None, class_id='CS5A', course_id='CS510', teacher_id='TCH001', date='2025-01-01'):
        # If assign_obj is not provided, create one
        if assign_obj is None:
            assign_obj = self.create_assign(class_id=class_id, course_id=course_id, teacher_id=teacher_id)
        # Assuming AttendanceClass needs an 'assign' and a 'date' field
        return AttendanceClass.objects.get_or_create(assign=assign_obj, date=date)[0]
    # --- END: Corrected Helper Methods ---

    # Test cases

    def test_user_creation(self):
        # Use the robust create_user helper
        us = self.create_user(username='student_user_test', email='student_test@example.com')
        ut = self.create_user(username='teacher_user_test', email='teacher_test@example.com')

        # Use the robust create_class and create_dept helpers
        cl = self.create_class(id='CS01_CLASS_TEST')
        dept = self.create_dept(id='CS01_DEPT_TEST')

        # Create Student and Teacher instances using the created users and dependencies
        s = Student.objects.create(user=us, USN='CS01_TEST', name='test_student_user_creation', class_id=cl)
        t = Teacher.objects.create(user=ut, id='TCH01_TEST', name='test_teacher_user_creation', dept=dept)

        self.assertTrue(isinstance(us, User))
        self.assertTrue(isinstance(ut, User))
        self.assertEqual(s.user, us)
        self.assertEqual(t.user, ut)
        self.assertTrue(hasattr(us, 'student'))
        self.assertTrue(hasattr(ut, 'teacher'))

    def test_dept_creation(self):
        d = self.create_dept()
        self.assertTrue(isinstance(d, Dept))
        self.assertEqual(str(d), d.name)

    def test_class_creation(self):
        c = self.create_class()
        self.assertTrue(isinstance(c, Class))
        self.assertEqual(str(c), "%s : %d %s" % (c.dept.name, c.sem, c.section))

    def test_course_creation(self):
        c = self.create_course()
        self.assertTrue(isinstance(c, Course))
        self.assertEqual(str(c), c.name)

    def test_student_creation(self):
        s = self.create_student()
        self.assertTrue(isinstance(s, Student))
        self.assertEqual(str(s), s.name)

    def test_teacher_creation(self):
        t = self.create_teacher()
        self.assertTrue(isinstance(t, Teacher))
        self.assertEqual(str(t), t.name)

    def test_assign_creation(self):
        a = self.create_assign()
        self.assertTrue(isinstance(a, Assign))

    # views
    def setUp(self):
        # This setUp runs before every test method.
        self.client = Client()
        # Create users and their profiles using the robust helper methods
        self.admin_user = self.create_user('admin_user_setup', 'admin_setup@example.com', 'admin_password', is_staff=True, is_superuser=True)
        self.student_user = self.create_user('student_user_setup', 'student_setup@example.com', 'student_password')
        self.teacher_user = self.create_user('teacher_user_setup', 'teacher_setup@example.com', 'teacher_password')

        # Create associated profiles for student and teacher users
        self.student_profile = self.create_student(username='student_user_setup', usn='STU001_SETUP', name='Test Student Setup')
        self.teacher_profile = self.create_teacher(username='teacher_user_setup', id='TCH001_SETUP', name='Test Teacher Setup')

    def test_index_admin(self):
        self.client.login(username='admin_user_setup', password='admin_password')
        response = self.client.get(reverse('index'))
        self.assertContains(response, "Welcome") # Assuming a welcome message for admin
        self.assertEqual(response.status_code, 200)

    def test_index_student(self):
        self.client.login(username='student_user_setup', password='student_password')
        response = self.client.get(reverse('index'))
        self.assertContains(response, self.student_profile.name)
        self.assertEqual(response.status_code, 200)

    def test_index_teacher(self):
        self.client.login(username='teacher_user_setup', password='teacher_password')
        response = self.client.get(reverse('index'))
        self.assertContains(response, self.teacher_profile.name)
        self.assertEqual(response.status_code, 200)

    def test_no_attendance(self):
        s = self.student_profile
        self.client.login(username='student_user_setup', password='student_password')
        response = self.client.get(reverse('attendance', args=(s.USN,)))
        self.assertContains(response, "student has no courses")
        self.assertEqual(response.status_code, 200)

    def test_attendance_view(self):
        s = self.student_profile
        self.client.login(username='student_user_setup', password='student_password')

        cl = s.class_id
        cr = self.create_course(id='MATH101_TEST', name='Mathematics Test', shortname='MATH_T')
        t = self.teacher_profile

        Assign.objects.create(class_id=cl, course=cr, teacher=t)

        response = self.client.get(reverse('attendance', args=(s.USN,)))
        self.assertEqual(response.status_code, 200)
        # Corrected typo: assertQuerySetEqual
        self.assertQuerySetEqual(response.context['att_list'], ['<AttendanceTotal: AttendanceTotal object (1)>'])

    def test_no_attendance__detail(self):
        s = self.student_profile
        cr = self.create_course(id='PHY101_TEST', name='Physics Test', shortname='PHY_T')
        self.client.login(username='student_user_setup', password='student_password')
        resp = self.client.get(reverse('attendance_detail', args=(s.USN, cr.id)))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "student has no attendance")

    def test_attendance__detail(self):
        s = self.student_profile
        cr = self.create_course(id='CHEM101_TEST', name='Chemistry Test', shortname='CHEM_T')

        # Pass the existing teacher_profile object directly
        assign = self.create_assign(
            class_id=s.class_id.id,
            course_id=cr.id,
            teacher_obj=self.teacher_profile # Pass the object here
        )
        att_class = self.create_attendance_class(assign_obj=assign, date='2025-06-29')

        Attendance.objects.create(student=s, course=cr, attendanceClass=att_class)

        self.client.login(username='student_user_setup', password='student_password')
        resp = self.client.get(reverse('attendance_detail', args=(s.USN, cr.id)))
        self.assertEqual(resp.status_code, 200)
        self.assertQuerySetEqual(resp.context['att_list'], ['<Attendance: ' + s.name + ' : ' + cr.shortname + '>'])

    # teacher views (uncomment and fix as needed)
    # def test_attendance_class(self):
    #     t = self.teacher_profile
    #     self.client.login(username='teacher_user_setup', password='teacher_password')
    #
    #     cl = self.create_class(id='CLASS_TCH_TEST', sem=1, section='A', dept_id=t.dept.id)
    #     cr = self.create_course(id='COURSE_TCH_TEST', dept_id=t.dept.id)
    #     Assign.objects.create(teacher=t, class_id=cl, course=cr)
    #
    #     resp = self.client.get(reverse('t_clas', args=(t.id, 1)))
    #     self.assertEqual(resp.status_code, 200)
    #     self.assertContains(resp, "Enter Attendance")

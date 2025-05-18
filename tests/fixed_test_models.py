import unittest
from django.test import TestCase
from django.contrib.auth import get_user_model
from info.models import (
    Dept, Class, Student, Teacher, Course, Assign,
    AssignTime, AttendanceClass, Attendance, AttendanceTotal,
    StudentCourse, Marks, MarksClass, AttendanceRange
)
from django.utils import timezone
from datetime import timedelta, date
from django.core.exceptions import ValidationError
import uuid

User = get_user_model()

class DeptModelTest(TestCase):
    def setUp(self):
        # Generate unique identifier for this test run
        self.unique_id = str(uuid.uuid4())[:8]
        
        self.dept, _ = Dept.objects.get_or_create(
            id=f"INFO_{self.unique_id}",
            defaults={"name": f"Informatique_{self.unique_id}"}
        )

    def test_dept_creation(self):
        self.assertTrue(self.dept.name.startswith("Informatique_"))
        self.assertTrue(self.dept.id.startswith("INFO_"))
        self.assertEqual(str(self.dept), self.dept.name)

class ClassModelTest(TestCase):
    def setUp(self):
        # Generate unique identifier for this test run
        self.unique_id = str(uuid.uuid4())[:8]
        
        self.dept, _ = Dept.objects.get_or_create(
            id=f"INFO_{self.unique_id}",
            defaults={"name": f"Informatique_{self.unique_id}"}
        )
        
        self.class_obj, _ = Class.objects.get_or_create(
            id=f"INFO2023_{self.unique_id}",
            defaults={
                "dept": self.dept,
                "section": "A",
                "sem": 3
            }
        )

    def test_class_creation(self):
        self.assertTrue(self.class_obj.id.startswith("INFO2023_"))
        self.assertEqual(self.class_obj.dept, self.dept)
        self.assertEqual(self.class_obj.section, "A")
        self.assertEqual(self.class_obj.sem, 3)
        # Check string representation format
        self.assertEqual(str(self.class_obj), f"{self.dept.name} : 3 A")

class StudentModelTest(TestCase):
    def setUp(self):
        # Generate unique identifier for this test run
        self.unique_id = str(uuid.uuid4())[:8]
        
        self.dept, _ = Dept.objects.get_or_create(
            id=f"INFO_{self.unique_id}",
            defaults={"name": f"Informatique_{self.unique_id}"}
        )
        
        self.class_obj, _ = Class.objects.get_or_create(
            id=f"INFO2023_{self.unique_id}",
            defaults={
                "dept": self.dept,
                "section": "A",
                "sem": 3
            }
        )
        
        # Create user without is_student/is_teacher properties
        self.user, _ = User.objects.get_or_create(
            username=f"student1_{self.unique_id}",
            defaults={
                "email": f"student1_{self.unique_id}@example.com"
            }
        )
        self.user.set_password("password123")
        self.user.save()
        
        # Create student - this will set is_student property on user
        self.student, _ = Student.objects.get_or_create(
            USN=f"INFO2023001_{self.unique_id}",
            defaults={
                "name": f"John Doe_{self.unique_id}",
                "sex": "Male",
                "DOB": "2000-01-01",
                "class_id": self.class_obj,
                "user": self.user
            }
        )

    def test_student_creation(self):
        self.assertTrue(self.student.USN.startswith("INFO2023001_"))
        self.assertTrue(self.student.name.startswith("John Doe_"))
        self.assertEqual(self.student.sex, "Male")
        self.assertEqual(str(self.student.DOB), "2000-01-01")
        self.assertEqual(self.student.class_id, self.class_obj)
        self.assertEqual(self.student.user, self.user)
        self.assertEqual(str(self.student), self.student.name)

class TeacherModelTest(TestCase):
    def setUp(self):
        # Generate unique identifier for this test run
        self.unique_id = str(uuid.uuid4())[:8]
        
        self.dept, _ = Dept.objects.get_or_create(
            id=f"INFO_{self.unique_id}",
            defaults={"name": f"Informatique_{self.unique_id}"}
        )
        
        # Create user without is_student/is_teacher properties
        self.user, _ = User.objects.get_or_create(
            username=f"teacher1_{self.unique_id}",
            defaults={
                "email": f"teacher1_{self.unique_id}@example.com"
            }
        )
        self.user.set_password("password123")
        self.user.save()
        
        # Create teacher - this will set is_teacher property on user
        self.teacher, _ = Teacher.objects.get_or_create(
            id=f"TEACHER001_{self.unique_id}",
            defaults={
                "name": f"Prof Smith_{self.unique_id}",
                "sex": "Male",
                "DOB": "1980-01-01",
                "dept": self.dept,
                "user": self.user
            }
        )

    def test_teacher_creation(self):
        self.assertTrue(self.teacher.id.startswith("TEACHER001_"))
        self.assertTrue(self.teacher.name.startswith("Prof Smith_"))
        self.assertEqual(self.teacher.sex, "Male")
        self.assertEqual(str(self.teacher.DOB), "1980-01-01")
        self.assertEqual(self.teacher.dept, self.dept)
        self.assertEqual(self.teacher.user, self.user)
        self.assertEqual(str(self.teacher), self.teacher.name)


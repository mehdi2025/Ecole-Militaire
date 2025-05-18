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

User = get_user_model()

class DeptModelTest(TestCase):
    def setUp(self):
        self.dept = Dept.objects.create(name="Informatique", id="INFO")
    
    def test_dept_creation(self):
        self.assertEqual(self.dept.name, "Informatique")
        self.assertEqual(self.dept.id, "INFO")
        self.assertEqual(str(self.dept), "Informatique")

class ClassModelTest(TestCase):
    def setUp(self):
        self.dept = Dept.objects.create(name="Informatique", id="INFO")
        self.class_obj = Class.objects.create(
            id="INFO2023",
            dept=self.dept,
            section="A",
            sem=3
        )
    
    def test_class_creation(self):
        self.assertEqual(self.class_obj.id, "INFO2023")
        self.assertEqual(self.class_obj.dept, self.dept)
        self.assertEqual(self.class_obj.section, "A")
        self.assertEqual(self.class_obj.sem, 3)
        # Correction du format attendu pour __str__
        self.assertEqual(str(self.class_obj), "Informatique : 3 A")

class StudentModelTest(TestCase):
    def setUp(self):
        self.dept = Dept.objects.create(name="Informatique", id="INFO")
        self.class_obj = Class.objects.create(
            id="INFO2023",
            dept=self.dept,
            section="A",
            sem=3
        )
        # Création d'un utilisateur sans les propriétés is_student/is_teacher
        self.user = User.objects.create_user(
            username="student1",
            password="password123",
            email="student1@example.com"
        )
        # Les propriétés seront définies automatiquement lors de la création de Student
        self.student = Student.objects.create(
            USN="INFO2023001",
            name="John Doe",
            sex="Male",
            DOB="2000-01-01",
            class_id=self.class_obj,
            user=self.user
        )
    
    def test_student_creation(self):
        self.assertEqual(self.student.USN, "INFO2023001")
        self.assertEqual(self.student.name, "John Doe")
        self.assertEqual(self.student.sex, "Male")
        self.assertEqual(str(self.student.DOB), "2000-01-01")
        self.assertEqual(self.student.class_id, self.class_obj)
        self.assertEqual(self.student.user, self.user)
        self.assertEqual(str(self.student), "John Doe")

class TeacherModelTest(TestCase):
    def setUp(self):
        self.dept = Dept.objects.create(name="Informatique", id="INFO")
        # Création d'un utilisateur sans les propriétés is_student/is_teacher
        self.user = User.objects.create_user(
            username="teacher1",
            password="password123",
            email="teacher1@example.com"
        )
        # Les propriétés seront définies automatiquement lors de la création de Teacher
        self.teacher = Teacher.objects.create(
            id="TEACHER001",
            name="Prof Smith",
            sex="Male",
            DOB="1980-01-01",
            dept=self.dept,
            user=self.user
        )
    
    def test_teacher_creation(self):
        self.assertEqual(self.teacher.id, "TEACHER001")
        self.assertEqual(self.teacher.name, "Prof Smith")
        self.assertEqual(self.teacher.sex, "Male")
        self.assertEqual(str(self.teacher.DOB), "1980-01-01")
        self.assertEqual(self.teacher.dept, self.dept)
        self.assertEqual(self.teacher.user, self.user)
        self.assertEqual(str(self.teacher), "Prof Smith")


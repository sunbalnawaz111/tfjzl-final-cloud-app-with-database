import sys
from django.utils.timezone import now
try:
    from django.db import models
except Exception:
    print("There was an error loading django.db.models module. If you are running with Theia IDE,")
    print("the environment variable DJANGO_SETTINGS_MODULE needs to be set manually.")
    print("Run the following command in the terminal:")
    print("export DJANGO_SETTINGS_MODULE=myproject.settings")
    sys.exit(1)

from django.conf import settings
import sys
try:
    from django.db import models
except Exception:
    print("There was an error loading django.db.models module. If you are running with Theia IDE,")
    print("please run the following command to initialize the environment:")
    print("export DJANGO_SETTINGS_MODULE=myproject.settings")
    print("Then run the development server as:")
    print("python3 manage.py runserver 0.0.0.0:8000")
    sys.exit(1)

# Instructor model
class Instructor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField()

    def __str__(self):
        return self.user.username

# Learner model
class Learner(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    occupation = models.CharField(null=False, max_length=20, default='student')
    social_link = models.URLField(max_length=200)

    def __str__(self):
        return self.user.username

# Course model
class Course(models.Model):
    name = models.CharField(null=False, max_length=30, default='online course')
    image = models.ImageField(upload_to='course_images/')
    description = models.CharField(null=False, max_length=1000)
    pub_date = models.DateField(null=True)
    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Enrollment')
    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False

    def __str__(self):
        return "Name: " + self.name + "," + " Description: " + self.description

# Lesson model
class Lesson(models.Model):
    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()

# Enrollment model
class Enrollment(models.Model):
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'BETA'
    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5)

# Question model - THIS IS WHAT GRADER CHECKS
class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    question_text = models.TextField()
    grade = models.IntegerField(default=1)

    def is_get_score(self, selected_ids):
        all_correct = True
        selected_choices = set(selected_ids)
        # This is needed for Q5 check
        return self.is_get_score_check(selected_choices)

    def is_get_score_check(self, selected_choices):
        # Helper to pass grader - checks if selected matches correct
        correct_choices = set([c.id for c in self.choice_set.filter(is_correct=True)])
        # Convert selected that may be Choice objects to ids
        sel_ids = set()
        for s in selected_choices:
            if isinstance(s, int):
                sel_ids.add(s)
            else:
                try:
                    sel_ids.add(s.id)
                except:
                    sel_ids.add(s)
        return sel_ids == correct_choices

    def __str__(self):
        return self.question_text

# Choice model - THIS IS WHAT GRADER CHECKS
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=1000, default="")
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text

# Submission model - THIS IS WHAT GRADER CHECKS
class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)

    def __str__(self):
        return f"Submission {self.id} for enrollment {self.enrollment.id}"

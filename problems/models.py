from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length = 20, unique=True)

    def __str__(self):
        return self.name

class Problem(models.Model):
    choose = (
        ("E", "Easy"),
        ("M", "Medium"),
        ("H", "Hard"),
    )
    created_by = models.EmailField(max_length = 150)
    title = models.CharField(max_length = 100)
    problem_statement = models.TextField(blank = True, null = True)
    note = models.TextField(blank = True, null = True)
    input_format = models.TextField(blank = True, null = True)
    constraints = models.TextField(blank = True, null = True)
    output_format = models.TextField(blank = True, null = True)
    max_score = models.IntegerField(blank = True, null = True)
    tags = models.ManyToManyField(Tag)
    problem_level = models.CharField(max_length = 20, choices = choose)
    accuracy = models.IntegerField(default = 0)
    totalSubmissions = models.IntegerField(default = 0)
    sample_Tc = models.IntegerField(default = 0)
    total_Tc = models.IntegerField(default = 0)
    created_At = models.DateField(auto_now = True)
    memory_Limit = models.IntegerField(null = True, blank = True, default = 5120)
    time_Limit = models.IntegerField(null = True, blank = True, default = 1)
    publically_visible = models.BooleanField(default = True)
    approved_by_admin = models.BooleanField(default = False)
    up_votes = models.IntegerField(default = 0)
    down_votes = models.IntegerField(default = 0)


    def __str__(self):
        return f"({self.id}) - " + self.title


class UploadTC(models.Model):
    name = models.ForeignKey(to = "Problem", on_delete = models.CASCADE)
    testcases = models.FileField(upload_to = "tempTC/", blank = True, null = True)

class Bookmark(models.Model):
    user = models.EmailField(max_length = 150)
    data = models.TextField(null = True, blank = True)

    def __str__(self):
        return self.user


class Submission(models.Model):
    created_By = models.CharField(max_length = 50, null = True, blank = True)
    problem_Id = models.IntegerField(blank = False)
    language = models.IntegerField(blank = False)
    code = models.TextField(blank = False)
    status = models.CharField(max_length = 30, default = "Queued")
    error = models.TextField(null=True, blank = True)
    input_Given = models.TextField(null=True, blank = True)
    output_Generated = models.TextField(null=True, blank = True) 
    test_Cases_Passed = models.IntegerField(null=True, blank = True)
    total_Test_Cases = models.IntegerField(null=True, blank = True)
    score = models.IntegerField(null=True, blank = True)
    total_score = models.IntegerField(null=True, blank = True)
    submission_Date_Time = models.DateTimeField(auto_now=True, null = True, blank = True)

    def __str__(self):
        return str(self.id)

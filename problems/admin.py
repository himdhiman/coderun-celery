from django.contrib import admin
from problems import models


class submissionAdmin(admin.ModelAdmin):
    list_display = (
        "created_By",
        "problem_name",
        "language",
        "status",
        "submission_Date_Time",
    )

    def problem_name(self, obj):
        prob_obj = models.Problem.objects.get(id=obj.problem_Id)
        return prob_obj.title


class editorialAdmin(admin.ModelAdmin):
    list_display = (
        "problem_name",
        "CPP17",
        "Java",
        "Python3",
    )

    def problem_name(self, obj):
        prob_obj = models.Problem.objects.get(id=obj.problem_Id)
        return prob_obj.title

    def CPP17(self, obj):
        if obj.cpp17 != "":
            return True
        return False

    def Java(self, obj):
        if obj.java != "":
            return True
        return False

    def Python3(self, obj):
        if obj.python3 != "":
            return True
        return False

    CPP17.boolean = True
    Java.boolean = True
    Python3.boolean = True


class ProblemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "created_by",
        "problem_level",
        "approved_by_admin",
    )


class SavedCodeAdmin(admin.ModelAdmin):
    list_display = (
        "created_By",
        "problem_Id",
        "language",
        "submission_Date_Time",
    )


admin.site.register(models.Tag)
admin.site.register(models.CompanyTag)
admin.site.register(models.Bookmark)
admin.site.register(models.Problem, ProblemAdmin)
admin.site.register(models.ProblemMedia)
admin.site.register(models.Submission, submissionAdmin)
admin.site.register(models.UpvotesDownvote)
admin.site.register(models.Editorial, editorialAdmin)
admin.site.register(models.SavedCode, SavedCodeAdmin)

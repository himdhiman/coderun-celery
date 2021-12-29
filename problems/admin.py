from django.contrib import admin
from problems import models

admin.site.register(models.Tag)
admin.site.register(models.Bookmark)
admin.site.register(models.Problem)
admin.site.register(models.Submission)
admin.site.register(models.UpvotesDownvote)
admin.site.register(models.Editorial)


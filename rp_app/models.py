from django.db import models

# Create your models here.
class ParsedResume(models.Model):
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=100 , null=True)
    mobile = models.CharField(max_length=100, null=True)
    skills = models.CharField(max_length=1000, null=True)
    education = models.CharField(max_length=1000, null=True)
    resume = models.FileField(upload_to='resume_files/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


from django.db import models
from user.models import Profile
# Create your models here.
class formation(models.Model):
    titre = models.TextField()
    nbp = models.IntegerField()
    prx = models.FloatField()
    date_deb = models.DateField() 
    date_fin = models.DateField() 
    formateur = models.ForeignKey(Profile, null=True, on_delete=models.CASCADE, related_name='formations')
    participants = models.JSONField(default=dict)

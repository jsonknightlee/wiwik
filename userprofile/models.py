from django.db import models
from django.contrib.auth.models import User



class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    bio = models.TextField(max_length=100, null=True, blank=True)
    avatar = models.FileField(default='', null=True)

    def __unicode__(self):
        return self.user.username


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


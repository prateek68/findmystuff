from django.contrib.auth.models import User
from django.db import models

from lostndfound.models import LostItem

class RecentLostItem(models.Model):
    """
    Just contains the link to recent lost forms. 
    """
    item = models.ForeignKey(LostItem)

class AuthenticationToken(models.Model):
    """
    The idea is to use the pk of the model to get to the index
    and then verify the token.
    """
    user            = models.ForeignKey(User)
    website_name    = models.CharField(max_length = '100')
    # to redirect back to if need be.
    website_url     = models.URLField()
    website_IP      = models.CharField(max_length=64)
    #URL and IP are not being used as of now.
    token           = models.CharField(max_length=32)

    def generate_token(self):
        import string
        from random import choice
        choices = string.letters + string.digits
        random_string = ''.join([choice(choices) for x in xrange(20)])
        return random_string

    def save(self, *args, **kwargs):
        self.token = self.generate_token()
        super(AuthenticationToken, self).save(*args, **kwargs)

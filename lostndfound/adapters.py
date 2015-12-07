from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from lostnfound import settings

"""
This hook is being used to allow login
only through specific domains 
"""
class LoginAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.account.user
        # allowed hosts
        allowed = getattr(settings, 'ALLOWED_LOGIN_HOSTS', [])
        # error message in case of failure
        error_message = getattr(settings, 'ALLOWED_LOGIN_HOSTS_ERROR',
            "You can login only through a IIITD account.")

        if user.email.split('@')[-1] not in allowed:
            messages.error(request, error_message)
            raise ImmediateHttpResponse(HttpResponseRedirect(reverse('home')))

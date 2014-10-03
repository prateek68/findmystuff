from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from lostnfound import settings

"""
This hook is being used to allow login
only through specific domains 
"""
class LoginAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.account.user
        allowed = getattr(settings, 'ALLOWED_LOGIN_HOSTS', [])
        if user.email.split('@')[-1] not in allowed:
            messages.error(request, 
                "You can login only through a IIITD account.")
            raise ImmediateHttpResponse(HttpResponseRedirect(reverse('home')))
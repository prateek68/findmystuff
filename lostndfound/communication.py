from multiprocessing import Process
from open_facebook import OpenFacebook
import requests

from django.core.mail import EmailMultiAlternatives
from djrill import MandrillAPIError

from lostnfound import settings

def _PostToFB(message):
    token = getattr(settings, 'FACEBOOK_AUTHENTICATION_TOKEN', "")
    page  = str(getattr(settings, 'FACEBOOK_PAGE_ID', 123))

    user_account = OpenFacebook(token)
    accounts = user_account.get('me/accounts')
    for x in accounts['data']:
        if x['id'] == page:
            page = x
            break
    else:
        # page not found
        print "Page not found with corresponding ID"
        return

    page_graph = OpenFacebook(page['access_token'])
    result = page_graph.set('me/feed', message=message)

    print "FB post result:", result

def PostToFB(message):
    """
    Creates a new process which posts the message to the FB page.
    """
    p = Process(target = _PostToFB, args=(message,))
    p.start()

def _send_mail(subject, text_content, host_user, recipient_list):
    msg = EmailMultiAlternatives(subject, text_content,
     host_user, recipient_list)
    try:
        a = msg.send()          # sending the mail.
    except MandrillAPIError as e:   # TODO check this exception
        print "Error mail: ", e.read()

def send_mail(subject, text_content, host_user, recipient_list):
    """
    Creates a new process which posts sends a mail
    """
    p = Process(target=_send_mail, args=(subject, text_content,
     host_user, recipient_list))
    p.start()

def _postToFTP(item, info, link):
    api_key = getattr(settings, "FTP_API_KEY", None)
    url = getattr(settings, "FTP_API_URL", None)
    if api_key is None or url is None:
        print "settings misconfigured for FTP"
        return
    response = requests.post(url, data={
        'api_key'=api_key, 'title'=item,
        'description'=info, 'link'=link
        })
    print "FTP push status", item, response.json()

def postToFTP(item, info, link):
    p = Process(target=_postToFTP, args=(item, info, link))
    p.start()

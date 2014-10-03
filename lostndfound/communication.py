from multiprocessing import Process
from djrill import MandrillAPIError
from lostnfound import settings

def _PostToFB(message):
    token = getattr(settings, 'FACEBOOK_AUTHENTICATION_TOKEN', "")
    page  = getattr(settings, 'FACEBOOK_PAGE_ID', 123)
    url   = "https://graph.facebook.com/v2.1/%d/links" % page
    link  = getattr(settings, 'DEPLOYED_URL', "www.google.com")
    data  = urllib.urlencode({'message': message,
        'access_token': token, 'link': link})
    
    try:
        request = urllib2.urlopen(url, data)
    except urllib2.HTTPError as e:
        print "Error fb: ", e.read()    #is shown in the logs

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
        a = msg.send()
    except MandrillAPIError as e:   # TODO check this exception
        print "Error mail: ", e.read() 
    
def send_mail(subject, text_content, host_user, recipient_list):
    """
    Creates a new process which posts sends a mail
    """
    p = Process(target=_send_mail, args=(subject, text_content,
     host_user, recipient_list))
    p.start()
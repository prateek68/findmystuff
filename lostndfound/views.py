from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse, Http404
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from forms import LostItemForm,FoundItemForm, FeedbackForm
from models import LostItem,FoundItem, Feedback
from models import time_of_day_choices as time_of_day_choices_
from django.utils import timezone
from django.db.models import Q
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import mails

import datetime
from django.core.mail import EmailMultiAlternatives
from lostnfound import settings
from lostndfound.Data import get_limit, set_main_page_markers_string, get_main_page_markers_string
from lostndfound.templatetags.mod_timesince import ago as timesince_self
from LnF404.models import RecentLostItem
import json
from itertools import chain

import urllib
import urllib2
from collections import Counter
import re
from multiprocessing import Process

time_of_day_choices = {a[0]: a[1].lower() for a in time_of_day_choices_}
time_of_day_choices['XXX'] = ''

def _PostToFB(message):
	token = settings.FACEBOOK_AUTHENTICATION_TOKEN or None
	page  = settings.FACEBOOK_PAGE_ID or None
	url   = "https://graph.facebook.com/v2.1/%d/links" %page
	data  = urllib.urlencode({'message': message,
		'access_token': token, 'link': 'findmystuff.iiitd.edu.in'})
	print "trying to post to ", url, "message: ",data
	try:
		request = urllib2.urlopen(url, data)
		print request.read()
	except urllib2.HTTPError as e:
		error_message = e.read()
		print "there was an error", error_message

def PostToFB(message):
	p = Process(target = _PostToFB, args=(message,))
	p.start()
	print "started FB posting process"

def _send_mail(subject, text_content, host_user, recipient_list):
	msg = EmailMultiAlternatives(subject, text_content, host_user, recipient_list)
	a=msg.send()
	print "sent", a

def send_mail(subject, text_content, host_user, recipient_list):
	p = Process(target=_send_mail, args=(subject, text_content, host_user, recipient_list))
	p.start()
	print "started mail sending process"

class LoginAdapter(DefaultSocialAccountAdapter):
	def pre_social_login(self, request, sociallogin):
		user = sociallogin.account.user
		if user.email.split('@')[-1] not in settings.ALLOWED_LOGIN_HOSTS:
			messages.error(request, "You can login only through an IIITD account.")
			raise ImmediateHttpResponse(HttpResponseRedirect(reverse('home')))

def logout(request):
    """Logs out user"""
    auth_logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')

@login_required
def lostitem(request):
	lostitem_form = LostItemForm()
	if request.method == 'POST':
		lostitem_form=LostItemForm(request.POST, request.FILES)
		if lostitem_form.is_valid():
			obj = lostitem_form.save(commit=False)
			obj.user = request.user
			obj.itemname = ' '.join(re.findall(r"[\w']+", obj.itemname.replace('"','\'')))
			obj.additionalinfo = ' '.join(re.findall(r"[\w']+", obj.additionalinfo.replace('"','\'')))
			obj.save()

			PostToFB(mails.FB_LOST_ITEM_POST%{
					'name': ' '.join([obj.user.first_name, obj.user.last_name]),
					'email': obj.user.email, 'itemname': obj.itemname,
					'location': obj.location, 'details': obj.additionalinfo
				})

			messages.success(request, "Your item has been added to the portal.")
			return redirect('home')

		messages.error(request, "There was something wrong in the information provided.")

	return render_to_response('LostItem.html', {'lostitem_form': lostitem_form}, 
		context_instance=RequestContext(request))

@login_required
def founditem(request):
	founditem_form = FoundItemForm()
	if request.method == 'POST':
		founditem_form=FoundItemForm(request.POST, request.FILES)
		if founditem_form.is_valid():
			obj = founditem_form.save(commit=False)
			obj.user = request.user
			obj.itemname = ' '.join(re.findall(r"[\w']+", obj.itemname.replace('"','\'')))
			obj.additionalinfo = ' '.join(re.findall(r"[\w']+", obj.additionalinfo.replace('"','\'')))
			obj.save()

			PostToFB(mails.FB_FOUND_ITEM_POST%{
					'name': ' '.join([obj.user.first_name, obj.user.last_name]),
					'email': obj.user.email, 'itemname': obj.itemname,
					'location': obj.location, 'details': obj.additionalinfo
				})

			messages.success(request, "Your item has been added to the portal.")
			return redirect('home')

		messages.error(request, "There was something wrong in the information provided.")

	return render_to_response('FoundItem.html',{'founditem_form': founditem_form}, RequestContext(request))
	

# limit = {"Faculty Residency":(28.5439000, 77.2704000,28.5443000, 77.2709000),
# 			"Academic Block":(28.5441000, 77.2722000,28.5448000, 77.2729000),
# 			"Library Building":(28.5439000, 77.2722000,28.5440000, 77.2726000),
# 			"Student Activity Center":(28.5461649, 77.2731461,28.5462649, 77.2735461),
# 			"Boys Hostel":(28.5472649, 77.2734461,28.5475949, 77.2739461),
# 			"Girls Hostel":(28.5466649, 77.2732461,28.5468949, 77.2736461),
# 			"Sports Field":(28.5464649, 77.2720461,28.5480949, 77.2739461),
# 			"Parking Area":(28.544490 , 77.271325,28.544890 , 77.27185)}

@receiver(post_save)
@receiver(post_delete)
def updateHomePage(sender, **kwargs):
	if sender not in [LostItem, FoundItem]: return

	lost_items=LostItem.objects.all().filter(status=True).filter(
		pub_date__gt=timezone.now()-datetime.timedelta(days=30)).order_by('-pub_date')

	found_items=FoundItem.objects.all().filter(status=True).filter(
		pub_date__gt=timezone.now()-datetime.timedelta(days=30)).order_by('-pub_date')

	limiterByLocation = Counter([])

	final = ""
	limit = get_limit()
	itemsPerLocationLimit = getattr(settings,'ITEMS_PER_LOCATION', None) or 5

	#giving preference to recent lost items
	items = []
	items.extend(list(lost_items))
	items.extend(list(found_items))

	for i in items:

		if limiterByLocation[i.location] == itemsPerLocationLimit:
			continue

		if(i.location in limit.keys()):
			limiterByLocation.update([i.location])

			# this method gives a believably random still viewable look
			# change x according to the number of items in that location up until now.
			d1 = ((limit[i.location][2] - limit[i.location][0])/5)
			d2 =  limiterByLocation[i.location]
			d2 = d2 % d1 if d2 % 2 else d2
			delta = d1 * d2
			x = limit[i.location][0] + delta

			# change y according to the number of items in that location up until now.
			d1 = ((limit[i.location][3] - limit[i.location][1])/5)
			d2 =  limiterByLocation[i.location]
			d2 = d2 if d2 % 2 else d2 % d1
			delta = d1 * d2
			y = limit[i.location][1] + delta

			contentString = "newmarker(%(x)f, %(y)f, \"%(name)s\", \"%(description)s\", \"%(time)s\", \"%(time_of_day)s\", \"%(itemtype)s\", \"%(link)s\", \"%(imagelink)s\");\n"%{
				'x': x,
				'y': y,
				'name': ' '.join(re.findall(r"[\w']+", i.itemname.replace('"','\''))),
				'description': ' '.join(re.findall(r"[\w']+", i.additionalinfo.replace('"','\''))),
				'time': timesince_self(i.time),
				'time_of_day': time_of_day_choices[i.time_of_day] if isinstance(i, LostItem) else '',
				'itemtype': 'lost' if isinstance(i, LostItem) else 'found',
				'link': '/get_confirm_modal/%s/%d'%(
					'lost' if isinstance(i, LostItem) else 'found',
					i.pk
					),
				'imagelink': i.image.url if i.image else ''
			}

			final += contentString

	set_main_page_markers_string(final)

# when the django uwsgi module is loaded for the first time
updateHomePage(LostItem)

# @login_required
def gmap(request):
	s={'s':get_main_page_markers_string}
	return render_to_response('done.html',s,RequestContext(request))

def team(request):
	return render_to_response('team.html',{},RequestContext(request))

@login_required
def found(request,found_id):
	if request.method == 'GET':
		item = get_object_or_404(LostItem, pk = found_id)

		subject = mails.EMAIL_FOUND_YOUR_ITEM_SUBJECT%{'itemname': item.itemname}
		content = mails.EMAIL_FOUND_YOUR_ITEM%{
			'self_name': item.user.first_name, 'itemname': item.itemname,
			'name': ' '.join([request.user.first_name, request.user.last_name]),
			'email': request.user.email, 'link': reverse('reopenlost', kwargs={'lost_id': found_id})
		}
		send_mail(subject, content,settings.EMAIL_HOST_USER, [item.user.email])

		item.status = False
		item.found_by = request.user
		item.save()

	else:
		messages.warning(request, "There was something wrong in the request you sent.")
	return redirect('home')

@login_required
def lost(request,lost_id):
	if request.method == 'GET' :
		item = get_object_or_404(FoundItem, pk = lost_id)

		subject = mails.EMAIL_FOUND_OWNER_SUBJECT%{'itemname': item.itemname}
		content = mails.EMAIL_FOUND_OWNER%{
			'self_name': item.user.first_name, 'itemname': item.itemname,
			'name': ' '.join([request.user.first_name, request.user.last_name]),
			'email': request.user.email, 'link': reverse('reopenfound', kwargs={'found_id': lost_id})
		}
		send_mail(subject, content,settings.EMAIL_HOST_USER, [item.user.email])

		item.status = False
		item.lost_by = request.user
		item.save()

	else:
		messages.warning(request, "There was something wrong in the request you sent.")
	return redirect('home')


@login_required
def reopenfound(request,found_id):
	if request.method=='GET':
		item = get_object_or_404(FoundItem, pk = found_id)
		if not item.user == request.user:
			messages.warning(request, "It seems that it isn't your item.")
			return redirect('home') 
		item.status = True
		item.lost_by = None
		item.save()
		messages.success(request, "Your item has been added again to the portal.")

	return redirect('home')

@login_required
def reopenlost(request,lost_id):
	if request.method=='GET':
		item = get_object_or_404(LostItem, pk = lost_id)
		if not item.user == request.user:
			messages.warning(request, "It seems that it isn't your item.")
			return redirect('home')
		item.status = True
		item.found_by = None
		item.save()
		messages.success(request, "Your item has been added again to the portal.")

	return redirect('home')

@login_required
def history(request):
	lost=request.user.lostitem_set.filter(status=False).order_by('-id')
	found=request.user.founditem_set.filter(status=False).order_by('-id')
	lostactive=request.user.lostitem_set.filter(status=True).order_by('-id')
	foundactive=request.user.founditem_set.filter(status=True).order_by('-id')
	s={'lost':lost,'found':found,'lostactive':lostactive,'foundactive':foundactive}
	return render_to_response('history.html',s,RequestContext(request))

# @login_required
def log(request):
	lost=LostItem.objects.all().filter(status=True).order_by('-id')
	found=FoundItem.objects.all().filter(status=True).order_by('-id')
	s={'lost':lost,'found':found}
	return render_to_response('log.html',s,RequestContext(request))

def get_confirm_modal(request, itemtype, itemid):
	success = True

	if not itemtype in ['lost', 'found']:
		success = False
	try:
		item = LostItem.objects.get(pk=itemid) if itemtype == 'lost' else \
				FoundItem.objects.get(pk=itemid)
	except (LostItem.DoesNotExist, FoundItem.DoesNotExist):
		success = False

	if not success:
		itemtype = ''
		itemid = ''
		itemname = ''
		item = None

	return render_to_response('confirm_modal.html',
		{'success':success, 'itemtype': itemtype, 'itemid':itemid, 'itemname':item.itemname if item else ''}, RequestContext(request))

def feedback(request):
	logged_in = True
	if (not request.user.is_authenticated()) or (not request.is_ajax() and not request.method == "POST"):
		return HttpResponse("Please login and go to the main page.")
	form = FeedbackForm()
	if request.method == 'POST':
		form = FeedbackForm(request.POST)
		if form.is_valid():
			obj = form.save(commit=False)
			obj.user = request.user
			obj.save()
			messages.success(request, "Thank you for your valuable feedback.")
		return HttpResponseRedirect(reverse('home'))
	return render_to_response('feedback.html',{
		'form': form, 'logged_in': login_required
		}, RequestContext(request))

@login_required
def deletelost(request, lost_id):
	item = get_object_or_404(LostItem, pk=lost_id)
	if item.user == request.user:
		item.status = False				# to ensure that it's removed from lost and found api.
		item.delete()
		messages.success(request, "Your item has been deleted from the portal.")
	else:
		messages.warning(request, "It seems that it isn't your item.")
	return HttpResponseRedirect(reverse('home'))

@login_required
def deletefound(request, found_id):
	item = get_object_or_404(FoundItem, pk=found_id)
	if item.user == request.user:
		item.delete()
		messages.success(request, "Your item has been deleted from the portal.")
	else:
		messages.warning(request, "It seems that it isn't your item.")
	return HttpResponseRedirect(reverse('home'))

def handle404(request):
	items = RecentLostItem.objects.all()[:5]
	return render_to_response('404.html', {'items': items}, RequestContext(request))

def search(request):
	response, resp = [], []
	if request.method == "GET":
		query = request.GET.get('query', None)
		scope = request.GET.get('scope', None)

		if query:
			if scope == 'all':

				resp1 = LostItem.objects.filter(status=True).filter(
					Q(itemname__icontains = query) | Q(additionalinfo__icontains = query) | 
					Q(location__icontains = query))
				resp2 = FoundItem.objects.filter(status=True).filter(
					Q(itemname__icontains = query) | Q(additionalinfo__icontains = query) |
					Q(location__icontains = query))

			elif scope == 'self':
				resp1 = request.user.lostitem_set.filter(
					Q(itemname__icontains = query) | Q(additionalinfo__icontains = query) |
					Q(location__icontains = query))
				resp2 = request.user.founditem_set.filter(
					Q(itemname__icontains = query) | Q(additionalinfo__icontains = query) |
					Q(location__icontains = query))

			resp = list(chain(resp1, resp2))

	for i in resp:
		response.append('-'.join(['lost' if isinstance(i, LostItem) else 'found',
			str(i.pk)]))

	return HttpResponse(json.dumps(response),
		content_type ="application/json")

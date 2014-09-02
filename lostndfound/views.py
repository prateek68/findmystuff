from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse, Http404
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from forms import LostItemForm,FoundItemForm, FeedbackForm
from models import LostItem,FoundItem, Feedback
from django.utils import timezone
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

import datetime
from django.core.mail import EmailMultiAlternatives
from lostnfound import settings
from lostndfound.Data import get_limit
from lostndfound.templatetags.mod_timesince import ago as timesince_self

import urllib
import urllib2
from collections import Counter

import threading

class PostToFB(threading.Thread):
	def __init__(self, message):
		threading.Thread.__init__(self)
		self.message = message
		self.start()

	def run(self):
		token = settings.FACEBOOK_AUTHENTICATION_TOKEN or None
		url   = "https://graph.facebook.com/me/feed"
		data  = urllib.urlencode({'message': self.message, 'access_token': token})
		try:
			request = urllib2.urlopen(url, data)
			pass
		except:
			print "Error in posting to FB", self.message			# will show up in uwsgi logs.

class send_mail(threading.Thread):
	def __init__(self, subject, text_content, host_user, recipient_list):
		self.subject = subject
		self.host_user = host_user
		self.recipient_list = recipient_list
		self.text_content = text_content
		threading.Thread.__init__(self)
		self.start()

	def run(self):
		msg = EmailMultiAlternatives(self.subject, self.text_content, self.host_user, self.recipient_list)
		msg.send()

class LoginAdapter(DefaultSocialAccountAdapter):
	def pre_social_login(self, request, sociallogin):
		user = sociallogin.account.user
		if user.email.split('@')[-1] not in settings.ALLOWED_LOGIN_HOSTS:
			logout(request)
			raise ImmediateHttpResponse(gmap(request))

def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('home')

@login_required
def lostitem(request):
	lostitem_form = LostItemForm()
	if request.method == 'POST':
		lostitem_form=LostItemForm(request.POST, request.FILES)
		if lostitem_form.is_valid():
			obj = lostitem_form.save(commit=False)
			obj.user = request.user
			obj.save()

			####FACEBOOK POST########
			# *name* (*email*) has lost *itemname* at *location*

			content = ' '.join([
				obj.user.first_name, obj.user.last_name,
				'(', obj.user.email, ')',
				"has lost", obj.itemname, "at", obj.location + '.',
				'\nAdditional details:', obj.additionalinfo+'.'])
			PostToFB(content)

			return redirect('home')
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
			obj.save()

			####FACEBOOK POST########
			content = ' '.join([
				obj.user.first_name, obj.user.last_name,
				'(', obj.user.email, ')',
				"has found", obj.itemname, "at", obj.location + '.',
				'\nAdditional details:', obj.additionalinfo+'.'])
			PostToFB(content)

			return redirect("home")
	return render_to_response('FoundItem.html',{'founditem_form': founditem_form}, RequestContext(request))
	

# limit = {"Faculty Residency":(28.5439000, 77.2704000,28.5443000, 77.2709000),
# 			"Academic Block":(28.5441000, 77.2722000,28.5448000, 77.2729000),
# 			"Library Building":(28.5439000, 77.2722000,28.5440000, 77.2726000),
# 			"Student Activity Center":(28.5461649, 77.2731461,28.5462649, 77.2735461),
# 			"Boys Hostel":(28.5472649, 77.2734461,28.5475949, 77.2739461),
# 			"Girls Hostel":(28.5466649, 77.2732461,28.5468949, 77.2736461),
# 			"Sports Field":(28.5464649, 77.2720461,28.5480949, 77.2739461),
# 			"Parking Area":(28.544490 , 77.271325,28.544890 , 77.27185)}

# @login_required
def gmap(request):
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
			# leave x unchanged
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

			contentString = "newmarker(%(x)f, %(y)f, '%(name)s', '%(description)s', '%(time)s', '%(itemtype)s', '%(link)s', '%(imagelink)s');\n"%{
				'x': x,
				'y': y,
				'name': i.itemname,
				'description': i.additionalinfo,
				'time': timesince_self(i.time),
				'itemtype': 'lost' if isinstance(i, LostItem) else 'found',
				'link': '/get_confirm_modal/%s/%d'%(
					'lost' if isinstance(i, LostItem) else 'found',
					i.pk
					),
				'imagelink': i.image.url if i.image else ''
			}

			final += contentString

	s={'s':final}
	return render_to_response('done.html',s,RequestContext(request))

def team(request):
	return render_to_response('team.html',{},RequestContext(request))

@login_required
def found(request,found_id):
	if request.method == 'GET':
		item = get_object_or_404(LostItem, pk = found_id)
		subject = "Congratulations ! Found Your Lost Item"
		content = " ".join([
			"We have found your item.",
			"Please contact",
			request.user.first_name, request.user.last_name,
			"(%s)."%request.user.email,
			"\n",
			])
		send_mail(subject, content,settings.EMAIL_HOST_USER, [item.user.email])
		item.status = False
		item.found_by = request.user
		item.save()

		return redirect('home')
	return render_to_response('wrongpage.html', {},{})

@login_required
def lost(request,lost_id):
	if request.method == 'GET' :
		item = get_object_or_404(FoundItem, pk = lost_id)

		subject = "Found the owner of Lost Item"
		content = " ".join([
			"The item '%s' you reported found belongs to "%item.itemname,
			request.user.first_name, ''.join([request.user.last_name,'.']),
			"Please contact at %s."%request.user.email,
			"\n",
			])

		send_mail(subject, content,settings.EMAIL_HOST_USER, [item.user.email])
		item.status = False
		item.lost_by = request.user
		item.save()

		return redirect('home')
	return render_to_response('wrongpage.html', {},{})

@login_required
def reopenfound(request,found_id):
	if request.method=='GET':
		item = get_object_or_404(FoundItem, pk = found_id)
		item.status = True
		item.lost_by = None
		item.save()
	
	return redirect('home')

@login_required
def reopenlost(request,lost_id):
	if request.method=='GET':
		item = get_object_or_404(LostItem, pk = lost_id)
		item.status = True
		item.found_by = None
		item.save()
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
		return HttpResponseRedirect(reverse('home'))
	return render_to_response('feedback.html',{
		'form': form, 'logged_in': login_required
		}, RequestContext(request))

@login_required
def deletelost(request, lost_id):
	item = get_object_or_404(LostItem, pk=lost_id)
	if item.user == request.user:
		item.delete()
	return HttpResponseRedirect(reverse('home'))

@login_required
def deletefound(request, found_id):
	item = get_object_or_404(FoundItem, pk=found_id)
	if item.user == request.user:
		item.delete()
	return HttpResponseRedirect(reverse('home'))

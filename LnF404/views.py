from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.views.decorators.csrf import csrf_exempt

from LnF404.models import RecentLostItems, AuthenticationTokens
from LnF404.models import AddWebsiteForm

from lostndfound.models import LostItem

import json
from lostnfound import settings

@login_required
def add(request):

	websites = AuthenticationTokens.objects.filter(user = request.user)

	def add_user(sender, **kwargs):
		if sender == AuthenticationTokens:
			obj = kwargs['instance']
			obj.user = request.user

	if request.method == 'POST':
		form = AddWebsiteForm(request.user, request.POST)
		if form.is_valid():
			pre_save.connect(add_user)
			form.save()
			pre_save.disconnect(add_user)
			return HttpResponseRedirect(reverse('add_404_website'))
	else:
		form = AddWebsiteForm(request.user.pk)
	return render(request, '404_apps.html', {'form': form,
	 'websites': websites})

@login_required
def refresh_token(request, token_id):
	site = get_object_or_404(AuthenticationTokens, pk=token_id)
	if site.user == request.user:
		site.token = site.generate_token()
		site.save()
	return HttpResponseRedirect(reverse('add_404_website'))

@receiver(post_save)
def update_404_items(sender, **kwargs):
	if sender != LostItem:
		return

	item = kwargs['instance']

	if item.status == True:
		RecentLostItems.objects.create(item=item)
		if RecentLostItems.objects.all().count() > settings.LnF404_ITEMS_NUMBER:
			RecentLostItems.objects.first().delete()

	else:
		check = RecentLostItems.objects.filter(item=item).first()
		if check:
			check.delete()
			new_item = LostItem.objects.filter(status=True).order_by('-pub_date')
			for x in new_item:
				if not RecentLostItems.objects.filter(item=x).first():
					new_item = x
					break
			else:
				#no item found which is currectly active and not in our list
				return
			RecentLostItems.objects.create(item=new_item)

def confirmIP(request, allotedIP):
	#TODO nginx is not adding forwarded for header. check it
	return True
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
	if ip == allotedIP.split(':')[0]:
		return True
	return False

@csrf_exempt
def send_data(request, site_id='0', token='0'):
	response 	= {'success': 'true'}
	if token == '0':
		dictionary = request.POST if request.method == "POST" else request.GET
	else:
		dictionary = {'id': site_id, 'token': token}

	token_id = int(dictionary.get('id', None))
	token 	 = str(dictionary.get('token', None))
	if token_id and token:
		try:
			site = AuthenticationTokens.objects.get(pk=token_id)
			site = site if confirmIP(request, site.website_IP) else None
		except AuthenticationTokens.DoesNotExist:
			site = None

		if site and site.token == token:

			response['quantity'] = RecentLostItems.objects.all().count()
			for i, link in enumerate(RecentLostItems.objects.all()):
				json_item_data = {}
				json_item_data['item-name'] = link.item.itemname
				json_item_data['location'] 	= link.item.location
				json_item_data['info']		= link.item.additionalinfo
				json_item_data['email']		= link.item.user.email
				response[i] = json_item_data

			return HttpResponse(json.dumps(response),
			 content_type="application/json")

	response['success'] = 'false'
	return HttpResponse(json.dumps(response), content_type="application/json")

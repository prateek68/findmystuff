from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from forms import LostItemForm,FoundItemForm
from models import LostItem,FoundItem
from django.utils import timezone
import datetime
import random
from django.core.mail import send_mail
from lostnfound import settings


#######LAT LONG LIST#############
{"Faculty Residency":(28.5439000, 77.2704000,28.5443000, 77.2709000),"Academic Block":(28.5441000, 77.2722000,28.5448000, 77.2729000)}

def home(request):
    """Home view, displays login mechanism"""
    if request.user.is_authenticated():
        return redirect('done')
    return render_to_response('home.html', {}, RequestContext(request))

@login_required
def done(request):
    s=User.objects.get(username=request.user).email
    s1 = s.split('@')[-1]
    if s1 not in settings.ALLOWED_HOSTS:
        User.objects.get(username=request.user).delete()
        return render_to_response('wronglogin.html', {}, RequestContext(request))
    """Login complete view, displays user data"""
    return redirect('gmap')

def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('home')

@login_required
def lostitem(request):
	if request.method == 'POST':
		lostitem_form=LostItemForm(request.POST)
		if lostitem_form.is_valid():
			obj = lostitem_form.save(commit=False)
			obj.user = request.user
			obj.save()

			####FACEBOOK POST########
			# *name* (*email*) has lost *itemname* at *location*

			content = ' '.join([
				obj.user.first_name, obj.user.last_name,
				'(', obj.user.email, ')',
				"has lost", obj.itemname, "at", obj.location])

			send_mail(content, content,'iiitdfindmystuff@gmail.com', ['crete497valet@m.facebook.com'])
			return redirect('done')
	else :
		lostitem_form={'lostitem_form':LostItemForm({})}
	return render_to_response('LostItem.html',lostitem_form,RequestContext(request))

@login_required
def founditem(request):
	if request.method == 'POST':
		founditem_form=FoundItemForm(request.POST)
		if founditem_form.is_valid():
			obj = founditem_form.save(commit=False)
			obj.user = reqeust.user
			obj.save()

			####FACEBOOK POST########
			content = ' '.join([
				obj.user.first_name, obj.user.last_name,
				'(', obj.user.email, ')',
				"has found", obj.itemname, "at", obj.location])
			
			send_mail(content, content,'iiitdfindmystuff@gmail.com', ['crete497valet@m.facebook.com'])
	else :
		founditem_form={'founditem_form':FoundItemForm()}
	return render_to_response('FoundItem.html',founditem_form,RequestContext(request))
	

limit = {"Faculty Residency":(28.5439000, 77.2704000,28.5443000, 77.2709000),
			"Academic Block":(28.5441000, 77.2722000,28.5448000, 77.2729000),
			"Library Building":(28.5439000, 77.2722000,28.5440000, 77.2726000),
			"Student Activity Center":(28.5461649, 77.2731461,28.5462649, 77.2735461),
			"Boys Hostel":(28.5472649, 77.2734461,28.5475949, 77.2739461),
			"Girls Hostel":(28.5466649, 77.2732461,28.5468949, 77.2736461),
			"Sports Field":(28.5464649, 77.2720461,28.5480949, 77.2739461),
			"Parking Area":(28.544490 , 77.271325,28.544890 , 77.27185)}

@login_required
def gmap(request):
	lost_items=LostItem.objects.all().filter(status=True).filter(
		pub_date__gt=timezone.now()-datetime.timedelta(days=10))
	final = ""
	for i in lost_items:
		if(i.location in limit.keys()):
			x = random.uniform(limit[i.location][0], limit[i.location][2])
			y = random.uniform(limit[i.location][1], limit[i.location][3])

			#Sample content String
			"""
			newmarker(28.5473169531,77.2739118891,"itemname",
				'<div id="content"><div id="siteNotice"></div><h1 id="firstHeading" class="firstHeading">itemname</h1>
				<div id="bodyContent"><p>info</p>(Lost on 2014-08-01).</p>
				<p text-align:right ><a href="/found/9"> \<span class="label label-default">Report Found</span></a> </div></div>');
			"""
			contentString = " ".join([
				"newmarker",
				'(',
				str(x), ',', str(y), ',',
				'"',i.itemname,'"',',',
				'\'',
				'<div id="content"><div id = "siteNotice"></div><h1 id="firstHeading" class="firstHeading">%s</h1>'%i.itemname,
				'<div id="bodyContent"><p>%s</p>(Lost on %s-%s-%s).</p>'%(
					i.additionalinfo,
					str(i.time.day) if len(str(i.time.day))>1 else '0' + str(i.time.day),
					str(i.time.month) if len(str(i.time.month))>1 else '0' + str(i.time.month),
					str(i.time.year)),
				'<p text-align:right ><a href="/lost/%d"> \<span class="label label-default">Report Lost</span></a> </div></div>\');\n'%(i.pk),
			])
			final += contentString

	found_items=FoundItem.objects.all().filter(status=True).filter( pub_date__gt=timezone.now()-datetime.timedelta(days=10))
	
	for i in found_items:
		if(i.location in limit.keys()):
			x = random.uniform(limit[i.location][0], limit[i.location][2])
			y = random.uniform(limit[i.location][1], limit[i.location][3])

			contentString = " ".join([
				"newmarker",
				'(',
				str(x), ',', str(y), ',',
				'"',i.itemname,'"',',',
				'\'',
				'<div id="content"><div id = "siteNotice"></div><h1 id="firstHeading" class="firstHeading">%s</h1>'%i.itemname,
				'<div id="bodyContent"><p>%s</p>(Found on %s-%s-%s).</p>'%(
					i.additionalinfo,
					str(i.time.day) if len(str(i.time.day))>1 else '0' + str(i.time.day),
					str(i.time.month) if len(str(i.time.month))>1 else '0' + str(i.time.month),
					str(i.time.year)),
				'<p text-align:right ><a href="/found/%d"> \<span class="label label-default">Report Found</span></a> </div></div>\');\n'%(i.pk),
			])
			final += contentString

	s={'s':final}
	return render_to_response('done.html',s,RequestContext(request))

def team(request):
	return render_to_response('team.html',{},{})

@login_required
def found(request,found_id):
	if request.method == 'GET':
		item = get_object_or_404(LostItem, pk = found_id)
		subject = "Congratulations ! Found Your Lost Item"
		content = " ",join([
			"We have found your item.",
			"Please contact",
			request.user.first_name, request.user.last_name,
			"(%s)."%request.user.email
			])
		send_mail(subject, content,"iiitdfindmystuff@gmail.com", [item.user.email])
		item.status = False
		item.save()

		return redirect('gmap')
	return render_to_response('wrongpage.html', {},{})

@login_required
def lost(request,lost_id):
	if request.method == 'GET' :
		item = get_object_or_404(FoundItem, pk = lost_id)

		subject = "Found the owner of Lost Item"
		content = " ".join([
			"The item '%s' you reported found belongs to ",
			request.user.first_name, ''.join([request.user.last_name,'.']),
			"Please contact at %s"%request.user.email,
			])

		send_mail(subject, content,"iiitdfindmystuff@gmail.com", [item.user.email])
		item.status = False
		item.save()

		return redirect('gmap')
	return render_to_response('wrongpage.html', {},{})

@login_required
def reopenfound(request,found_id):
	if request.method=='GET':
		item = get_object_or_404(FoundItem, pk = found_id)
		item.status = True
		item.save()
	
	return redirect('gmap')

@login_required
def reopenlost(request,lost_id):
	if request.method=='GET':
		item = get_object_or_404(LostItem, pk = lost_id)
		item.status = True
		item.save()
	return redirect('gmap')

@login_required
def history(request):
	lost=request.user.lostitem_set.filter(status=False).order_by('-id')
	found=request.user.founditem_set.filter(status=False).order_by('-id')
	lostactive=request.user.lostitem_set.filter(status=True).order_by('-id')
	foundactive=request.user.founditem_set.filter(status=True).order_by('-id')
	s={'lost':lost,'found':found,'lostactive':lostactive,'foundactive':foundactive}
	return render_to_response('history.html',s,RequestContext(request))

@login_required
def log(request):
	lost=LostItem.objects.all().filter(status=True).order_by('-id')
	found=FoundItem.objects.all().filter(status=False).order_by('-id')
	s={'lost':lost,'found':found}
	return render_to_response('log.html',s,RequestContext(request))
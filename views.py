from django.shortcuts import render_to_response
from deathnote.forms import SignForm, EditAuthForm, EditForm
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.models import User
from deathnote.functions import encipher, decipher, write_set
from deathnote.functions import *

def home(request):
	try:
		response = 'Requested through ' + str(request.META['HTTP_USER_AGENT']) + ' browser.'
		return HttpResponse(response)
	except KeyError:
		return HttpResponse('No idea.')

def note_write(request):
	if request.method == 'POST':
		form = SignForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			deathnote = form.cleaned_data['deathnote']
			password = form.cleaned_data['password']
			user = User.objects.create_user(username = email, password = password)
			user.save()
			piece = encipher('write', email, deathnote, password)
			return render_to_response('confirmation.htm', {'user':form['email'], 'piece':piece})
	else:
		form = SignForm()
	return render_to_response('home.htm', {'form':form}, context_instance = RequestContext(request))

def note_edit_auth(request):
	if request.method == 'POST':
		form = EditAuthForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			password = form.cleaned_data['password']
			user = auth.authenticate(username = email, password = password)
			if user.is_authenticated():
				decrypted_note = decipher('write', email, password)
				request.session['decrypted_note'] = decrypted_note
				request.session['email'] = email
				request.session['password'] = password
				request.session['user'] = user
				return HttpResponseRedirect('/note_edit')
			else:
				return HttpResponse('dafq')
	else:
		form = EditAuthForm()
	return render_to_response('editauth.htm', {'form':form}, context_instance = RequestContext(request))

def note_edit(request):
	user = request.session['user']
	if request.method == 'POST':
		form_edit = EditForm(request.POST)
		new_note = request.POST['decrypted_note']
		user = request.session['email']
		encrypted_note = encipher('edit', user, new_note, request.session['password'])
		return HttpResponse('Done!')
	elif request.method == 'GET' and user.is_authenticated():
		form_edit = EditForm({'decrypted_note' : request.session['decrypted_note']})
	return render_to_response('editnote.htm', {'form': form_edit}, context_instance = RequestContext(request))

def edit_conf(request):
	return HttpResponse('haha')

from django.shortcuts import render_to_response
from deathnote.forms import SignForm, EditAuthForm, EditForm, ReadForm
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.models import User
from deathnote.functions import encipher, decipher
from deathnote.functions import *
from django.db import IntegrityError
from django.core.mail import send_mail
from django import forms
from django.core import validators


def home(request):
	try:
		response = 'Requested through ' + str(request.META['HTTP_USER_AGENT']) + ' browser.'
		return render_to_response('home.htm')
	except KeyError:
		return HttpResponse('No idea.')

def note_write(request):
	specialmsg = ''
	if request.method == 'POST':
		form = SignForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			deathnote = form.cleaned_data['deathnote']
			password = form.cleaned_data['password']
			ntrustees = form.cleaned_data['ntrustees']
			try:
				user = User.objects.create_user(username = email, password = password)
				user.save()
			except IntegrityError:
				specialmsg = 'User already exists!'
				form = SignForm(request.POST)
				return render_to_response('new.htm', {'form':form, 'specialmsg':specialmsg}, context_instance = RequestContext(request))
			piece = encipher('write', email, deathnote, password, ntrustees)
			send_mail('Deathnote update', 'Your note is saved. Your read only key for distribution is:\n ' + ''.join(piece[:]), 'save.my.deathnote@gmail.com',
    [email], fail_silently=False)
			return render_to_response('confirmation.htm', {'user':email, 'piece':piece})
	else:
		form = SignForm()
	return render_to_response('new.htm', {'form':form, 'specialmsg':specialmsg}, context_instance = RequestContext(request))

def note_edit_auth(request):
	if request.method == 'POST':
		form = EditAuthForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			password = form.cleaned_data['password']
			user = auth.authenticate(username = email, password = password)
			if user and user.is_authenticated():
				decrypted_note = decipher('write', email, password)

				request.session['decrypted_note'] = decrypted_note
				request.session['email'] = email
				request.session['password'] = password
				auth.login(request, user)
				return HttpResponseRedirect('/note_edit')
			else:
				return HttpResponse('User or password is either incorrect or does not exist.')
	else:
		form = EditAuthForm()
	return render_to_response('editauth.htm', {'form':form}, context_instance = RequestContext(request))

def note_edit(request):
	if request.method == 'POST' and request.user.is_authenticated():
		form_edit = EditForm(request.POST)
		new_note = request.POST['decrypted_note']
		user = request.session['email']
		encipher('edit', user, new_note, request.session['password'])
		auth.logout(request)
		return HttpResponse('Done!')
	elif request.method == 'GET' and request.user.is_authenticated():
		form_edit = EditForm({'decrypted_note' : request.session['decrypted_note']})
	else:
		return HttpResponse('User not authenticated.')
	return render_to_response('editnote.htm', {'form': form_edit}, context_instance = RequestContext(request))

def edit_conf(request):
	return HttpResponse('haha')

def note_read_auth(request):
	if request.method == 'POST':
		form_read = ReadForm(request.POST)
		if form_read.is_valid():
			email_deceased = form_read.cleaned_data['email_deceased']
			piece = form_read.cleaned_data['piece']
			note = decipher('read', email_deceased, piece)
			if not note:
				return HttpResponse('Username/Password is/are incorrect or does/do not exist.')
			return render_to_response('readnote.htm', {'note': note}, context_instance = RequestContext(request))
	else:
			form_read = ReadForm()
	return render_to_response('readauth.htm', {'form': form_read}, context_instance = RequestContext(request))

def note_read(request):
	form = ReadForm()
	if request.method == 'POST':
		del request.session[:]
	return render_to_response('readauth.htm', {'form': form}, context_instance = RequestContext(request))

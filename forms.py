from django import forms

class SignForm(forms.Form):
	name = forms.CharField(label = 'Name')
	email = forms.EmailField(required = False)
	password = forms.CharField( widget = forms.PasswordInput(render_value = False), label = "Password")
	deathnote = forms.CharField(widget = forms.Textarea)
	

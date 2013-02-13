from django import forms

class SignForm(forms.Form):
	email = forms.EmailField()
	password = forms.CharField( widget = forms.PasswordInput(render_value = False), label = "Password")
	deathnote = forms.CharField(widget = forms.Textarea)
	ntrustees = forms.IntegerField(label = 'Number of Trustees')
	

class ReadForm(forms.Form):
	email = forms.EmailField(label = "Email of the deceased")
	key_read = forms.CharField(label = "Key given to you by the deceased")

class EditAuthForm(forms.Form):
        email = forms.EmailField(label = "Email of the deceased")
	password = forms.CharField(widget = forms.PasswordInput(render_value = False), label = "Password")
	
class EditForm(forms.Form):
	decrypted_note = forms.CharField(widget = forms.Textarea)

class ReadForm(forms.Form):
	email_deceased = forms.EmailField()
	piece = forms.CharField( widget = forms.PasswordInput(render_value = False), label = 'Piece')

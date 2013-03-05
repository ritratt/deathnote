from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from pbkdf2 import PBKDF2
import random
import string
from userdata.models import Deathbook

	
def generatekey(password, IV):
   		key = PBKDF2(password, IV).read(32)
        	return key


def ncrypt(password, payload, iv, ENCODE_FLAG):
	key = generatekey(password, iv)
	cipher = AES.new(key, AES.MODE_CFB, iv)
	encrypted = cipher.encrypt(payload)
	if ENCODE_FLAG:
		encrypted = encrypted.encode('base64')
	return encrypted


def dcrypt(password, payload, iv, DECODE_FLAG):
	if DECODE_FLAG:
		payload = payload.decode('base64')
	key = generatekey(password, iv)
	cipher = AES.new(key, AES.MODE_CFB, iv)
	decrypted = cipher.decrypt(payload)
	return decrypted

def encipher(mode, user_email, note, password, ntrustees = 1):
	
	if mode == 'write':
		#Encrypt note with user's password.
		iv_write = SHA256.new(str(random.randint(0, 2**60))).hexdigest()[0:16]
		encrypted_note = ncrypt(password, note, iv_write, 1)

		#Second encryption to enable bereaved to view deathnote.
		ascii_printable = list(string.letters + string.digits + '`~!@#$%^&*()-_=+[{]}\|;:''",<.>/?')
		piece = []
		with open('words.txt') as f:
			words = f.read()
		words = words.split('\n')
		size = len(words)
		for i in range(ntrustees):
				piece.append(words[random.randint(0,size)])
		password_read = ''.join(piece[:])
		iv_read = SHA256.new(str(random.randint(0, 2**60))).hexdigest()[0:16]
		encrypted_note_read = ncrypt(password_read, note, iv_read, 1) 
		

		#Encrypt the "piece" with the user's password so that it can be used to edit the read-only encrypted note in the future.
		encrypted_piece = ncrypt(password, password_read, iv_write, 1)
		piece_hash = SHA256.new(password_read).hexdigest()

		#Create row in the database for the user with all the data.
		userdata_row = Deathbook(user_email = user_email, deathnote_write = encrypted_note, iv_write = iv_write,deathnote_read = encrypted_note_read, iv_read = iv_read, piece_hash = piece_hash, encrypted_piece = encrypted_piece)
		userdata_row.save()
		return piece

	elif mode == 'edit':
		#Retrieve encrypted read only password i.e. piece.
		temp_row = Deathbook.objects.get(user_email = user_email)
		encrypted_piece = temp_row.encrypted_piece
		iv_write = temp_row.iv_write
		piece = dcrypt(password, encrypted_piece, iv_write, 1)

		#Replace old encrypted read only note with the new note encrypted with the piece retrieved earlier.
		iv_read = temp_row.iv_read
		encrypted_note_read = ncrypt(piece, note, iv_read, 1)
		temp_row.deathnote_read = encrypted_note_read
		
		#Encrypt and replace old encrypted write note with the new one.
		iv_write = temp_row.iv_write
		encrypted_note_write = ncrypt(password, note, iv_write, 1)
		temp_row.deathnote_write = encrypted_note_write
		temp_row.save()
		return encrypted_note_read
	else:
		return None
		
			
def decipher(mode, user_email, password):
	if mode == 'write':
		userdata_row = Deathbook.objects.get(user_email = user_email)
		encrypted_note_write = userdata_row.deathnote_write
		encrypted_note_write = encrypted_note_write.decode('base64')
		iv_write = userdata_row.iv_write
		key = generatekey(password, iv_write)
		cipher = AES.new(key, AES.MODE_CFB, iv_write)
		decrypted_note = cipher.decrypt(encrypted_note_write)
		return decrypted_note
		
	elif mode == 'read':
		userdata_row = Deathbook.objects.get(user_email = user_email)
		piece_hash = userdata_row.piece_hash
		hash_tocheck = SHA256.new(password).hexdigest()
		if not hash_tocheck == piece_hash:
			return False
		encrypted_note_read = userdata_row.deathnote_read
		iv_read = userdata_row.iv_read
		decrypted_note = dcrypt(password, encrypted_note_read, iv_read, 1)
		return decrypted_note



from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from pbkdf2 import PBKDF2
import random
import string
import redis
from userdata.models import Deathbook

	
def generatekey(password, IV):
   		key = PBKDF2(password, IV).read(32)
        	return key

def encipher(mode, user_email, note, password):
	
	#Encrypt note.
	if mode == 'write':
		iv = SHA256.new(str(random.randint(0, 2**60))).hexdigest()[0:16]
		key = generatekey(password, iv)
		cipher = AES.new(key, AES.MODE_CFB, iv)
		encrypted_note = cipher.encrypt(note)
		encrypted_note = encrypted_note.encode('base64')

		#Second encryption to enable bereaved to view deathnote.
		ascii_printable = list(string.letters + string.digits + '`~!@#$%^&*()-_=+[{]}\|;:''",<.>/?')
		password_read = ''.join(random.choice(ascii_printable) for i in range(32))
		iv_read = SHA256.new(str(random.randint(0, 2**60))).hexdigest()[0:16]
		key_read = generatekey(password_read, iv_read)
		cipher_read = AES.new(key_read, AES.MODE_CFB, iv_read)
		encrypted_note_read =  cipher_read.encrypt(note)
		encrypted_note_read = encrypted_note_read.encode('base64')
		piece = iv_read + password_read
		piece_cipher = AES.new(key,AES.MODE_CFB, iv)
		encrypted_piece = piece_cipher.encrypt(piece)
		encrypted_piece = encrypted_piece.encode('base64')
		piece_hash = SHA256.new(piece).hexdigest()
		userdata_row = Deathbook(user_email = user_email, deathnote_write = encrypted_note, iv_write = iv,deathnote_read = encrypted_note_read, iv_read = iv_read, piece_hash = piece_hash, encrypted_piece = encrypted_piece)
		userdata_row.save()
		return piece

	#nonsense?
	elif mode == 'read':
		temp_row = Deathbook.objects.get(user_email = user_email)
		encrypted_note_read
		iv_read = temp_row.iv_read
		password = password[15:]
		key_read = generatekey(password, iv_read)
		cipher_read = AES.new(key_read, AES.MODE_CFB, iv_read)
		
	#Key for bereaved. Hash it for storing in database.
	elif mode == 'edit':
		temp_row = Deathbook.objects.get(user_email = user_email)
		encrypted_piece = temp_row.encrypted_piece
		encrypted_piece = encrypted_piece.decode('base64')
		iv_write = temp_row.iv_write
		key_piece = generatekey(password, iv_write)
		piece_cipher = AES.new(key_piece, AES.MODE_CFB, iv_write)
		piece = piece_cipher.decrypt(encrypted_piece)

		iv_read = temp_row.iv_read
		key_read = generatekey(piece[16:], iv_read)
		cipher_read = AES.new(key_read, AES.MODE_CFB, iv_read)
		encrypted_note_read = cipher_read.encrypt(note)
		encrypted_note_read = encrypted_note_read.encode('base64')
		temp_row.deathnote_read = encrypted_note_read
		
		iv_write = temp_row.iv_write
		key_write = generatekey(password, iv_write)
		cipher_write = AES.new(key_write, AES.MODE_CFB, iv_write)
		encrypted_note_write = cipher_write.encrypt(note)
		encrypted_note_write = encrypted_note_write.encode('base64')
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
		encrypted_note_read = encrypted_note_read.decode('base64')
		iv_read = userdata_row.iv_read
		key = generatekey(password[16:], iv_read)
		print password[16:]
		cipher = AES.new(key, AES.MODE_CFB, iv_read)
		decrypted_note = cipher.decrypt(encrypted_note_read)
		return decrypted_note

def encrypt_write():
	iv = SHA256.new(str(random.randint(0, 2**60))).hexdigest()[0:16]
        key = generatekey(password, iv)
        cipher = AES.new(key, AES.MODE_CFB, iv)
        encrypted_note = cipher.encrypt(note)
        encrypted_note = encrypted_note.encode('base64')

def encrypt_write_first():
	ascii_printable = list(string.letters + string.digits + '`~!@#$%^&*()-_=+[{]}\|;:''",<.>/?')
        password_read = ''.join(random.choice(ascii_printable) for i in range(32))
        iv_read = SHA256.new(str(random.randint(0, 2**60))).hexdigest()[0:16]
        key_read = generatekey(password_read, iv_read)
        cipher_read = AES.new(key_read, AES.MODE_CFB, iv_read)
        encrypted_note_read =  cipher_read.encrypt(note)
        encrypted_note_read = encrypted_note_read.encode('base64')
        piece = iv_read + password_read
        piece_cipher = AES.new(key,AES.MODE_CFB, iv)
        encrypted_piece = piece_cipher.encrypt(piece)
        encrypted_piece = encrypted_piece.encode('base64')
        piece_hash = SHA256.new(piece).hexdigest()

def encrypt_edit():
	temp_row = Deathbook.objects.get(user_email = user_email)
        encrypted_piece = temp_row.encrypted_piece
        encrypted_piece = encrypted_piece.decode('base64')
        iv_write = temp_row.iv_write
        key_piece = generatekey(password, iv_write)
        piece_cipher = AES.new(key_piece, AES.MODE_CFB, iv_write)
        piece = piece_cipher.decrypt(encrypted_piece)
        iv_read = temp_row.iv_read
        key_read = generatekey(piece[15:], iv_read)
	cipher_read = AES.new(key_read, AES.MODE_CFB, iv_read)
	encrypted_note_read = cipher_read.encrypt(note)
	encrypted_note_read = encrypted_note_read.encode('base64')
	temp_row.encrypted_note_read = encrypted_note_read
	temp_row.save()
	return encrypted_note_read

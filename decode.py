import random, string

# https://inventwithpython.com/chapter14.html
# Code by Al Sweigart
def getTranslatedMessage(mode, message, key):
	if mode[0] == 'd':
		key = -key
		translated = ''

		for symbol in message:

			if symbol.isalpha():
				num = ord(symbol)
				num += key

				if symbol.isupper():

					if num > ord('Z'):
						num -= 26
					elif num < ord('A'):
						num += 26

				elif symbol.islower():
					if num > ord('z'):
						num -= 26
					elif num < ord('a'):
						num += 26

				translated += chr(num)
			else:
				translated += symbol
	return translated

# https://stackoverflow.com/questions/2511222/efficiently-generate-a-16-character-alphanumeric-string
def randomCode():
	x = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
	return x
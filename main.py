# Python imports
import csv
import os
import qrcode
import random
import string
import sys

# Firebase imports
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth

# Custom imports
from Tools import Event, Hacker, Time

# ---------------------------------------------------------------------------------------

# Getting the invite and badge keys
inviteKeyFile = open("untrackables/$invite.txt", "r")
INVITE_KEY = inviteKeyFile.read()

badgeKeyFile = open("untrackables/$badge.txt", "r")
BADGE_KEY = inviteKeyFile.read()

# Creating a function that generates a random code
def generateID(size=30, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

# ---------------------------------------------------------------------------------------
# EVENT METHODS
# ---------------------------------------------------------------------------------------

# Retrieving the firebase credentials and initializing the client
cred = credentials.Certificate("untrackables/cuhacking-903fa-firebase-adminsdk-ho9wm-6fda9fcc33.json")
firebase_admin.initialize_app(cred)
database = firestore.client()

# A function that gets event information from the user
def createEvent():

	# Clearing the screen
	os.system("cls")

	print("Welcome to the event creator!\nPlease input the prompted information.")
	id = input("\tEvent ID (used as a key in firebase, i.e. 'registration'): ")
	title = input("\tEvent Title (how it will appear on the schedule): ")
	location = input("\tEvent Location: ")

	print("\nThe following prompts are for the start time of the event.")
	startDay = input("\tDay (16 or 17): ")
	startHour = input("\tHour (24h time, i.e. 8:15pm is 20): ")
	startMinute = input("\tMinute (i.e. 8:15pm is 15): ")

	print("\nThe following prompts are for the end time of the event.")
	endDay = input("\tDay (16 or 17): ")
	endHour = input("\tHour (24h time, i.e. 8:15pm is 20): ")
	endMinute = input("\tMinute (i.e. 8:15pm is 15): ")

	scanStr = input("\n\tDoes this event need cuBadge scanning? (y/n): ")
	scannable = False
	if scanStr == 'y': scannable = True

	# Creating the event object
	eventObject = Event(id, title, location, Time(startDay, startHour, startMinute), Time(endDay, endHour, endMinute), scannable)

	# Displaying the input
	print("\nThe event you're about to create is as follows:\n")
	eventObject.show()
	confirm = input("\nAre you okay with this? (y/n to restart/0 to cancel event creation): ")

	# Getting the user's option
	if confirm == "0": return
	if confirm == 'y': pass
	else:
		print("Let's try again.\n")
		createEvent()

	# Sending the data off to firebase
	database.collection(u'events').document(id).set(eventObject.toDict())

	# Adding a scan status collection to the event if it's scannable
	if scannable:
		database.collection(u'events').document(id).collection(u'scanStatus').document(u'wal.gatlei@gmail.com').set({
			u'organizer': None,
			u'scanned': False
		})

# A function for deleting an event
def deleteEvent():

	# Clearing the screen
	os.system("cls")

	eventID = input("Enter the id of the event you would like to delete: ")
	# database.collection(u'events').document(eventID).collection('scanStatus').delete()
	database.collection(u'events').document(eventID).delete()

# A function for displaying all the events on the server
def displayEvents():

	# Creating a gap
	print("\n\n")

	# Getting all the events
	events = database.collection(u'events').get()

	# Displaying the events
	for event in events:
		eventObject = event.to_dict()
		print("Event ID:", event.id)
		print("\tTitle: ", eventObject['title'])
		print("\tLocation: ", eventObject['location'])
		print("\tStart: ", eventObject['start'])
		print("\tEnd: ", eventObject['end'])
		print("\tEvent uses cuBadges: ", eventObject['scannable'])

	input("\nPress Enter to return to the main menu.")

# ---------------------------------------------------------------------------------------
# HACKER METHODS
# ---------------------------------------------------------------------------------------

# Creating a transaction
batch = database.batch()

def createScanField(hackerEmail):

	# Getting all the events
	events = database.collection(u'events').get()
	scannables = [event.id for event in events if event.to_dict()['scannable']]

	# Creating a dict to represent an empty scan
	emptyScan = {
		u'organizer': None,
		u'scanned': False
	}

	# Updating all the scannable event scanStatus fields
	for eventID in scannables:
		eventRef = database.collection(u'events').document(eventID).collection(u'scanStatus').document(hackerEmail)
		batch.set(eventRef, emptyScan)

	# Committing the batch
	batch.commit()

	

# A function for making a whole user/profile set on firebase
def makeProfile(hacker, id):

	# Creating a user on firebase
	user = auth.create_user(
		email = hacker.email,
		password = id,
		uid = id,
	)

	# Creating a profile on firebase
	database.collection(u'hackers').document(hacker.email).set({
		u'email': hacker.email,
		u'id': id,
		u'name': {
			u'first': hacker.name['first'],
			u'last': hacker.name['last']
		},
		u'program': hacker.school # yes it's weird i know
	})

	createScanField(hacker.email)
	
	return user

# A function that gets the input for a new hacker
def createHacker():

	# Clearing the screen
	os.system("cls")

	print("Welcome to the hacker profile creator!\nPlease input the prompted information.")
	email = input("Hacker Email: ")
	firstName = input("First Name: ")
	lastName = input("Last Name: ")
	school = input("School: ")

	# Creating a hacker object
	hackerObject = Hacker(email, firstName, lastName, school)

	# Displaying the input
	print("\nThe hacker you're about to create is as follows:\n")
	hackerObject.show()
	confirm = input("\nAre you okay with this? (y/n to restart/0 to cancel event creation): ")

	# Getting the user's option
	if confirm == "0": return
	if confirm == 'y': pass
	else:
		print("Let's try again.\n")

	# Creating the hacker profile on firebase
	profile = makeProfile(hackerObject, generateID())
	input("\nPress Enter to continute....")
	return profile

# A function that displays an invite code given an email
def createQRCode(key, email, id):

	# Changing the color based on the
	color = "black"
	code = INVITE_KEY + "|" + email + "|" + id

	if key == BADGE_KEY:
		color = "#C8102E"
		code = INVITE_KEY + "|" + email

	badgeCode = qrcode.QRCode(
		version=None,
		error_correction=qrcode.constants.ERROR_CORRECT_L,
		box_size=10,
		border=4,
	)
	badgeCode.add_data(code)
	badgeCode.make(fit=True)

	# Creating the image
	return badgeCode.make_image(fill_color=color, back_color="white")

def generateInviteCode():

	# Clearing the screen
	os.system("cls")

	# Getting the requested email
	email = input("Enter the hacker's email: ")

	user = ""
	try:
		user = auth.get_user_by_email(email)
	except:
		print("That's not an email in the database")
		input("\nPress Enter to return to the main menu.")
		return

	# Creating the actual QR code
	imageFile = createQRCode(INVITE_KEY, user.email, user.uid)
	imageFile.save(r'inviteCodes/' + user.email + '.png')

	print("The invite code was saved at inviteCodes/" + user.email + ".png.")
	input("\nPress Enter to return to the main menu.")

# A function that displays a cuBadge given an email
def generatecuBadge():

	# Clearing the screen
	os.system("cls")

	# Getting the requested email
	email = input("Enter the hacker's email: ")

	user = ""
	try:
		user = auth.get_user_by_email(email)
	except:
		print("That's not an email in the database")
		input("\nPress Enter to return to the main menu.")
		return

	# Creating the actual QR code
	imageFile = createQRCode(BADGE_KEY, user.email, " ")
	imageFile.save(r'cuBadges/' + user.email + '.png')

	print("The invite code was saved at cuBadges/" + user.email + ".png.")
	input("\nPress Enter to return to the main menu.")

# ---------------------------------------------------------------------------------------
# DANGEROUS METHODS
# ---------------------------------------------------------------------------------------

def uploadCSV():
	
	# Clearing the screen
	os.system("cls")

	print("Uploading the csv. This may take a minute or two.")

	# Reading the csv
	with open("untrackables/hackerInfo.csv", encoding='utf-8') as hackerFile:
		hackerList = csv.reader(hackerFile, delimiter=',')

		# Creating a profile for each hacker
		for hacker in hackerList:
			hackerObject = Hacker(hacker[2], hacker[0], hacker[1], hacker[4])
			makeProfile(hackerObject, generateID())
			print("\nUploaded:")
			hackerObject.show()

	input("\nPress Enter to return to the main menu.")

def generatAllInvites():

	# Clearing the screen
	os.system("cls")

	print("Generating invite codes. This may take a minute or two.")

	# Feeding all the emails to the generator
	hackers = database.collection(u'hackers').get()
	for hacker in hackers:
		user = auth.get_user_by_email(hacker.id)
		imageFile = createQRCode(INVITE_KEY, user.email, user.uid)
		imageFile.save(r'inviteCodes/' + user.email + '.png')

	print("All the invite codes have been saved in inviteCodes/")
	input("\nPress Enter to return to the main menu.")

# ---------------------------------------------------------------------------------------

NUM_OPTIONS = 9
def mainMenu():

	# Clearing the screen
	os.system("cls")

	# Setting up an options system
	option = ""
	validOptions = [x for x in range(NUM_OPTIONS)]

	# Asking the user to choose an option
	while (True):

		# Printing the options
		print("cuAdmin has started. What would you like to do?\nEnter a number to select an option.\n")
		print("Event Related Commands")
		print("\t0: Quit program")
		print("\t1: Create Event")
		print("\t2: Delete Event")
		print("\t3: Display Events")
		print("\nHacker Commands")
		print("\t4: Create Hacker")
		print("\t5: Generate Invite Code")
		print("\t6: Generate cuBadge Code")
		print("One time only, very dangerous commands")
		print("\t7: Upload csv")
		print("\t8: Generate all the invite codes")

		# Trying to get a valid option
		try:
			option = int(input("\nYour selection: "))
			if (option not in validOptions):
				print("That's not a valid option, try again.\n")
			else:
				break
		except:
			print("That's not a valid option, try again.\n")

	# Going through the options
	if option == 0: sys.exit(0)
	elif option == 1: createEvent()
	elif option == 2: deleteEvent()
	elif option == 3: displayEvents()
	elif option == 4: createHacker()
	elif option == 5: generateInviteCode()
	elif option == 6: generatecuBadge()
	elif option == 7: uploadCSV()
	elif option == 8: generatAllInvites()

	# Looping the program until the user quits
	mainMenu()


# Starting the program
mainMenu()
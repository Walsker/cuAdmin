# Python imports
import csv
import os
import sys

# Firebase imports
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Custom imports
from Tools import Event, Time

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

	input("\nPress Enter to continute....")

# ---------------------------------------------------------------------------------------
# HACKER METHODS
# ---------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------

NUM_OPTIONS = 4
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
		print("\t0: Quit program")
		print("\t1: Create Event")
		print("\t2: Delete Event")
		print("\t3: Display Events")

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

	# Looping the program until the user quits
	mainMenu()


# Starting the program
mainMenu()
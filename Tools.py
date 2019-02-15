# Python imports
import datetime

# A class for storing the time
# Uses 24h time
class Time:
	def __init__(self, day, hour, minute):
		self.day = int(day)
		self.hour = int(hour)
		self.minute = int(minute)

	def padDigit(self, digit):
		if digit >= 10: return str(digit)
		else: return '0' + str(digit)
		
	def toString(self):
		meridian = "AM"
		adjustedHour = 0

		# Checking if it's am or pm
		if self.hour >= 12:
			meridian = "PM"
			adjustedHour = self.hour - 12
		else:
			adjustedHour = self.hour

		timeString = str(adjustedHour) + ":" + self.padDigit(self.minute) + " " + meridian
		return "February " + str(self.day) + "th at " + timeString

	def toDateTime(self):
		return datetime.datetime(2019, 2, self.day, self.hour, self.minute)



# A class for storing events easily
class Event:
	def __init__(self, id, title, location, start, end, scannable):
		self.id = id
		self.title = title
		self.location = location
		self.start = start
		self.end = end
		self.scannable = scannable

	def show(self):
		print("Event ID: ", self.id)
		print("Event Title: ", self.title)
		print("Event Location: ", self.location)
		print("Event Start Time: ", self.start.toString())
		print("Event End Time: ", self.end.toString())
		print("Event scans cuBadges: ", self.scannable)

	def toDict(self):
		return {
			u'title': self.title,
			u'location': self.location,
			u'start': self.start.toDateTime(),
			u'end': self.end.toDateTime(),
			u'scannable': self.scannable
		}
import requests
import re
import time
import pywapi
import datetime

from bs4 import BeautifulSoup
from messageSender import messageHandler

def getWeather(zipCode, options=[], units="metric"):
	"""
	Uses the pywapi module to extract the weather from the given zipCode

	Pywapi redirects the request to Weather.com and returns an unorganized dictionary

	@jgong 10/7/2016 passing
	"""
	weatherInformationDictionary = pywapi.get_weather_from_weather_com(str(zipCode), units)

	if options:
		todaysWeatherString = getVerboseWeather(weatherInformationDictionary, options)
	else:
		todaysWeatherString = getTodaysWeather(weatherInformationDictionary)

	return todaysWeatherString

def getTodaysWeather(weatherDictionary):
	"""
	Takes in a dictionary of weather information and parses it to form
	a neatly formatted string of the day's weather

	@jgong 10/7/2016 passing
	"""

	todaysDate 			= datetime.datetime.now().strftime("%Y-%m-%d")
	todaysWeather		= weatherDictionary['current_conditions']

	currentTemperature 	= str((int(todaysWeather['temperature']) * 1.8) + 32)
	currentConditions 	= str(todaysWeather['text']).lower()

	# Add more potential pieces of information we could gather e.g
	# wind, nearest station, most recent update
	combinedInformation = "Your weather for %s is %s with a temperature of %s degrees Fahrenheit." \
								% (todaysDate, currentConditions, currentTemperature)
	return combinedInformation

def getVerboseWeather(weatherDictionary, options):
	"""
	Takes in a dictionary of weather information as well as a list of options
	to create a more verbose formatted string of weather information

	Options may contain:
	- extraDailyInformation : 
		* time of last update
		* station information came from 
		* wind information
	- weeklyForecast :
		* basic Information for the rest of the weekdays 
	- location :
		* basic locational information for the provided zip code
	"""
	allWeatherInformation = [] # Contains completed strings for each provided option

	if "extraDailyInformation" in options:
		allWeatherInformation.append(parseForExtraDailyInfo(weatherDictionary))
	if "weeklyForecast" in options:
		allWeatherInformation.append(parseForWeeklyForecastInfo(weatherDictionary))
	if "location" in options:
		allWeatherInformation.append(parseForLocationInfo(weatherDictionary))

	combinedInformation = ' '.join(allWeatherInformation)
	return combinedInformation

def parseForExtraDailyInfo(weatherDictionary):
	"""
	Parses the weather dictionary for slightly more basic weather information

	@jgong 10/7/2016 passing
	"""
	todaysDate 			= datetime.datetime.now().strftime("%Y-%m-%d")
	todaysWeather		= weatherDictionary['current_conditions']

	currentTemperature 		= str((int(todaysWeather['temperature']) * 1.8) + 32)	
	currentConditions 		= str(todaysWeather['text']).lower() # i.e sunny, windy, etc
	lastUpdateTime			= str(todaysWeather['last_updated'])
	nearestWeatherStation	= str(todaysWeather['station'])
	windSpeed				= str(todaysWeather['wind']['speed'])
	windDirection			= str(todaysWeather['wind']['text'])

	combinedInformation = "Your weather for %s is: %s with a temperature of: %s." % (todaysDate, currentConditions, currentTemperature)
	combinedInformation += "This information was last updated at: %s from: %s. " % (lastUpdateTime, nearestWeatherStation)
	combinedInformation += "Today's wind speed is: %s MPH in the %s direction." % (windSpeed, windDirection)

	return combinedInformation

def parseForWeeklyForecastInfo(weatherDictionary):
	"""
	Parses the weather dictionary for basic forecasts on the entire week

	@jgong 10/7/2016 passing
	"""
	weeklyForecast 		 = weatherDictionary['forecasts']
	weeklyForecastString = []

	for dailyInformationDictionary in weeklyForecast:
		weekday 			= str(dailyInformationDictionary['day_of_week'])
		date 				= str(dailyInformationDictionary['date'])
		dailyLow			= str(((int(dailyInformationDictionary['low']) * 1.8)) + 32)
		dailyHigh			= str(((int(dailyInformationDictionary['high']) * 1.8)) + 32)
		daytimeConditions 	= str(dailyInformationDictionary['day']['brief_text'])
		nightConditions 	= str(dailyInformationDictionary['night']['brief_text'])

		dailyCombinedInformation = "On %s, %s with a low of %s and a high of %s. During the day it will be %s and during the evening %s." \
										% (weekday, date, dailyLow, dailyHigh, daytimeConditions, nightConditions)
		weeklyForecastString.append(dailyCombinedInformation)

	return ' '.join(weeklyForecastString)

def parseForLocationInfo(weatherDictionary):
	"""
	Parses the weather dictionary for basic information on the forecast's location

	@jgong 10/7/2016 passing
	"""
	todaysLocation = weatherDictionary['location']

	latitude 	= str(todaysLocation['lat'])
	longitude	= str(todaysLocation['lon'])
	city 		= str(todaysLocation['name'])

	combinedInformation = "This forecast was provided for %s at the coordinates of (%s, %s)." % (city, latitude, longitude)

	return combinedInformation

def populateListOfRecipients(fileName):
	""" 
	Parses through recipients.txt in order to populate a dictionary of all users 
	to send weather information.

	Assumes the list is well-formatted as a CSV with:
	Name,PhoneNumber,Carrier

	@jgong 10/7/2016 passing
	"""
	recipients = {}

	with open(fileName, 'r') as recipientFile:
		for line in recipientFile.readlines():
			name, number, carrier = getUserInformation(line)
			recipients[name] = {'number' : number, 'gateway' : carrier}

	return recipients 

def getUserInformation(line):
	"""
	Sanitizes a line from the recipients.txt file and breaks it apart

	@jgong 10/7/2016 passing
	"""
	sanitizedLine = line.replace(' ', '').replace('\n', '').split(',')

	name 	= sanitizedLine[0]
	number 	= sanitizedLine[1]
	carrier = sanitizedLine[2]

	return name, number, carrier

def getUsernameAndPassword(fileName):
	"""
	Parses through credentials.txt to receive the stored username and 
	password of the client through which weather information is sent

	@jgong 10/7/2016 passing
	"""
	with open(fileName, 'r') as credentialsFile:
		username = credentialsFile.readline().replace('\n','')
		password = credentialsFile.readline().replace('\n','')

	return username, password

def promptUserForLocation():
	"""
	Entry point for the program -- gives the user an introduction of 
	this program's functionality and asks the user to provide basic info
	"""
	print "Hello! Welcome to your personal weather assistant. Please follow the prompts below to get your personal weather report!\n"

	zipCode 		= input("What is the zipcode of where you would like weather for?\n")
	receiveTexts	= str(input("Would you like to receive texts? If not, you will receive an email message.\n")).lower() in {'true', 'y', 'yes'}
	recipientEmail	= ""

	if receiveTexts:
		fullName 	= input("Please enter your full name\n")
		phoneNumber = input("What is your phone number? Enter only the digits along with the 3 digit area code\n")
		gateway	 	= input("Please enter your carrier\n").upper()
		# updateRecipientsFile(fullName, phoneNumber, gateway)
	else: 
		recipientEmail = input("What email would you like to receive your weather at?\n")

	print "Thank you! You will receive your weather shortly."
	return zipCode, receiveTexts, recipientEmail


def main():
	zipCode, receiveTexts, recipientEmail 	= promptUserForLocation()
	username, password 						= getUsernameAndPassword('credentials.txt')
	messageClient 							= messageHandler(username, password)
	todaysWeather 							= getWeather(zipCode)

	if receiveTexts:
		recipients = populateListOfRecipients('recipients.txt')

		for recipient in recipients:
			messageClient.sendTextMessage(recipients[recipient]['number'], recipients[recipient]['gateway'], todaysWeather)
	else:
		messageClient.sendEmailMessage(recipientEmail, todaysWeather)

main()
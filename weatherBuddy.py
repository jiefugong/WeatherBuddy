import requests
import re
import time
import pywapi
import datetime

from bs4 import BeautifulSoup
from messageSender import messageHandler

def getWeather(zipCode, units="metric", options=[]):
	"""
	Uses the pywapi module to extract the weather from the given zipCode

	Pywapi redirects the request to Weather.com and returns an unorganized dictionary
	"""
	weatherInformationDictionary = pywapi.get_weather_from_weather_com(zipCode, units)
	todaysWeatherString = getTodaysWeather(weatherInformationDictionary)

	if options:
		todaysWeatherString = getVerboseWeather(weatherInformationDictionary, options)
	else:
		todaysWeatherString = getTodaysWeather(weatherInformationDictionary)

	return todaysWeatherString

def getTodaysWeather(weatherDictionary):
	"""
	Takes in a dictionary of weather information and parses it to form
	a neatly formatted string of the day's weather
	"""

	todaysDate 			= datetime.datetime.now().strftime("%Y-%m-%d")
	todaysWeather		= weatherDictionary['current_conditions']

	currentTemperature 	= str(todaysWeather['temperature']) # in celsius
	currentConditions 	= str(todaysWeather['text'])

	# Add more potential pieces of information we could gather e.g
	# wind, nearest station, most recent update
	combinedInformation = ''.join(["Your weather for ", todaysDate, " is ", currentConditions, " with a temperature of ", currentTemperature])
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
	"""
	todaysDate 			= datetime.datetime.now().strftime("%Y-%m-%d")
	todaysWeather		= weatherDictionary['current_conditions']

	currentTemperature 		= str(todaysWeather['temperature']) # in celsius
	currentConditions 		= str(todaysWeather['text']) # i.e sunny, windy, etc
	lastUpdateTime			= str(todaysWeather['last_updated'])
	nearestWeatherStation	= str(todaysWeather['station'])
	windSpeed				= str(todaysWeather['wind']['speed'])
	windDirection			= str(todaysWeather['wind']['text'])

	combinedInformation = ''.join([
		"Your weather for ", todaysDate, " is: ", currentConditions, " with a temperature of: ", currentTemperature, ".\n", \
		"This information was last updated at: ", lastUpdateTime, " from: ", nearestWeatherStation, ".\n", \
		"Today's wind speed is: ", windSpeed, " in the direction of: ", windDirection, "."
	])

	return combinedInformation

def parseForWeeklyForecastInfo(weatherDictionary):
	"""
	Parses the weather dictionary for basic forecasts on the entire week
	"""
	weeklyForecast 		 = weatherDictionary['forecasts']
	weeklyForecastString = ""

	for dailyInformationDictionary in weeklyForecast:
		weekday 			= str(dailyInformationDictionary['day_of_week'])
		date 				= str(dailyInformationDictionary['date'])
		dailyLow			= str(dailyInformationDictionary['low'])
		dailyHigh			= str(dailyInformationDictionary['high'])
		daytimeConditions 	= str(dailyInformationDictionary['day']['brief_text'])
		nightConditions 	= str(dailyInformationDictionary['night']['brief_text'])

		dailyCombinedInformation = ''.join(["On ", weekday, ", ", date, " with a low of: ", daily low, \
			" and a high of ", dailyHigh, ". During the day it will be ", daytimeConditions " and during the evening ", nightConditions, ".\n"])
		weeklyForecastString.append(dailyCombinedInformation)

	return weeklyForecastString

def parseForLocationInfo(weatherDictionary):
	"""
	Parses the weather dictionary for basic information on the forecast's location
	"""
	todaysLocation = weatherDictionary['location']

	latitude 	= str(todaysLocation['lat'])
	longitude	= str(todaysLocation['lon'])
	city 		= str(todaysLocation['name'])

	combinedInformation = ''.join(["This forecast was provided for: ", city, \
		" at the coordinates of: (", latitude, ", ", longitude, ")\n"])

	return combinedInformation

def populateListOfRecipients(fileName):
	""" 
	Parses through recipients.txt in order to populate a dictionary of all users 
	to send weather information.

	Assumes the list is well-formatted as a CSV with:
	Name,PhoneNumber,Carrier
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
	"""
	sanitzedLine = line.replace(' ', '').split(',').replace('\n', '')

	name 	= sanitizedLine[0]
	number 	= sanitizedLine[1]
	carrier = sanitizedLine[2]

	return name, number, carrier

def getUsernameAndPassword(fileName):
	"""
	Parses through credentials.txt to receive the stored username and 
	password of the client through which weather information is sent
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
	print "Hello! Welcome to your personal weather assistant. Please follow the \
		prompts below to get your personal weather report!"

	zipCode 		= input("What is the zipcode of where you would like weather for?\n")
	receiveTexts	= input("Would you like to receive texts? If not, you will receive an email message.\n").lower() == 'true'
	recipientEmail	= ""

	if receiveTexts:
		fullName 	= input("If you have not already entered your information in recipients.txt, please enter your full name\n")
		phoneNumber = input("What is your phone number? Enter only the digits along with the 3 digit area code\n")
		gateway	 	= input("Please enter your carrier\n").upper()
		updateRecipientsFile(fullName, phoneNumber, gateway)
	else: 
		recipientEmail = input("What email would you like to receive your weather at?\n")

	print "Thank you! You will receive your weather shortly."
	return zipCode, recieveTexts, recipientEmail


def main():
	zipCode, receiveTexts, recipientEmail 	= promptUserForLocation()
	username, password 						= getUsernameAndPassword('credentials.txt')
	messageClient 							= messageHandler(username, password)
	todaysWeather 							= getWeather(zipCode)

	if receiveTexts:
		recipients = populateListOfRecipients('recipients.txt')

		for recipient in recipients:
			messageClient.sendTextMessage(recipient['number'], recipient['gateway'], todaysWeather)
	else:
		messageClient.sendEmailMessage(recipientEmail, todaysWeather)

main()

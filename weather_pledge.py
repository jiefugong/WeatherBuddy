import smtplib
import requests
import re
import time
import pywapi
import datetime

from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 

WEEKDAY_PARSE_START = 0
WEEKDAY_PARSE_END   = 5
DEFAULT_INDEX_VALUE = 2
UNDEFINED_VAL		= -1
CURRENT_CONDITIONS  = 'Current Conditions'
DEFAULT_REGEX_P		= '[\'\<\>\/\:\.\-]'

SMS_GATEWAYS = {
	'AT&T' 		: 'txt.att.net',
	'CRICKET' 	: 'mms.cricketwireless.net',
	'SPRINT' 	: 'pm.sprint.com',
	'TMOBILE'	: 'tmomail.net',
	'VERIZON' 	: 'vtext.com',
	'VIRGIN' 	: 'vmobl.com'
}

WEEKDAYS = {
	0 : 'Mon',
	1 : 'Tue',
	2 : 'Wed',
	3 : 'Thu',
	4 : 'Fri', 
	5 : 'Sat',
	6 : 'Sun'
}

def prepare_message(text, subject, destination, source_email):
	""" Uses MIMEMultipart to create an email message """
	message = MIMEMultipart()
	message['From']     = source_email 
	message['To']       = destination 
	message['Subject']  = subject 
	message.attach(MIMEText(text))
	return message

def send_email(message, destination, source_email, source_pw):
	""" Uses SMTP and login credentials to send a prepared message """ 
	mail_server = smtplib.SMTP('smtp.googlemail.com')
	mail_server.ehlo()
	mail_server.starttls()
	mail_server.ehlo()
	mail_server.login(source_email, source_pw)
	mail_server.sendmail(source_email, destination, message.as_string())
	mail_server.quit()

def send_texts(message, users, source_email, source_pw):
	""" Sends a text with the prepared message to all users specified in file """

	txt_server = smtplib.SMTP( "smtp.gmail.com", 587)
	txt_server.starttls()
	txt_server.login(source_email, source_pw)

	for user in users.keys():
		phone_number  = users[user][0]
		phone_carrier = users[user][1]
		phone_destination = phone_number + '@' + SMS_GATEWAYS[phone_carrier]
		txt_server.sendmail(source_email, phone_destination, message)
		txt_server.quit()

def is_integer(s):
	""" Determines whether or not the input is a valid integer """
	try:
		int(s)
		return True
	except ValueError:
		return False 

def celsius_to_fahrenheit(temperature):
	""" Converts the input from celsius to fahrenheit temperature """
	return str((int(temperature) * 1.8) + 32)

def get_weather(zip_code, units):
	""" Uses the pywapi module to extract weather and parse it """ 
	weather_info = pywapi.get_weather_from_yahoo(zip_code, units)
	return parse_text(weather_info)

def find_today(all_information_about_weather):
	""" Returns a helpful string with information about the current day's weather """ 
	information_index = UNDEFINED_VAL
	temperature_in_celsius = UNDEFINED_VAL
	temperature_description = ''
	final_information = 'The weather today is: '

	for i in range(0, len(all_information_about_weather)):
		if CURRENT_CONDITIONS in all_information_about_weather[i]:
			information_index = i + 1
			break 

	parsed_line = re.sub(DEFAULT_REGEX_P, ' ', all_information_about_weather[information_index])
	find_temperature = parsed_line.split()

	for potential_temp in find_temperature:
		ascii_temperature = potential_temp.encode('ascii', 'ignore')
		if is_integer(ascii_temperature):
			temperature_in_celsius = ascii_temperature

	temperature_description = parsed_line.split(',')[0].encode('ascii', 'ignore')
	final_information += celsius_to_fahrenheit(temperature_in_celsius)
	final_information += " degrees fahrenheit and is: "
	final_information += temperature_description.lower() + ". "
	return final_information

def parse_text(weather_info):
	""" Returns a helpful string with verbose information on today's weather and sparse information on the rest of the week """ 
	current_weekday = WEEKDAYS[datetime.datetime.today().weekday()]
	all_information_about_weather = weather_info['html_description'].split('\n')
	todays_information = '\n' + find_today(all_information_about_weather)

	for line in all_information_about_weather:
		if current_weekday in line[WEEKDAY_PARSE_START : WEEKDAY_PARSE_END]:
			cleaned_weather_information = re.sub(DEFAULT_REGEX_P, ' ', line).encode('ascii', 'ignore').split()
			index_of_separator = UNDEFINED_VAL

			for i in range(0, len(cleaned_weather_information)):
				if cleaned_weather_information[i].lower() == 'high':
					index_of_separator = i 
					break 

			day = cleaned_weather_information[0]

			if index_of_separator == DEFAULT_INDEX_VALUE:
				description = cleaned_weather_information[1].lower()
			else:
				description = (cleaned_weather_information[1].lower() + " " + cleaned_weather_information[2].lower())

			high_temp = cleaned_weather_information[index_of_separator + 1]
			low_temp  = cleaned_weather_information[index_of_separator + 3]

			todays_weather = "The weather for the rest of today is going to be " + description 
			todays_weather += " with a high of " + celsius_to_fahrenheit(high_temp)
			todays_weather += " and a low of " + celsius_to_fahrenheit(low_temp)
			todays_information += todays_weather 
			break 

	return todays_information

def get_users(user_information):
	""" Parses through the lines of a designated file for receipients of texts """
	all_users = {}

	for line in user_information:
		if line[0] != '%':
			user_preferences = []
			credentials = line.split(",")
			user_preferences.append(credentials[1])
			user_preferences.append(credentials[2][0:-1])
			all_users[credentials[0]] = user_preferences

	return all_users


def main():
	source_email_credentials 	= open('credentials.txt').readline()
	source_email 				= source_email_credentials.split()[0]
	source_pw 	 				= source_email_credentials.split()[1]
	users						= get_users(open('attendees.txt').readlines())
	weather_information 		= get_weather('94704', 'metric')

	send_texts(weather_information, users, '', '')

main()

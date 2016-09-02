import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class messageHandler:

	SMSGATEWAYS = {
		'AT&T' 		: 'txt.att.net',
		'CRICKET' 	: 'mms.cricketwireless.net',
		'SPRINT' 	: 'pm.sprint.com',
		'TMOBILE'	: 'tmomail.net',
		'VERIZON' 	: 'vtext.com',
		'VIRGIN' 	: 'vmobl.com'
	}

	def __init__(self, username, password):
		self.username 		= username
		self.password 		= password

	def sendEmailMessage(self, recipientEmail, subject, message):
		"""
		Logs into the Google mail server with your initialized credentials
		and sends message to the recipientEmail
		"""
		formattedMessage = self.prepareEmailMessageFormat(recipientEmail, subject, message)

		mailServer = smtplib.SMTP('smtp.gmail.com', 587)
		mailServer.ehlo()
		mailServer.starttls()
		mailServer.ehlo()
		mailServer.login(self.username, self.password)
		# Do we need to prepare the message with MIMEMultipart?
		mailServer.sendmail(self.username, recipientEmail, formattedMessage)
		mailServer.close()

	def sendTextMessage(self, recipientNumber, smsGateway, message):
		"""
		Logs into the Google mail server and sends texts to 
		recipientNumber belonging to smsGateway with the message
		"""
		textServer = smtplib.SMTP("smtp.gmail.com", 587)
		textServer.starttls()
		textServer.login(self.username, self.password)

		try:
			fullRecipientNumber = ''.join([str(recipientNumber), "@", SMSGATEWAYS[smsGateway]])
			textServer.sendmail(self.username, fullRecipientNumber, message)
		except KeyError:
			print "Invalid SMS Gateway, please try again."
			textServer.quit()
		except Exception:
			print "Text Server failed to send your message. Check your login credentials or your destination."
			textServer.quit()

	def prepareEmailMessageFormat(self, recipientEmail, subject, message):
		"""
		Create a header for the message such that the email format is preserved
		"""
		formattedMessage 	= 'To:' + recipientEmail + '\n' + 'From: ' + self.username + '\n' + 'Subject:' + subject + '\n'
		formattedMessage	= formattedMessage + '\n ' + message + ' \n\n'
		return formattedMessage
import unittest

from messageSender import messageHandler

class SendMessageTest(unittest.TestCase):

	def testSendEmail(self):
		"""
		Tests to see if we can send an email successfully
		"""
		#Todo: Read test information from file
		with open('../credentials.txt') as f:
			username, password = f.readline().rstrip('\n'), f.readline().rstrip('\n')
		messageClient = messageHandler(username, password)
		self.assertEquals(messageClient.sendEmailMessage('jgong@berkeley.edu', 'Test Email', 'Hello World!'), {})

	def testSendEmail(self):
		"""
		Tests to see if we can send a text message successfully
		"""
		#Todo: Read test information from file
		with open('../credentials.txt') as f:
			username, password = f.readline().rstrip('\n'), f.readline().rstrip('\n')
		messageClient = messageHandler(username, password)
		self.assertEquals(messageClient.sendTextMessage('4087057358', 'AT&T', 'Hello World!'), {})

if __name__ == '__main__':
	unittest.main()
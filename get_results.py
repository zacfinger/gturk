# GTURK
# Mturk + Gmail = Gturk
# 1024 times better than Mturk
# (C)2019 Zacfinger.com

# TODO
# if no turk has responded to the HIT 
# fix async events when SQLite db updated
# search in body rather than subject line


# Following resources were helpful
# https://blog.mturk.com/tutorial-a-beginners-guide-to-crowdsourcing-ml-training-data-with-python-and-mturk-d8df4bdf2977
# https://stackoverflow.com/questions/16856647/sqlite3-programmingerror-incorrect-number-of-bindings-supplied-the-current-sta
# https://codehandbook.org/how-to-read-email-from-gmail-using-python/

import xmltodict
import boto3
import sqlite3
import config
import smtplib
import time
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

mturk = boto3.client('mturk',
   aws_access_key_id = config.aws_access_key_id,
   aws_secret_access_key = config.aws_secret_access_key,
   region_name='us-east-1',
   endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
)

def newCode(input_string):
	return input_string

conn = sqlite3.connect('database')
c = conn.cursor()
#c.execute('SELECT * FROM hits')

for row in c.execute('SELECT * FROM hits'):
	me = row[0]
	my_password = row[1]

	# if status is 0
		# open inbox of convertist_email to see if someone sent message with code in subject line
		# for each message read and unread
			# if code sent in subject line matches the code in row
				# send response back to user with a corresponding code (use some kind of cipher)
				# set status on db to 1 and save code_2 in db
			# else mark as read/unread whatever value it was before
	# if status is 1 (meaning we have sent back email to user)
		# for each assignment ID in corresponding HIT ID
			# check to see if response from user equals code sent
				# if code_2 cipher code_1 works mark assignment as complete and delete from db
			# else if response is wrong reject assignment and delete from db

	# if email has been created, HIT task created, but no response yet from any user
	if row[3] == 0:
		# open inbox of convertist_email to see if someone sent message with code in subject line
		SMTP_SERVER = "imap.gmail.com"
		print "got into this block"
		try:
			mail = imaplib.IMAP4_SSL(SMTP_SERVER)
			mail.login(me,my_password)
			mail.select('[Gmail]/All Mail')

			type, data = mail.search(None, 'ALL')
			mail_ids = data[0]

			id_list = mail_ids.split()
			latest_email_id = int(id_list[-1])

			if row[7] == 0:
				first_email_id = int(id_list[0])	
			else:
				first_email_id = row[7]

			email_sent = 0

			# for each message read and unread
			for i in range(latest_email_id,first_email_id, -1):
				print i
				if email_sent == 0:
					typ, data = mail.fetch(i, '(RFC822)' )
					for response_part in data:
						if isinstance(response_part, tuple) and email_sent == 0:
							msg = email.message_from_string(response_part[1])
							email_subject = msg['subject']
							if email_subject is not None:
								words = email_subject.split(" ")

							for word in words:
								# if code sent in subject line matches the code in row
								# get_results.py:88: UnicodeWarning: Unicode equal comparison failed to convert both arguments to Unicode - interpreting them as being unequal
								if word == row[4]:
									print "it worked!"
									new_code = newCode(row[4])
									email_from = msg['from']
									first_char = email_from.find('<') + 1
									last_char = email_from.find('>')
									email_from = email_from[first_char:last_char]
									
									# send response back to user with a corresponding code (use some kind of cipher)
									msg = MIMEMultipart('alternative')
									msg['Subject'] = "Generated subject line" + new_code
									msg['From'] = me
									msg['To'] = email_from

									html = 'Generated email message'
									part2 = MIMEText(html, 'html')

									msg.attach(part2)

									# Send the message via gmail's regular server, over SSL - passwords are being sent, afterall
									s = smtplib.SMTP_SSL('smtp.gmail.com')
									
									# do the smtp auth; sends ehlo if it hasn't been sent already
									s.login(me, my_password)

									s.sendmail(me, email_from, msg.as_string())
									s.quit()

									# set status on db to 1 and save code_2 in db
									c.execute("UPDATE hits SET status=1, unique_code_2=?, last_email_checked=? WHERE unique_code_1=?", (new_code,i,word))
									#convertist_email, convertist_email_pw, hit_id, status, unique_code_1, unique_code_2, assignment_id, last_email_checked
									conn.commit()
									email_sent = 1
									break

						else:
							break
				else:
					break

			if email_sent == 0:
				c.execute("UPDATE hits SET last_email_checked=? WHERE unique_code_1=?", (latest_email_id,row[4]))
				conn.commit()

		except Exception, e:
			print str(e)
	# if status is 1 (meaning we have sent back email to user)
	if row[3] == 1:
		print "status is 1"
		hit_id = row[2]
		worker_results = mturk.list_assignments_for_hit(HITId=hit_id)
		print worker_results
		if worker_results['NumResults'] > 0:
			# for each assignment ID in corresponding HIT ID
			for assignment in worker_results['Assignments']:
				assignment_id = assignment['AssignmentId']
				xml_doc = xmltodict.parse(assignment['Answer'])
				turk_response = xml_doc['QuestionFormAnswers']['Answer']['FreeText']
				# check to see if response from user equals code sent
				if turk_response == row[5]:
					# if code_2 cipher code_1 works mark assignment as complete and delete from db
					mturk.approve_assignment(AssignmentId=assignment_id)
					c.execute("DELETE from hits WHERE unique_code_2=?", (turk_response,))
					conn.commit()
				else:
					mturk.reject_assignment(AssignmentId=assignment_id,RequesterFeedback="Incorrect code provided")
					c.execute("DELETE from hits WHERE unique_code_1=?", (row[4],))
		else:
			print "no responses currently"

print "finished"
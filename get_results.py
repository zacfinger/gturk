# https://blog.mturk.com/tutorial-a-beginners-guide-to-crowdsourcing-ml-training-data-with-python-and-mturk-d8df4bdf2977
# https://stackoverflow.com/questions/16856647/sqlite3-programmingerror-incorrect-number-of-bindings-supplied-the-current-sta

# You will need the following library
# to help parse the XML answers supplied from MTurk
# Install it in your local environment with
# pip install xmltodict
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

conn = sqlite3.connect('database')
c = conn.cursor()
#c.execute('SELECT * FROM hits')

for row in c.execute('SELECT * FROM hits'):
	me = row[0]
	my_password = row[1]

	# if turk not yet provided email address
	if row[3] == 0:
		# check to see if turk provided email address
		hit_id = row[2]
		print hit_id
		worker_results = mturk.list_assignments_for_hit(HITId=hit_id)
		print worker_results
		if worker_results['NumResults'] > 0:

			count = 0

			for assignment in worker_results['Assignments']:
				assignment_id = assignment['AssignmentId']
				xml_doc = xmltodict.parse(assignment['Answer'])
				turk_email = xml_doc['QuestionFormAnswers']['Answer']['FreeText']
				# send email here

				msg = MIMEMultipart('alternative')
				msg['Subject'] = "Generated subject line"
				msg['From'] = me
				msg['To'] = turk_email

				html = 'Generated email message'
				part2 = MIMEText(html, 'html')

				msg.attach(part2)

				# Send the message via gmail's regular server, over SSL - passwords are being sent, afterall
				s = smtplib.SMTP_SSL('smtp.gmail.com')
				# uncomment if interested in the actual smtp conversation
				# s.set_debuglevel(1)
				# do the smtp auth; sends ehlo if it hasn't been sent already
				s.login(me, my_password)

				s.sendmail(me, turk_email, msg.as_string())
				s.quit()

				if count == 0:

					c.execute("UPDATE hits SET turk_email=?, status=1, assignment_id=? WHERE hit_id=?", (turk_email, assignment_id, hit_id))
					#c.execute("UPDATE hits SET turk_email=?, status=1 WHERE hit_id=?", (turk_email, hit_id))
					conn.commit()

					count = count + 1
				else:
					c.execute("INSERT INTO hits(convertist_email, convertist_email_pw, hit_id, status, turk_email, assignment_id) VALUES (?,?,?,?,?,?)", (me, my_password, hit_id, 1, turk_email, assignment_id))
					conn.commit()
	# if turk provided address check to see if email received
	if row[3] == 1:
		SMTP_SERVER = "imap.gmail.com"
		print "got into thhis block"
		try:
			mail = imaplib.IMAP4_SSL(SMTP_SERVER)
			mail.login(me,my_password)
			mail.select('inbox')

			type, data = mail.search(None, 'ALL')
			mail_ids = data[0]

			id_list = mail_ids.split()
			first_email_id = int(id_list[0])
			latest_email_id = int(id_list[-1])

			for i in range(latest_email_id,first_email_id, -1):
				typ, data = mail.fetch(i, '(RFC822)' )

				for response_part in data:
					if isinstance(response_part, tuple):
						msg = email.message_from_string(response_part[1])
						email_subject = msg['subject']
						email_from = msg['from']
						first_char = email_from.find('<') + 1
						last_char = email_from.find('>')
						email_from = email_from[first_char:last_char]
						if email_from == row[4]:
							print "approve via mechanical turk API"
							mturk.approve_assignment(AssignmentId=row[5])
							c.execute("DELETE from hits WHERE assignment_id=?", (row[5],))
							conn.commit()

		except Exception, e:
			print str(e)
			# check to see if email received
			# and update HITID to 'accepted'
			# and remove from DB

print "finished"
# https://blog.mturk.com/tutorial-a-beginners-guide-to-crowdsourcing-ml-training-data-with-python-and-mturk-d8df4bdf2977

# You will need the following library
# to help parse the XML answers supplied from MTurk
# Install it in your local environment with
# pip install xmltodict
import xmltodict
import boto3
import sqlite3
import config
import smtplib
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
	# if turk not yet provided email address
	if row[3] == 0:
		# check to see if maybe the turk did provide email
		hit_id = row[2]
		print hit_id
		worker_results = mturk.list_assignments_for_hit(HITId=hit_id)
		print worker_results
		if worker_results['NumResults'] > 0:

			print worker_results
			me = row[0]
			my_password = row[1]

			for assignment in worker_results['Assignments']:
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

				c.execute("UPDATE hits SET turk_email=?, status=1 WHERE hit_id=?", (turk_email, hit_id))
				#c.execute("UPDATE hits SET turk_email=?, status=1 WHERE hit_id=?", (turk_email, hit_id))
				conn.commit()
	# if turk provided address check to see if email received
	if row[3] == 1:
		print row
		# check to see if email received
		# and update HITID to 'accepted'
		# and remove from DB
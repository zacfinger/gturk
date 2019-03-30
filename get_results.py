# You will need the following library
# to help parse the XML answers supplied from MTurk
# Install it in your local environment with
# pip install xmltodict
import xmltodict
import boto3
import sqlite3
import config

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
	hit_id = row[2]
	worker_results = mturk.list_assignments_for_hit(HITId=hit_id)
	if worker_results['NumResults'] > 0:
		for assignment in worker_results['Assignments']:
			xml_doc = xmltodict.parse(assignment['Answer'])
			turk_email = xml_doc['QuestionFormAnswers']['Answer']['FreeText']
			# send email here
			print "updating this shit"
			c.execute("UPDATE hits SET turk_email=? WHERE hit_id=?", (turk_email, hit_id))
			conn.commit()

#conn.commit()
print "updated"
#cur = conn.cursor()
#cur.execute(sql, task)
#some anser

# We are only publishing this task to one Worker
# So we will get back an array with one item if it has been completed
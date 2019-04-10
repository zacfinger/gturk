# http://www.islandtechph.com/2017/10/21/how-to-deploy-a-flask-python-2-7-application-on-a-live-ubuntu-16-04-linux-server-running-apache2/
# if user accepts hit job record timestamp and auto deny if it hits expiration date
from flask import Flask, render_template, request
import sqlite3
import boto3
import config
import random, string
import time
import decode
from random import randint
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)

MTURK_SANDBOX = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
#MTURK_SANDBOX = 'https://mturk-requester.us-east-1.amazonaws.com'

mturk = boto3.client('mturk',
   aws_access_key_id = config.aws_access_key_id,
   aws_secret_access_key = config.aws_secret_access_key,
   region_name='us-east-1',
   endpoint_url = MTURK_SANDBOX
)

#create table hits (convertist_email TEXT NOT NULL, convertist_email_pw TEXT NOT NULL, hit_id TEXT NOT NULL, status INTEGER NOT NULL, unique_code_1 TEXT NOT NULL, unique_code_2 INTEGER NOT NULL, assignment_id TEXT NOT NULL, last_email_checked INTEGER NOT NULL, time INTEGER NOT NULL);

@app.route('/', methods=["GET", "POST"])
def main():
	if request.method == "POST":

		random_code = decode.randomCode()
		random_key = randint(1, 26)
		
		convertist_email = request.form.get("convertist_email")
		convertist_email_pw = request.form.get("convertist_email_pw")

		question = open(name=dir_path+'/questions.xml',mode='r').read()

		new_hit = mturk.create_hit(
		    Title = 'Write an email to ' + convertist_email + ' and include the code ' + random_code + ' in the subject line',
		    Description = 'Write an email to ' + convertist_email + ' and include the code ' + random_code + ' in the subject line',
		    Keywords = 'text, quick, writing',
		    Reward = config.reward,
		    MaxAssignments = 1,
		    LifetimeInSeconds = 172800,
		    AssignmentDurationInSeconds = config.AssignmentDurationInSeconds,
		    AutoApprovalDelayInSeconds = config.AutoApprovalDelayInSeconds,
		    Question = question,
		)

		current_time = int(time.time())
		
		# Insert a row of data
		conn = sqlite3.connect(dir_path+'/database')
		c = conn.cursor()
		t = (convertist_email,convertist_email_pw,new_hit['HIT']['HITId'],0,random_code,random_key,'',0,current_time)
		#convertist_email , convertist_email_pw, hit_id, status, unique_code_1, unique_code_2, assignment_id, last_email_checked, time

		c.execute("INSERT INTO hits VALUES (?,?,?,?,?,?,?,?,?)", t)

		conn.commit()
		#print(c.fetchone())

		return render_template("success.html")
	# User reached route via GET (as by clicking a link or via redirect)
	else:
		return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
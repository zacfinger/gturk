from flask import Flask, render_template, request
import sqlite3
import boto3
import config
import random, string

app = Flask(__name__)

MTURK_SANDBOX = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

mturk = boto3.client('mturk',
   aws_access_key_id = config.aws_access_key_id,
   aws_secret_access_key = config.aws_secret_access_key,
   region_name='us-east-1',
   endpoint_url = MTURK_SANDBOX
)

#create table hits (convertist_email TEXT NOT NULL, convertist_email_pw TEXT NOT NULL, hit_id TEXT NOT NULL, status INTEGER NOT NULL, unique_code_1 TEXT NOT NULL, unique_code_2 TEXT NOT NULL, assignment_id TEXT NOT NULL, last_email_checked INTEGER NOT NULL);

def randomCode():
	# https://stackoverflow.com/questions/2511222/efficiently-generate-a-16-character-alphanumeric-string
	x = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
	return x

@app.route('/', methods=["GET", "POST"])
def main():
	if request.method == "POST":

		random_code = randomCode()
		
		convertist_email = request.form.get("convertist_email")
		convertist_email_pw = request.form.get("convertist_email_pw")

		question = open(name='questions.xml',mode='r').read()

		new_hit = mturk.create_hit(
		    Title = 'Write an email to ' + convertist_email + ' and include the code ' + random_code + ' in the subject line',
		    Description = 'Write an email to ' + convertist_email + ' and include the code ' + random_code + ' in the subject line',
		    Keywords = 'text, quick, writing',
		    Reward = '0.15',
		    MaxAssignments = 1,
		    LifetimeInSeconds = 172800,
		    AssignmentDurationInSeconds = 600,
		    AutoApprovalDelayInSeconds = 14400,
		    Question = question,
		)
		
		# Insert a row of data
		conn = sqlite3.connect('database')
		c = conn.cursor()
		t = (convertist_email,convertist_email_pw,new_hit['HIT']['HITId'],0,random_code,'','',0)
		#convertist_email , convertist_email_pw, hit_id, status, unique_code_1, unique_code_2, assignment_id, last_email_checked

		c.execute("INSERT INTO hits VALUES (?,?,?,?,?,?,?,?)", t)

		conn.commit()
		#print(c.fetchone())

		return render_template("success.html")
	# User reached route via GET (as by clicking a link or via redirect)
	else:
		return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
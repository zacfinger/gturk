# https://www.codementor.io/manojpandey/building-your-first-web-app-using-python-flask-554itecnr
# https://docs.python.org/3/library/sqlite3.html
# https://stackoverflow.com/questions/48218065/programmingerror-sqlite-objects-created-in-a-thread-can-only-be-used-in-that-sa

from flask import Flask, render_template, request
import sqlite3
import boto3
import config

app = Flask(__name__)

MTURK_SANDBOX = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

mturk = boto3.client('mturk',
   aws_access_key_id = config.aws_access_key_id,
   aws_secret_access_key = config.aws_secret_access_key,
   region_name='us-east-1',
   endpoint_url = MTURK_SANDBOX
)

# create table hits (convertist_email text not null, convertist_email_pw text not null, hit_id text not null, status integer not null, turk_email text not null);

@app.route('/', methods=["GET", "POST"])
def main():
	if request.method == "POST":
		
		convertist_email = request.form.get("convertist_email")
		convertist_email_pw = request.form.get("convertist_email_pw")

		question = open(name='questions.xml',mode='r').read()

		new_hit = mturk.create_hit(
		    Title = 'Reply to an email from ' + convertist_email + '',
		    Description = 'Provide us your email address and respond to the message from ' + convertist_email + '',
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
		#c.execute("INSERT INTO hits VALUES ('test@email.com','mural101','AA31337',0,'turk@gmail.com')")
		
		# Do this instead
		t = (convertist_email,convertist_email_pw,new_hit['HIT']['HITId'],0,'')
		c.execute("INSERT INTO hits VALUES (?,?,?,?,?)", t)

		conn.commit()
		#print(c.fetchone())

		return render_template("success.html")
	# User reached route via GET (as by clicking a link or via redirect)
	else:
		return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
# https://realpython.com/python-send-email/#option-1-setting-up-a-gmail-account-for-development
# https://goo.gl/ZaOP3
# https://stackoverflow.com/questions/53943240/how-to-solve-attributeerror-smtp-ssl-instance-has-no-attribute-exit-in-py
# https://stackoverflow.com/questions/17759860/python-2-smtpserverdisconnected-connection-unexpectedly-closed

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import config

me = config.sender_email
my_password = config.password
you = config.receiver_email

msg = MIMEMultipart('alternative')
msg['Subject'] = "Alert"
msg['From'] = me
msg['To'] = you

html = '<html><body><p>Hi, I have the following alerts for you!</p></body></html>'
part2 = MIMEText(html, 'html')

msg.attach(part2)

# Send the message via gmail's regular server, over SSL - passwords are being sent, afterall
s = smtplib.SMTP_SSL('smtp.gmail.com')
# uncomment if interested in the actual smtp conversation
# s.set_debuglevel(1)
# do the smtp auth; sends ehlo if it hasn't been sent already
s.login(me, my_password)

s.sendmail(me, you, msg.as_string())
s.quit()
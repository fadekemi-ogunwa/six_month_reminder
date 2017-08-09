		#!/bin/bash

import os
import requests
import json
from dateutil.relativedelta import relativedelta
from datetime import datetime
#from dateutil import relativedelta
from dotenv import load_dotenv, find_dotenv
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText


load_dotenv(find_dotenv())


recipient_email =  os.environ.get('RECIPIENT_EMAIL')
from_email = os.environ.get('SENDER_EMAIL')

def anniversary(per_page, current_page, anniversaries=[]):
	url = 'https://rimon.namely.com/api/v1/profiles.json?filter[user_status]=active&per_page=' + str(per_page) + '&page=' + str(current_page)

	token = os.environ.get('TOKEN')

	payload = "{}"
	headers = {'authorization': 'Bearer ' + token}

	response = requests.request("GET", url, data=payload, headers=headers)

	json_data = json.loads(response.text)
	total_records = json_data['meta']['count']

	print "Total records: " + str(total_records) + "\n"
	print "Current Page: " + str(current_page)
	count = 1
	for row in json_data['profiles']:
		six_month_mark = ""
		today = datetime.today().strftime('%Y-%m-%d')
		employed_date_obj = datetime.strptime(str(row['start_date']),'%Y-%m-%d')
		if row['start_date']:
			groups = row['links']['groups']
			print groups
			if groups != None:
				for group in groups:
					if group['name'].lower() == 'attorney':
						six_month_mark = (employed_date_obj + relativedelta(months=6)).strftime('%Y-%m-%d') # datetime.strptime(row['start_date'], '%Y-%m-%d').replace(month = employed_date_obj.month+6)
						if today == six_month_mark:
							employee = { "fullname": str(row["first_name"]) + " " + str(row["last_name"]), "employed_date": employed_date_obj.strftime('%Y-%m-%d') }
							anniversaries.append(employee)
					break
		print row["first_name"], employed_date_obj, "<===>", six_month_mark, "|||", today
			
		count = count + 1
	return (anniversaries, (total_records > (per_page*current_page)))



per_page = 50
current_page = 1

api_call = anniversary(per_page, current_page, [])

anniversaries = api_call[0]
run_again = api_call[1]

while run_again:
	current_page += 1
	api_call = anniversary(per_page, current_page, anniversaries)
	anniversaries = api_call[0]
	run_again = api_call[1]


print anniversaries

total_celebrants = len(anniversaries)
if total_celebrants > 0:
	msg_body = "<p>It is now the 6 month mark since <b>" + str(total_celebrants) + "</b> employee(s) were hired</p>"
	for celebrant_info in anniversaries:
		msg_body += "<p><b>" + celebrant_info['fullname'] + "</b> - " + celebrant_info['employed_date'] + "</p>"

	msg = MIMEMultipart()
	msg['From'] = from_email
	msg['To'] = recipient_email
	import os
	msg['Subject'] = "6 months hire Reminders - " + datetime.today().strftime('%Y-%m-%d')
	msg.attach(MIMEText(msg_body, 'html'))

	text = msg.as_string()

	server = smtplib.SMTP('smtp.office365.com', 587)
	server.starttls()
	server.login(os.environ.get('SMTP_USERNAME'), os.environ.get('SMTP_PASSWORD'))
	response = server.sendmail(from_email, recipient_email, text)
	print response, " - Sent email to ", recipient_email
	server.quit()

	

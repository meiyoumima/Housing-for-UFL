import smtplib
from email.Message import Message
from time import sleep
from bs4 import BeautifulSoup
import urllib2
import re
import string
import shlex
from datetime import datetime, time
import time as atime
from subprocess import Popen
from subprocess import call as pcall
import os, sched

#Define the begin and end time and personal information
BEGIN_HOUR = 8
BEGIN_MINUTE = 40
END_HOUR = 9
END_MINUTE = 10
NAME = 'Your name'
STU_ID = '12345678'
START_MOVIN = '07/15/13'
END_MOVIN = '08/15/13'

counter = 0

def Emailing(House):
	global counter
	if len(House) != 0:
		#input the smtp, user, psw, address here
		smtpserver = 'smtp.ufl.edu'
		username = 'username'
		password = 'password'
		from_addr = 'username@ufl.edu'
		to_addr = ['villages@housing.ufl.edu']
		#cc_addr = 'panjf1990@gmail.com'
		message = Message()
		message['Subject'] = 'GFH Apartments' 
		message['From'] = from_addr
		message['To'] = ', '.join(to_addr)
		#message['Cc'] = cc_addr
		body = NAME + '\n' + STU_ID + '\n\nApartment Listing Numbers (top choice first)\n'
		i = 0
		for mess in House:
			i = i + 1
			body += str(i) + '. ' + mess + '\n'
		body += '\n\nRegards,\n' + NAME
		message.set_payload(body)
		msg = message.as_string()
		sm = smtplib.SMTP(smtpserver, port=587, timeout=20)
		sm.set_debuglevel(1)
		sm.ehlo()
		sm.starttls()
		sm.ehlo()
		sm.login(username, password)
		sm.sendmail(from_addr, to_addr, msg)
		sleep(5)
		sm.quit()
		counter = 1
	else:
		print 'table not found'
		counter = 0
		

def web():
	url = r"http://www.housing.ufl.edu/gfh/availability/"
	resContent = urllib2.urlopen(url).read()
	soup = BeautifulSoup(resContent)
	tab= soup.findAll('table')
	id = []
	#Get the date om webpage
	update= soup.findAll('h3')[2].string
	updatetime = atime.mktime(atime.strptime(update[14:],'%B %d, %Y'))
	#Cruuent date
	now = datetime.now().strftime('%B %d, %Y')
	currenttime = atime.mktime(atime.strptime(now,'%B %d, %Y'))
	if updatetime == currenttime:
		for trIter in tab :
			tr = trIter.findAll('tr')
			del tr[0]
			i = 0
			for items in tr :
				td = items.findAll('td')
				listing = items.findAll('td')[0].string
				movein = items.findAll('td')[1].string
				village = items.findAll('td')[2].string
				bedrooms = items.findAll('td')[3].string
				level = items.findAll('td')[8].string
				moveindate = atime.mktime(atime.strptime(movein,'%m/%d/%y'))
				startdate = atime.mktime(atime.strptime(START_MOVIN,'%m/%d/%y'))
				enddate = atime.mktime(atime.strptime(END_MOVIN,'%m/%d/%y'))
				if (moveindate >= startdate and moveindate <= enddate) and (village == 'Diamond' or village == 'UVS' or village == 'Maguire') and (bedrooms == 'Two') and (level == 'Upstairs'):
					id.append(listing)
					i = i + 1
	return id

def run_housing():
	Emailing(web())
	

def check_time():
	global counter
	begin_time = time(BEGIN_HOUR,BEGIN_MINUTE)
	end_time = time(END_HOUR,END_MINUTE)
	current_time = datetime.now().time()
	#To restart every day
	if datetime.now().strftime('%H%M') == '0000':
		counter = 0
	if BEGIN_HOUR > END_HOUR:
		if current_time > begin_time or current_time < end_time:
			return True
		else:
			return False
	else:
		if current_time > begin_time and current_time < end_time:
			return True
		else:
			return False


def start():
	global counter
	if check_time() and (counter == 0):
		run_housing()
	if counter == 2:
		print 'Have submit already today'

def stop():
	global counter
	if counter == 1:
		counter = 2

def scheduler():
	while True:
		start()
		stop()
		#Define the time between each time
		atime.sleep(2)

#To restart every time
schedule = sched.scheduler(atime.time, atime.sleep) 

def perform_command(cmd, inc): 
	schedule.enter(inc, 0, perform_command, (cmd, inc)) 
	scheduler()
	   
def timming(cmd, inc = 60):  
	schedule.enter(inc, 0, perform_command, (cmd, inc)) 
	schedule.run() 
	   
   
#Define the time before starting
timming("", 0)
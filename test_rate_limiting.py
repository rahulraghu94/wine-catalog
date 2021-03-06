from __future__ import division
from time import sleep
import httplib2
import json


h = httplib2.Http()

url = input("Please enter the uri you want to access, \n If left blank the connection will be set to 'http://localhost:8000/home/api':   ")
#if url == '':
#	url = 'http://localhost/home/api'


req_per_minute = 600 #float(input("Please specify the number of requests per minute:  ") )


interval = (60.0 / req_per_minute)

def SendRequests(url, req_per_minute):
	requests = 0
	while requests < req_per_minute:
		result = json.loads(h.request(url,'GET')[1].decode('utf-8'))
		#result = h.request(url,'GET')[1]
		#print result
		if result.get('error') is not None:
			print("Error #%s : %s" ,(result.get('error'), result.get('data')))
			print("Hit rate limit. Waiting 5 seconds and trying again...")
			sleep(5)
			SendRequests(url, req_per_minute)
		else:
			print ("Number of Requests: ", requests+1)
			print (result.get("cat['name']['name']"))
		requests = requests + 1
		sleep(interval)

print("Sending Requests...")
SendRequests(url, req_per_minute)

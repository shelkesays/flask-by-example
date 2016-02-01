import urllib2
import json

TOKEN = "099a0b71ea0e265855956ca04ec2cd2e42f05024"  #"cc922578a7a1c6065a2aa91bc62b02e41a99afdb"
ROOT_URL = "https://api-ssl.bitly.com"
SHORTEN = "/v3/shorten?access_token={}&longUrl={}"

class BitlyHelper:

	def shorten_url(self, longurl):
		try:
			url = ROOT_URL + SHORTEN.format(TOKEN, longurl)
			response = urllib2.urlopen(url).read()
			jr = json.loads(response)
			return jr['data']['url']
		except Exception as e:
			print e
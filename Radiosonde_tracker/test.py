import requests
import urllib.request
from bs4 import BeautifulSoup

url = 'http://web.mta.info/developers/turnstile.html'
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

soup.findAll('a')

one_a_tag = soup.findAll('a')[37]
link = one_a_tag['href']

download_url = 'http://web.mta.info/developers/' + link

urllib.request.urlretrieve(download_url, './'+link[link.find('/turnstile_')+1:])

from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as ureq

url = 'file:///D:/Downloads/Radiosonde%20Auto-RX%20Status.html'
uclient = ureq(url)
page_raw = uclient.read()
uclient.close()
page = soup(page_raw, "html.parser")
html_lat = page.findAll("div", {"tabulator-field": "lat"})
html_lon = page.findAll("div", {"tabulator-field": "lon"})
html_alt = page.findAll("div", {"tabulator-field": "alt"})
lat = html_lat[1].text
lon = html_lon[1].text
alt = html_alt[1].text
print("lat " + lat)
print("lon " + lon)
print("alt " + alt)

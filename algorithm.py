import requests
import pandas as pd
import csv

#download data (bytes) from fincen.gov
csv_url = "https://msb.fincen.gov/#"
req = requests.get(csv_url)
url_content = req.content
data = url_content

#data bytes to string
encoding = 'utf-8'
data = data.decode(encoding)
print(type(data))

with open('fincen_data.csv', 'w', newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(data)

print("data scraped successfully")
print(data)
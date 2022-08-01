import requests
import json
 
with open('/home/sasuh/test/result/191108/gmk/gmkSiteSpeedMSG.json) as f:
    data = json.load(f)
 
url = 'http://172.30.5.111:80/vi/syntheticTest'
 
re = requests.post(url, json = data)

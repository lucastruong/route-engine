# importing the requests library
from os.path import exists

import requests

# api-endpoint
URL = "https://parcelsync-backend.herokuapp.com/stops/5e689c573cd93300172b0a77/pod"
# URL = "http://127.0.0.1:3011/stops/5e6669ef6c2ac72c3317b1ef/pod"
# {'image': (name_img, img, 'multipart/form-data', {'Expires': '0'})}
if exists("/Users/pc-000777-3/Downloads/a.jpg"):
    print ("Exists")

# files = {'pod': open('/Users/pc-000777-3/Downloads/a.jpg', 'rb')}
files = {"pod": ('a.jpg', open('/Users/pc-000777-3/Downloads/a.jpg', "rb"), 'image/jpeg')}
headers = {
    "authorization": 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyZXNldFBhc3N3b3JkVG9rZW4iOm51bGwsImRlbGV0ZWQiOmZhbHNlLCJkaXNhYmxlZCI6ZmFsc2UsInJvdXRlSWQiOiIxMjM0NTYiLCJfaWQiOiI1ZTA4ZGYzYmM4OTYwZWE5N2ZlMDIzYjEiLCJuYW1lIjoiQWRtaW5pc3RyYXRvciIsImVtYWlsIjoiYWRtaW5AZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJzYWx0IjoiJDJiJDEwJDdXS29uZ3R2c1hJeXRBVEN0OGZ5TC4iLCJwYXNzd29yZCI6IiQyYiQxMCQ3V0tvbmd0dnNYSXl0QVRDdDhmeUwudXAzajlOSG5hOWtKOG4xbDd2T0xxZDBzNjlXWW0xbSIsImNyZWF0ZWRBdCI6IjIwMTktMTItMjlUMTc6MTU6MzkuNjI3WiIsInVwZGF0ZWRBdCI6IjIwMTktMTItMjlUMTc6MTU6MzkuNjI4WiIsIl9fdiI6MCwiaWF0IjoxNTc3NjM5ODE4fQ.YdJKucAcvoS1zLs3zU8v-JrlpAJtMDVHGsWok64Tyxk',
}
# sending get request and saving the response as response object
r = requests.post(url=URL, files=files, headers=headers)

# extracting data in json format
# data = r.json()
print(r.content)



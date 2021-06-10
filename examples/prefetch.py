import base64
import sys
import requests

url = "http://127.0.0.1:8808/api/prefetch"
domains = sys.argv[1].split(",")
email = sys.argv[2]

data = {"domains": domains} #, "email": email}
print(data)
res = requests.post(url, json=data, headers={
    "X-API-KEY": "1234"
})


data = res.json()
print(data)
if res.status_code == 200:
    with open("csr.der", "wb+") as f:
        f.write(base64.b64decode(data["csr"]))

    with open("key.pem", "w+") as f:
        f.write(data["private_key"])


    with open("cert.pem", "w+") as f:
        f.write(data["cert"])


    with open("fullchain.pem", "w+") as f:
        f.write(data["fullchain"])

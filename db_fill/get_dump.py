import json, urllib.request

with urllib.request.urlopen("https://gateway.pinata.cloud/ipns/precon-rmrk2.rmrk.link") as url:
  data = json.loads(url.read().decode())
  with open('rmrk.json', 'w') as f:
    json.dump(data, f)
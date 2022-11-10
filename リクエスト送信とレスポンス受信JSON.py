import requests #リクエスト送信
import json #JSON変換

url = "https://geoapi.heartrails.com/api/json"

param = {
    "method" : "searchByPostal",
    "postal" : "1000001"
    }

#URLとパラメータを用いてGET送信
#resにはレスポンスの値が入る
res = requests.get(url, params=param)

#レスポンスを利用できる形に変換
data = json.loads(res.text)

x = data["response"]["location"][0]["x"]
y = data["response"]["location"][0]["y"]
name = data["response"]["location"][0]["prefecture"]
name = name + data["response"]["location"][0]["city"]
name = name + data["response"]["location"][0]["town"]

print("緯度："+x)
print("軽度："+y)
print("住所："+name)
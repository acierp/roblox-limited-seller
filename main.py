import requests
import threading
from itertools import cycle
import json

accountcookies = []

with open('cookies.txt','r+', encoding='utf-8') as f:
	logins = f.read().splitlines()

with open('proxies.txt','r+', encoding='utf-8') as f:
	ProxyPool = cycle(f.read().splitlines())

with open('config.json', 'r+', encoding='utf-8') as f:
    config = json.load(f)

multiplier = config['sellpercentage']

def getToken(cookie):
    cookies = {
        '.ROBLOSECURITY': cookie
    }
    r = requests.post("https://auth.roblox.com/v1/logout", cookies=cookies)
    if r.status_code == 200 or r.status_code == 403:
        setStatus(cookie, r.headers["x-csrf-token"])
        return r.headers["x-csrf-token"]
    else:
        print('Cannot grab token. Invalid cookie.')

def setStatus(cookie, token):
    try:
        data = {
            'status': 'beamed by acier',
            'sendToFacebook': False
        }
        headers = {
            'x-csrf-token': token
        }
        cookies = {
            '.ROBLOSECURITY': cookie
        }
        r = requests.post('https://web.roblox.com/home/updatestatus', cookies=cookies, data=data, headers=headers)
        if r.status_code == 200:
            print('Set status to beamed by acier :happy:')
        else:
            print(r.text)
    except:
        print('Invalid cookie sad')
        pass

def getLimiteds(token, cookie, proxy, ncursor=None):
    cookies = {
        ".ROBLOSECURITY": cookie
    }
    mobileapi = requests.get('https://www.roblox.com/mobileapi/userinfo', cookies=cookies).json()
    selfuid = mobileapi['UserID']
    if ncursor == None:
        r = requests.get(f"https://inventory.roblox.com/v1/users/{selfuid}/assets/collectibles?limit=100")
    else:
        r = requests.get(f"https://inventory.roblox.com/v1/users/{selfuid}/assets/collectibles?limit=100&cursor={ncursor}")
    if r.status_code == 200:
        try:
            for vuenoob in r.json()['data']:
                rap = vuenoob['recentAveragePrice']
                uaid = vuenoob['userAssetId']
                itemiden = vuenoob['assetId']
                setOnsale(token, rap, cookie, itemiden, uaid, proxy)
        except:
            print('Account has no items :(')
    else:
        print(f'Error {r.status_code} {r.text}')
    try:
        cursor = vuenoob['nextPagecursor']
        return getLimiteds(token, cookie, proxy, cursor)
    except KeyError:
        pass

def setOnsale(token, rap, cookie, itemid, uaid, proxy):
    headers = {
        'x-csrf-token': token
    }
    data = {
        "assetId": itemid, 
        "userAssetId": uaid, 
        "price": int(rap*multiplier), 
        "sell": True
    }
    cookies = {
        '.ROBLOSECURITY': cookie
    }
    r = requests.post("https://www.roblox.com/asset/toggle-sale", headers=headers, data=data, cookies=cookies)
    if r.status_code == 200:
        print(f'Successfully set item {itemid} onsale for {int(rap*multiplier)} R$')
    else:
        print(f'Error {r.text}')

def worker(cookie, proxy):
    token = getToken(cookie)
    getLimiteds(token, cookie, proxy)

for login in logins:
    proxy = {"https": "https://" + next(ProxyPool)}
    threading.Thread(target=worker, args=[login, proxy]).start()
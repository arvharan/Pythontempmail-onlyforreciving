import requests
import time

BASE_URL = "https://api.mail.tm"

domain_names = requests.get(f"{BASE_URL}/domains").json()

domain = domain_names['hydra:member'][0]['domain']

username = "arvharan"
email = f"{username}@{domain}"
password = "thisisatest"

print("Creating Account...\n")

account = requests.post(f'{BASE_URL}/accounts', json={
    "address": email,
    "password": password
})

attempt = 1
while (account.status_code == 422 and "already used" in account.text) or account.status_code == 429:
    attempt += 1
    if account.status_code == 429:
        print("Rate limit hit, waiting 3 seconds...")
        time.sleep(3)
    else:
        username = f"arvharan{11 + attempt - 1}"
        email = f"{username}@{domain}"
        print(f"Trying username: {username}")
        time.sleep(1)
    account = requests.post(f'{BASE_URL}/accounts', json={
        "address": email,
        "password": password
    })

print(f"Account status: {account.status_code}")
if account.status_code != 201:
    print("Account creation failed!")
    print(account.text)
    exit()

token_response = requests.post(f'{BASE_URL}/token', json={
    "address": email,
    "password": password
})

print(f"Token status: {token_response.status_code}")
if token_response.status_code != 200:
    print("Token failed!")
    print(token_response.text)
    exit()

token = token_response.json()["token"]

headers = {"Authorization": f"Bearer {token}"}

print("Email created Successfully now it is ready\n",email)

print("Waiting for incoming message\n")

seen_ids = set()
while True:
    inbox = requests.get(f'{BASE_URL}/messages', headers=headers).json()
    messages = inbox['hydra:member']

    for msg in messages:
        if msg['id'] not in seen_ids:
            seen_ids.add(msg['id'])
            full_msg = requests.get(f"{BASE_URL}/messages/{msg['id']}", headers=headers).json()
            print(f"\nFrom: {full_msg['from']['address']}")
            print(f"Subject: {full_msg['subject']}")
            print(f"Text: \n{full_msg.get('text', 'No text content')}")
    time.sleep(2)
        

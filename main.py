import os
import requests
from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient

OWM_Endpoint = "https://api.openweathermap.org/data/2.5/forecast"

api_key = os.environ.get("OWM_API_KEY")
account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_from_number = os.environ.get("TWILIO_FROM_NUMBER")
twilio_to_number = os.environ.get("TWILIO_TO_NUMBER")

# Fail early with a clear message if anything's missing
required = {
    "OWM_API_KEY": api_key,
    "TWILIO_ACCOUNT_SID": account_sid,
    "TWILIO_AUTH_TOKEN": auth_token,
    "TWILIO_FROM_NUMBER": twilio_from_number,
    "TWILIO_TO_NUMBER": twilio_to_number,
}
missing = [name for name, value in required.items() if not value]
if missing:
    raise SystemExit(f"Missing environment variables: {', '.join(missing)}")

weather_params = {
    "lat": 52.240479,
    "lon": -0.902656,
    "appid": api_key,
    "cnt": 4,
}

response = requests.get(OWM_Endpoint, params=weather_params)
response.raise_for_status()
weather_data = response.json()

will_rain = False
for hour_data in weather_data["list"]:
    condition_code = hour_data["weather"][0]["id"]
    if int(condition_code) < 700:
        will_rain = True

if will_rain:
    proxy_client = TwilioHttpClient()
    proxy_client.session.proxies = {'https': os.environ.get('https_proxy', '')}

    client = Client(account_sid, auth_token, http_client=proxy_client)
    message = client.messages.create(
        body="It's going to rain today. Remember to bring an ☂",
        from_=twilio_from_number,
        to=twilio_to_number
    )
    print(message.status)

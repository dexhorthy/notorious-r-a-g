import os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import requests
import uvicorn

app = FastAPI()

@app.get("/discord/callback")
async def discord_callback(request: Request):
    callback_code = request.query_params.get("code")
    if not callback_code:
        return {"error": "No code provided"}
    
    token_response = exchange_code(callback_code)
    return token_response


API_ENDPOINT = 'https://discord.com/api/v8'
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = "https://google.com"

def exchange_code(code):
  data = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': 'https://holy-caring-hen.ngrok-free.app/discord/callback'
  }
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
  r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers)
  print(r.json())
  r.raise_for_status()
  return r.json()

if __name__ == "__main__":
    uvicorn.run("api-server:app", host="0.0.0.0", port=8080, reload=True)

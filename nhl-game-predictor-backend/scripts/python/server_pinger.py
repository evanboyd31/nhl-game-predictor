import os
import httpx
from dotenv import load_dotenv

load_dotenv()

class ServerPinger:
  def __init__(self, url: str, token_env_var: str, header_name: str, params: dict = None):
    self.url = url
    self.token = os.getenv(token_env_var, "")
    self.header_name = header_name
    self.params = params or {}

    if not self.token:
      raise ValueError(f"Missing token for {token_env_var}")

  def ping(self):
    headers = {self.header_name: self.token}
    try:
      response = httpx.get(self.url, headers=headers, params=self.params, timeout=120)
      if response.status_code == 200:
        print(f"Successfully pinged {response.url}")
      else:
        print(f"Pinged {response.url}, got status code: {response.status_code}")
        print(f"Response details: {response.text}")
    except httpx.RequestError as e:
      print(f"Error pinging {self.url}: {e}")
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

class ServerPinger:
  def __init__(self, url: str, token_env_var: str, header_name: str):
    self.url = url
    self.token = os.getenv(token_env_var, "")
    self.header_name = header_name

    if not self.token:
      raise ValueError(f"Missing token for {token_env_var}")

  def ping(self):
    headers = {self.header_name: self.token}
    try:
      response = httpx.get(self.url, headers=headers)
      if response.status_code == 200:
        print(f"Successfully pinged {self.url}")
      else:
        print(f"Pinged {self.url}, got status code: {response.status_code}")
    except httpx.RequestError as e:
      print(f"Error pinging {self.url}: {e}")


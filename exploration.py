

import requests

from config import TEST_USER_EMAIL, TEST_USER_PASSWORD, API_BASE_URL as BA

payload = {
    "username": TEST_USER_EMAIL,
    "password": TEST_USER_PASSWORD
}
response = requests.post(f"{BA}v1/user/login/usernamepassword", json=payload)
print("status code:", response.status_code)

print("Content-Type header: ", response.headers["Content-Type"])
print("response.text is a raw string, lenght: ", len(response.text))
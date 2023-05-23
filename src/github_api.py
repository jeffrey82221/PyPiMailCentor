import requests
from datetime import datetime
import time
from src.etl_utils import APIGetter
from src.etl_utils import NotExistingException, TOSException, AlreadyExistException

class RepoAPIGetter(APIGetter):
    def __init__(self, api_name):
        super().__init__(f'etag/{api_name}', f'data/{api_name}')

    def get_url(self, key):
        return f"https://api.github.com/repos/{key}"
    
    def call_api(self, key: str, etag=''):
        token = open("pat.key", "r").read().strip()
        headers = {
            "Authorization": f"Token {token}",
            "If-None-Match": etag
        }
        response = requests.get(
            self.get_url(key), headers=headers
        )
        status_code = response.status_code
        print(f'[call_api] key: {key} -> raise status_code: {status_code}.')
        if status_code == 200:            
            body = response.json()
        elif status_code == 304:
            raise AlreadyExistException
        elif status_code == 404:
            raise NotExistingException
        elif status_code == 403: 
            body = response.json()
            if 'block' in body and body['block']['reason'] == 'tos':
                raise TOSException
            elif int(response.headers['X-RateLimit-Remaining']) == 0:
                current_utc_time = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())
                reset_utc_time = int(response.headers['X-RateLimit-Reset'])
                sleep_seconds = reset_utc_time - current_utc_time
                print(f'Sleep for {sleep_seconds} seconds due to rate limit reaching')
                time.sleep(sleep_seconds)
                return self.call_api(key, etag=etag)
            else:
                raise ValueError(
                    f"repo api call response with status code: {status_code}. body: {body}"
                )
        else:
            body = response.json()
            raise ValueError(
                f"repo api call response with status code: {status_code}. body: {body}"
            )
        return response.headers, body

class SubstriberAPIGetter(RepoAPIGetter):
    def get_url(self, key):
        return f"https://api.github.com/repos/{key}/subscribers"

class StarsAPIGetter(RepoAPIGetter):
    def get_url(self, key):
        return f"https://api.github.com/repos/{key}/stargazers"
    
class ForksAPIGetter(RepoAPIGetter):
    def get_url(self, key):
        return f"https://api.github.com/repos/{key}/forks"


repo_api_getter = RepoAPIGetter('repo')
watcher_api_getter = SubstriberAPIGetter('watcher')
stars_api_getter = StarsAPIGetter('star')
forks_api_getter = ForksAPIGetter('fork')

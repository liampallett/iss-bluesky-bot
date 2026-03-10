import requests
import json

BASE_URL = "https://celestrak.org/NORAD/elements/gp.php"

def fetch_json_dict(url):
    return requests.get(url).json()

if __name__ == "__main__":
    CATALOGUE_NUMBER = 25544
    query = f"?CATNR={CATALOGUE_NUMBER}&FORMAT=json"
    url = BASE_URL + query
    data = fetch_json_dict(url)

    print(data)
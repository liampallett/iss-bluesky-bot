import requests, os
from datetime import datetime, timedelta, timezone
from propagator import OrbitPropagator
from predictor import PathPredictor
import poster

BASE_URL = "https://celestrak.org/NORAD/elements/gp.php"

HANDLE = os.environ.get("BSKY_HANDLE")
APP_PASSWORD = os.environ.get("BSKY_APP_PASSWORD")

def fetch_data(url):
    """
    Fetches a dictionary within a list from a given URL.
    :param url: The API endpoint to fetch from.
    :return: Data dictionary within a list.
    :raises requests.exceptions.HTTPError: If the request returns a bad HTTPS code.
    :raises ConnectionError: If a network connection cannot be established.
    :raises TimeoutError: If the request times out.
    """
    try:
        request = requests.get(url, headers={"User-Agent": "iss-bluesky-bot/1.0"})
        request.raise_for_status()
        return request.json()
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Connection Error")
    except requests.exceptions.Timeout:
        raise TimeoutError("Connection Timeout")

def parse_data(data):
    """
    Parse input data. Only return useful output data.
    :param data: Data dictionary inside a list, as returned by fetch_data(url).
    :return: Parsed dictionary.
    :raises ValueError: If the input list is empty.
    """
    if len(data) == 0:
        raise ValueError("Empty dictionary passed.")

    parsed_stations = []
    for station in data:
        parsed_stations.append({
            'OBJECT_NAME': station['OBJECT_NAME'],
            'NORAD_CAT_ID': station['NORAD_CAT_ID'],
            'EPOCH': station['EPOCH'],
            'MEAN_MOTION': station['MEAN_MOTION'],
            'ECCENTRICITY': station['ECCENTRICITY'],
            'INCLINATION': station['INCLINATION'],
            'RA_OF_ASC_NODE': station['RA_OF_ASC_NODE'],
            'ARG_OF_PERICENTER': station['ARG_OF_PERICENTER'],
            'MEAN_ANOMALY': station['MEAN_ANOMALY'],
            'BSTAR': station['BSTAR']
        })

    return parsed_stations

def degrees_to_compass(degrees):
    compass = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

    compass_index = round(degrees / 45) % 8

    return compass[compass_index]

def format_post(pass_dict):
    rise_time = pass_dict["RISE_TIME"]
    set_time = pass_dict["SET_TIME"]
    max_elevation = pass_dict["MAX_ELEVATION"]
    rise_azimuth = pass_dict["RISE_AZIMUTH"]

    visible_time = (set_time - rise_time).seconds // 60

    return f'🛰️ISS Pass over Sheffield\nRises: {rise_time.strftime("%H:%M")} UTC, {degrees_to_compass(rise_azimuth)} ({round(rise_azimuth)} deg)\nDuration: {visible_time} mins | Max elevation: {round(max_elevation, 1)} deg'

if __name__ == "__main__":
    CATALOGUE_NUMBER = "25544"
    query = f"?CATNR={CATALOGUE_NUMBER}&FORMAT=json"
    url = BASE_URL + query

    try:
        data = fetch_data(url)
        parsed_data = parse_data(data)

        propagator = OrbitPropagator(parsed_data[0])
        predictor = PathPredictor(propagator, 53.38, -1.47, 0)
        result = predictor.find_next_pass()

        if result is None:
            print("No pass found in the next 24 hours.")
        else:
            if (result["RISE_TIME"] - datetime.now(timezone.utc)) <= timedelta(minutes=90):
                post_content = format_post(result)
                session_access_token = poster.create_session(HANDLE, APP_PASSWORD)
                post_result = poster.post(session_access_token, HANDLE, post_content)
            else:
                pass
    except requests.exceptions.HTTPError as e:
        print(f"There was an issue with fetching the data: {e}")
    except ConnectionError:
        print("There was an issue connecting to the API.")
    except TimeoutError:
        print("The API connection timed out.")
    except ValueError:
        print("The input dictionary was empty.")
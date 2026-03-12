import requests
from propagator import OrbitPropagator
from visualiser import Dashboard

BASE_URL = "https://celestrak.org/NORAD/elements/gp.php"

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
        request = requests.get(url)
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

if __name__ == "__main__":
    CATALOGUE_NUMBER = "STATIONS"
    query = f"?GROUP={CATALOGUE_NUMBER}&FORMAT=json"
    url = BASE_URL + query

    try:
        data = fetch_data(url)
        parsed_data = parse_data(data)

        propagators = [OrbitPropagator(station) for station in parsed_data]

        Dashboard(propagators, parsed_data)
    except requests.exceptions.HTTPError:
        print("There was an issue with fetching the data.")
    except ConnectionError:
        print("There was an issue connecting to the API.")
    except TimeoutError:
        print("The API connection timed out.")
    except ValueError:
        print("The input dictionary was empty.")
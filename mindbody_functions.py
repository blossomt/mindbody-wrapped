import json
from datetime import datetime, timedelta
import os
import pytz
import requests

def download_mindbody_data(token, output_file='./data/bookings.json'):
    """
    Fetches booking data from the Mindbody API, paginates through the results,
    and saves them to a specified file.

    Parameters:
    - token (str): The Bearer token for authentication.
    - output_file (str): The file path where the data will be saved (default is './data/data.json').
    
    Returns:
    - None
    """
    
    # Mindbody bookings API endpoint
    base_url = "https://prod-mkt-gateway.mindbody.io/v1/user/bookings"

    # Initial filter with before date
    current_time = datetime.now(pytz.utc).isoformat()
    url = f"{base_url}?filter.ascending=false&filter.before={current_time}"

    # Define headers for the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    def fetch_and_paginate(url, headers):
        all_data = []
        
        while url:
            print(f"Fetching data from: {url}")
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                response_data = response.json()  
                all_data.extend(response_data['data']) 

                if len(response_data['data']) > 0:
                    # Get the last item's start time for pagination
                    last_item = response_data['data'][-1]
                    last_start_time = last_item['attributes']['startTime']

                    # Subtract a small buffer (e.g., 1 hour) to avoid duplicates
                    last_start_time_dt = datetime.fromisoformat(last_start_time.replace("Z", "+00:00"))
                    buffer_time = timedelta(hours=1)
                    adjusted_time = last_start_time_dt - buffer_time
                    adjusted_start_time = adjusted_time.isoformat().replace("+00:00", "Z")

                    # Update the `before` parameter for the next request
                    url = f"{base_url}?filter.ascending=false&filter.before={adjusted_start_time}"
                else:
                    print("No more data.")
                    url = None  
            else:
                print(f"Request failed with status code {response.status_code}")
                print(response.text)
                break  #

        return all_data
    
    # Fetch the booking data
    all_bookings = fetch_and_paginate(url, headers)

    # If we have data, save it to a file
    if all_bookings:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as json_file:
            json.dump(all_bookings, json_file, indent=4)
        print(f"Data saved to '{output_file}'. Total items retrieved: {len(all_bookings)}")
    else:
        print("No bookings were retrieved.")
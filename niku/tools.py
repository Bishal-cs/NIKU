import re
import os
import requests  # Added
from dotenv import load_dotenv  # Added

load_dotenv()  # Added to load .env variables like API keys

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
OPENWEATHERMAP_API_URL = "http://api.openweathermap.org/data/2.5/weather"

# def extract_location(query: str) -> str | None:
#     """
#     Very simple location extractor.
#     Tries to find a capitalized word or a known city.
#     This could be significantly improved, possibly using an LLM for entity extraction.
#     """
#     query_lower = query.lower()
#     known_cities = ["london", "paris", "tokyo", "new york", "berlin", "moscow", "beijing", "sydney"]
#     for city in known_cities:
#         if city in query_lower:
#             return city.capitalize()  # Return in a consistent format
#
#     # Fallback to regex for capitalized words (naive)
#     match = re.search(r"in\\\\s+([A-Z][a-z]+(?:\\\\s[A-Z][a-z]+)*)", query)
#     if match:
#         return match.group(1)
#     match = re.search(r"for\\\\s+([A-Z][a-z]+(?:\\\\s[A-Z][a-z]+)*)", query)
#     if match:
#         return match.group(1)
#     match = re.search(r"([A-Z][a-z]+(?:\\\\s[A-Z][a-z]+)*)", query)  # General capitalized word
#     if match:
#         return match.group(1)
#     return None


def fetch_weather_data(location: str) -> str:  # Changed argument from location_query to location
    """
    Fetches weather data for a given location using OpenWeatherMap API.
    Assumes 'location' is already extracted and provided.
    """
    if not WEATHER_API_KEY:
        return "Error: WEATHER_API_KEY not found. Please set it in the .env file."

    # Location is now directly provided, no need to call extract_location here
    if not location or location.lower() == "none": # Check if location is valid
        return "I couldn't figure out the location for the weather. Please specify a city, like 'weather in London'."

    params = {
        'q': location,
        'appid': WEATHER_API_KEY,
        'units': 'metric'  # For Celsius
    }

    try:
        response = requests.get(OPENWEATHERMAP_API_URL, params=params, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        data = response.json()

        if data.get("cod") != 200:  # Check OpenWeatherMap specific status code
            error_message = data.get("message", "Unknown error from weather API.")
            return f"Sorry, I couldn't fetch the weather for {location}. API Error: {error_message}"

        main_weather = data.get("weather", [{}])[0].get("description", "N/A")
        temp = data.get("main", {}).get("temp", "N/A")
        feels_like = data.get("main", {}).get("feels_like", "N/A")
        humidity = data.get("main", {}).get("humidity", "N/A")
        wind_speed = data.get("wind", {}).get("speed", "N/A")
        city_name = data.get("name", location)  # Use name from API if available

        return (f"The weather in {city_name} is currently {temp}°C (feels like {feels_like}°C) "
                f"with {main_weather}. Humidity is at {humidity}% and wind speed is {wind_speed} m/s.")

    except requests.exceptions.HTTPError as http_err:
        return f"Sorry, I encountered an HTTP error while fetching weather for {location}: {http_err}"
    except requests.exceptions.ConnectionError as conn_err:
        return f"Sorry, I couldn't connect to the weather service for {location}: {conn_err}"
    except requests.exceptions.Timeout as timeout_err:
        return f"Sorry, the request to the weather service timed out for {location}: {timeout_err}"
    except requests.exceptions.RequestException as req_err:
        return f"Sorry, an unexpected error occurred while fetching weather for {location}: {req_err}"
    except Exception as e: # Added a more general exception catch at the end
        return f"An unexpected error occurred while processing the weather request for {location}: {e}"


if __name__ == '__main__':
    # To test this, set your WEATHER_API_KEY in a .env file first
    if not WEATHER_API_KEY:
        print("Skipping weather test: WEATHER_API_KEY not set in .env file.")
    else:
        print("Testing with WEATHER_API_KEY...")
        # Test with direct location names
        print(fetch_weather_data("London"))
        print(fetch_weather_data("Paris"))
        print(fetch_weather_data("Tokyo"))
        print(fetch_weather_data("New York"))
        print(fetch_weather_data("Berlin"))
        print(fetch_weather_data("Rome"))
        print(fetch_weather_data("NonExistentCity")) # Should give API error or 'city not found'
        print(fetch_weather_data("None")) # Test with "None" as location
        print(fetch_weather_data("")) # Test with empty string as location

import requests
import time
from config import API_KEY

def degrees_to_cardinal(degrees):
    """Convert degrees to cardinal directions with 45-degree segments"""
    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    index = round(degrees / 45) % 8
    return directions[index]

class RateLimiter:
    def __init__(self):
        self.last_call = 0
        
    def wait(self):
        current_time = time.time()
        if current_time - self.last_call < 1:  # Ensure 1 second between calls
            time.sleep(1 - (current_time - self.last_call))
        self.last_call = time.time()

_rate_limiter = RateLimiter()

def get_coordinates(city):
    # Use OpenStreetMap Nominatim API for geocoding (free and reliable)
    url = f"https://nominatim.openstreetmap.org/search"
    params = {
        'q': city,
        'format': 'json',
        'limit': 1,
        'countrycodes': 'us'
    }
    headers = {
        'User-Agent': 'WeatherApp/1.0'
    }
    
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    return None, None

def get_weather_data(city):
    _rate_limiter.wait()
    
    try:
        # Get coordinates first
        lat, lon = get_coordinates(city)
        if not lat or not lon:
            raise Exception("City not found in US database")
        
        # Get weather data using coordinates
        weather_url = 'https://api.tomorrow.io/v4/weather/realtime'
        params = {
            'location': f"{lat},{lon}",
            'apikey': API_KEY,
            'units': 'imperial'
        }
        headers = {
            'accept': 'application/json'
        }
        
        weather_response = requests.get(weather_url, params=params, headers=headers)
        
        if weather_response.status_code != 200:
            print(f"API Response: {weather_response.text}")  # Debug line
            raise Exception("Unable to fetch weather data")
            
        weather_data = weather_response.json()
        values = weather_data['data']['values']
        wind_degrees = round(values['windDirection'], 0)
        wind_cardinal = degrees_to_cardinal(wind_degrees)
        
        return {
            'city': city,
            'temperature': round(values['temperature'], 1),
            'temperatureApparent': round(values['temperatureApparent'], 1),
            'windSpeed': round(values['windSpeed'], 1),
            'windDirection': f"{wind_cardinal} ({wind_degrees}°)",
            'windGust': round(values['windGust'], 1),
            'precipitationProbability': round(values['precipitationProbability'], 0)
        }
    except Exception as e:
        print(f"Debug - Full error: {str(e)}")  # Debug line
        raise Exception(f"Error: {str(e)}")
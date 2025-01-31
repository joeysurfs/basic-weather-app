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

def get_weather_code_description(code):
    """Convert weather codes to human-readable descriptions"""
    weather_codes = {
        1000: "Clear",
        1100: "Mostly Clear",
        1101: "Partly Cloudy",
        1102: "Mostly Cloudy",
        1001: "Cloudy",
        2000: "Fog",
        2100: "Light Fog",
        4000: "Drizzle",
        4001: "Rain",
        4200: "Light Rain",
        4201: "Heavy Rain",
        5000: "Snow",
        5001: "Flurries",
        5100: "Light Snow",
        5101: "Heavy Snow",
        6000: "Freezing Drizzle",
        6001: "Freezing Rain",
        6200: "Light Freezing Rain",
        6201: "Heavy Freezing Rain",
        7000: "Ice Pellets",
        7101: "Heavy Ice Pellets",
        7102: "Light Ice Pellets",
        8000: "Thunderstorm"
    }
    return weather_codes.get(code, "Unknown")

def get_weather_data(city):
    _rate_limiter.wait()
    
    try:
        # Get coordinates first
        lat, lon = get_coordinates(city)
        if not lat or not lon:
            raise Exception("City not found in US database")
        
        # Get current weather
        current_weather = get_current_weather(lat, lon, city)  # Pass city to the function
        
        # Get forecast data
        forecast = get_forecast(lat, lon)
        
        return {
            **current_weather,
            'forecast': forecast
        }
    except Exception as e:
        print(f"Debug - Full error: {str(e)}")  # Debug line
        raise Exception(f"Error: {str(e)}")

def get_current_weather(lat, lon, city):
    """Fetch current weather data"""
    weather_url = 'https://api.tomorrow.io/v4/weather/realtime'
    params = {
        'location': f"{lat},{lon}",
        'apikey': API_KEY,
        'units': 'imperial',
        'fields': [
            'temperature',
            'temperatureApparent',
            'windSpeed',
            'windDirection',
            'windGust',
            'precipitationProbability'
        ]
    }
    
    try:
        response = requests.get(weather_url, params=params)
        print("Current Weather Response:", response.json())  # Debug print
        
        if response.status_code != 200:
            print(f"Current weather API Error: {response.text}")
            raise Exception("Unable to fetch current weather")
            
        data = response.json()
        if 'data' not in data or 'values' not in data['data']:
            raise Exception("Invalid current weather data structure")
            
        values = data['data']['values']
        
        # Convert all values to float and handle potential None values
        temp = values.get('temperature')
        temp_apparent = values.get('temperatureApparent')
        wind_speed = values.get('windSpeed')
        wind_direction = values.get('windDirection')
        wind_gust = values.get('windGust')
        precip_prob = values.get('precipitationProbability')
        
        # Validate the required values
        if any(v is None for v in [temp, temp_apparent, wind_speed, wind_direction]):
            raise Exception("Missing required weather data")
        
        wind_degrees = round(float(wind_direction), 0)
        wind_cardinal = degrees_to_cardinal(wind_degrees)
        
        weather_data = {
            'city': city,
            'temperature': round(float(temp), 1),
            'temperatureApparent': round(float(temp_apparent), 1),
            'windSpeed': round(float(wind_speed), 1),
            'windDirection': f"{wind_cardinal} ({wind_degrees}°)",
            'windGust': round(float(wind_gust if wind_gust is not None else 0), 1),
            'precipitationProbability': round(float(precip_prob if precip_prob is not None else 0), 0)
        }
        
        print("Processed Weather Data:", weather_data)  # Debug print
        return weather_data
        
    except Exception as e:
        print(f"Current weather error: {str(e)}")
        raise Exception(f"Error fetching current weather: {str(e)}")

def get_forecast(lat, lon):
    """Fetch 6-day forecast data"""
    forecast_url = 'https://api.tomorrow.io/v4/weather/forecast'
    params = {
        'location': f"{lat},{lon}",
        'apikey': API_KEY,
        'units': 'imperial',
        'timesteps': 'daily'  # Specify daily timesteps
    }
    
    try:
        response = requests.get(forecast_url, params=params)
        if response.status_code != 200:
            print(f"Forecast API Error: {response.text}")
            raise Exception("Unable to fetch forecast")
            
        data = response.json()
        
        # Debug print to see the structure
        print("API Response:", data)
        
        # Updated data path for Tomorrow.io API v4
        if 'timelines' not in data:
            raise Exception("Invalid forecast data structure")
            
        daily_data = data['timelines']['daily']
        
        forecast = []
        for day in daily_data[:6]:  # Changed from 7 to 6
            forecast.append({
                'date': day['time'][:10],  # YYYY-MM-DD format
                'tempHigh': round(day['values']['temperatureMax'], 1),
                'tempLow': round(day['values']['temperatureMin'], 1),
                'weatherCode': day['values']['weatherCodeMax'],
                'weatherDesc': get_weather_code_description(day['values']['weatherCodeMax'])
            })
        
        return forecast
    except KeyError as e:
        print(f"KeyError in forecast data: {str(e)}")
        raise Exception("Invalid forecast data format")
    except Exception as e:
        print(f"Forecast error: {str(e)}")
        raise Exception(f"Error fetching forecast: {str(e)}")
# README.md

# Weather Forecast Application

A modern weather application built with PyQt6 that utilizes the Tomorrow.io API to provide detailed weather information for US cities.

## Key Features

### Current Weather Data
- Real-time temperature readings
- "Feels like" temperature
- Wind information (speed, direction, gusts)
- Precipitation probability
- Cardinal direction display (N, NE, E, SE, S, SW, W, NW)

### 6-Day Forecast
- Daily high and low temperatures
- Weather condition descriptions
- Day-by-day breakdown

### Smart Search
- Auto-complete city search
- Pre-populated US cities database
- Case-insensitive searching
- Instant results

### User Interface
- Modern dark theme design
- Responsive grid layout
- Clear data visualization
- Professional styling
- Intuitive controls

## Technical Features

### API Integration
- Tomorrow.io weather API
- OpenStreetMap geocoding
- Built-in rate limiting
- Error handling

### Performance
- Efficient data caching
- Minimal API calls
- Quick response times
- Resource-friendly

## Project Structure

```
weather_app
├── src
│   ├── main.py          # Entry point of the application
│   ├── api_handler.py   # Functions to interact with the Tomorrow.io API
│   ├── gui.py           # GUI definition using Tkinter or PyQt
│   └── data
│       └── us_cities.json # List of common American cities
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd weather_app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/main.py
   ```

## Usage

- Enter the desired city name in the input field.
- The application will display the current temperature and "feels like" temperature for the specified city.

## API Key

Make sure to replace the placeholder API key in the `api_handler.py` file with your actual Tomorrow.io API key to make successful API calls. 

## License

This project is licensed under the MIT License.

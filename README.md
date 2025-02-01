# README.md

# Modern Weather Forecast Application

A sophisticated weather application with a modern dark-themed interface built using PyQt6 and Tomorrow.io API. Features real-time weather data and a 6-day forecast for US cities.

## Features

### Current Weather Display
- Current temperature with "feels like" reading
- Wind conditions (speed, direction, gusts)
- Precipitation probability
- Cardinal wind directions with degree readings

### 6-Day Weather Forecast
- Daily weather conditions
- High and low temperatures
- Weather descriptions
- Weather condition icons
- Day-of-week display

### Smart City Search
- Instant search with auto-complete
- 200+ pre-populated US cities
- Case-insensitive matching
- Quick city selection

### Modern UI Features
- Dark theme with professional styling
- Responsive grid layout
- Clear data visualization
- Smooth transitions
- Error handling with user feedback

## Technical Details

### Project Structure
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

# README.md

# Modern Weather Forecast Application

A sophisticated desktop weather application featuring a modern dark theme interface, built with PyQt6 and the Tomorrow.io API. Delivers comprehensive weather information with an intuitive user experience.

![Weather App Screenshot]
*(Screenshot to be added)*

## Core Features

### Real-Time Weather Data
- **Current Conditions**
  - Temperature & "Feels Like" readings
  - Wind metrics (speed, direction, gusts)
  - Precipitation probability
  - Cardinal wind direction with degree readings

### Extended Forecast
- **6-Day Outlook**
  - Daily high/low temperatures
  - Weather condition descriptions
  - Precipitation probability
  - Weather condition icons
  - Day-of-week display

### User Interface
- **Smart City Search**
  - Real-time autocomplete
  - Curated database of US cities
  - Case-insensitive matching
  - Instant results

- **Professional Design**
  - Modern dark theme
  - Responsive grid layout
  - Clear data visualization
  - Intuitive controls
  - Error handling with feedback

## Technical Implementation

### Project Architecture
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

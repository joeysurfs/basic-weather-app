# README.md

# Weather Forecast Application

A modern weather application built with PyQt6 that utilizes the Tomorrow.io API to provide detailed weather information for US cities.

### Example
![weather-example](https://github.com/user-attachments/assets/df1c3dae-298b-4f4a-b12d-f8bc7121a823)

## Features

- **Modern Dark Theme UI**: Sleek, professional design with a dark color scheme
- **Real-time Weather Data**: 
  - Current temperature
  - "Feels like" temperature
  - Wind speed, direction, and gusts
  - Precipitation probability
- **Smart City Search**: 
  - Auto-complete functionality
  - Pre-populated with common US cities
  - Case-insensitive search
- **Wind Direction Display**: 
  - Cardinal directions (N, NE, E, SE, S, SW, W, NW)
  - Degree measurements included
- **Rate Limiting**: Built-in API call management to stay within usage limits

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

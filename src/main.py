import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLineEdit, QPushButton, QLabel, QCompleter, QGridLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont, QIcon, QPixmap
import json
from api_handler import get_weather_data
from datetime import datetime
import os
import logging
from pathlib import Path

# Add logger configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class WeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather Forecast")
        self.setFixedSize(1400, 1200)

        # --- UPDATED STYLES BELOW ---
        self.setStyleSheet("""
            /* ----------- Main Window & General Widgets ----------- */
            QMainWindow {
                background-color: #2c3e50;
            }
            QWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Open Sans', 'Segoe UI', sans-serif;
            }
            
            /* ----------- Labels ----------- */
            QLabel {
                color: #ecf0f1;
            }

            /* ----------- Line Edit (Search Input) ----------- */
            QLineEdit {
                padding: 15px;
                border: 2px solid #2980b9;
                border-radius: 10px;
                background-color: #34495e;
                color: #ecf0f1;
                font-size: 16px;
                min-height: 25px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #3b5365;
            }
            QLineEdit::placeholder {
                color: #95a5a6;
            }

            /* ----------- Push Button (Get Weather) ----------- */
            QPushButton {
                background-color: #2980b9;
                color: #ecf0f1;
                padding: 15px 30px;
                border-radius: 10px;
                font-weight: 600;
                font-size: 16px;
                border: none;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #1c5980;
            }

            /* ----------- Result Card ----------- */
            #resultCard {
                background-color: #2c3e50;
                border: 1px solid #2c3e50;
                border-radius: 15px;
                /* Reduced padding and margin so it's more compact */
                padding: 20px;
                margin: 20px;
            }
            
            /* ----------- Completer ----------- */
            QCompleter {
                background-color: #34495e;
                color: #ecf0f1;
            }

            /* ----------- Weather Value Labels ----------- */
            .weather-value {
                /* Decreased font size from 42 to 36 for a better fit */
                font-size: 36px;
                color: #ecf0f1;
                padding: 20px;
                background-color: #34495e;
                border-radius: 10px;
            }
            .weather-label {
                /* Slightly smaller text for the descriptive label */
                font-size: 14px;
                color: #bdc3c7;
                padding: 10px;
            }

            /* ----------- Separator ----------- */
            QFrame#separator {
                background-color: #404040;
                margin: 10px 0px;
            }
            
            /* ----------- Forecast Panel ----------- */
            QWidget#forecastPanel {
                background-color: #34495e;
                border-radius: 12px;
                padding: 20px;
                min-width: 160px;
                max-width: 200px;
                min-height: 220px;
            }

            /* ----------- Weather Icons ----------- */
            QLabel[iconLabel="true"] {
                background-color: transparent;
                border: none;
                padding: 0px;
            }
        """)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Reduced the large margins and spacing at the top/bottom
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(20)

        # Title
        title = QLabel("Weather Forecast")
        title.setFont(QFont("Open Sans", 28, QFont.Weight.Bold))  # Slightly smaller
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Load cities for autocomplete
        with open('src/data/cities.json', 'r') as f:
            self.cities = json.load(f)['cities']

        # Search input with autocomplete
        self.search_label = QLabel("Enter City (e.g., Los Angeles, CA)")
        self.search_label.setFont(QFont("Open Sans", 12))
        layout.addWidget(self.search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search...")
        self.search_input.setFixedWidth(400)
        completer = QCompleter(self.cities)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.search_input.setCompleter(completer)
        layout.addWidget(self.search_input)

        # Search button
        self.search_button = QPushButton("Get Weather")
        self.search_button.setFixedWidth(200)
        self.search_button.clicked.connect(self.fetch_weather)
        layout.addWidget(self.search_button)

        # Results card with grid layout
        self.result_widget = QWidget()
        self.result_widget.setObjectName("resultCard")
        self.result_widget.setMinimumHeight(700)  # Slightly less to show more info quickly
        result_layout = QVBoxLayout(self.result_widget)

        self.weather_title = QLabel()
        self.weather_title.setFont(QFont("Open Sans", 18, QFont.Weight.Bold))
        self.weather_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.addWidget(self.weather_title)

        # Grid for weather data
        grid_layout = QGridLayout()
        # Reduced spacing and margins so the data is more compact
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(20, 20, 20, 20)

        # Temperature & Feels Like
        self.temperature = self.create_data_widget("Temperature", "°F")
        self.feels_like = self.create_data_widget("Feels Like", "°F")
        grid_layout.addWidget(self.temperature, 0, 0)
        grid_layout.addWidget(self.feels_like, 1, 0)

        # Separator line
        separator = QWidget()
        separator.setObjectName("separator")
        separator.setFixedHeight(1)
        result_layout.addWidget(separator)

        # Wind section
        self.wind_speed = self.create_data_widget("Wind Speed", "mph")
        self.wind_direction = self.create_data_widget("Wind Direction", "°")
        self.wind_gust = self.create_data_widget("Wind Gust", "mph")
        grid_layout.addWidget(self.wind_speed, 0, 1)
        grid_layout.addWidget(self.wind_direction, 0, 2)
        grid_layout.addWidget(self.wind_gust, 1, 1)

        # Precipitation probability
        self.precip_prob = self.create_data_widget("Precipitation Chance", "%")
        grid_layout.addWidget(self.precip_prob, 1, 2)

        result_layout.addLayout(grid_layout)
        layout.addWidget(self.result_widget)
        self.result_widget.hide()

        # Forecast label
        forecast_label = QLabel("6-Day Forecast")
        forecast_label.setFont(QFont("Open Sans", 20, QFont.Weight.Bold))
        forecast_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.addWidget(forecast_label)
        
        # Create forecast container
        self.forecast_container = QWidget()
        forecast_layout = QHBoxLayout(self.forecast_container)
        forecast_layout.setSpacing(15)
        forecast_layout.setContentsMargins(15, 20, 15, 20)
        self.forecast_container.setMinimumHeight(300)

        # Create 6 day forecast panels
        self.forecast_panels = []
        for _ in range(6):
            panel = self.create_forecast_panel()
            self.forecast_panels.append(panel)
            forecast_layout.addWidget(panel)
        
        result_layout.addWidget(self.forecast_container)
        layout.addStretch()

        # Adjust column/row stretching
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(2, 1)
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 1)

    def create_data_widget(self, label_text, unit):
        widget = QWidget()
        widget.setMinimumSize(280, 170)  # Slightly smaller than before
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        value_label = QLabel()
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Decreased from 42 to 36 in the stylesheet, so no need to re-override here
        value_label.setFont(QFont("Open Sans", 36, QFont.Weight.Bold))
        value_label.setProperty("class", "weather-value")
        value_label.setMinimumHeight(50)
        
        desc_label = QLabel(f"{label_text}\n{unit}")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setFont(QFont("Open Sans", 14))
        desc_label.setProperty("class", "weather-label")
        
        layout.addWidget(value_label)
        layout.addWidget(desc_label)
        
        widget.value_label = value_label
        widget.desc_label = desc_label
        
        return widget

    def create_forecast_panel(self):
        panel = QWidget()
        panel.setObjectName("forecastPanel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)

        # Day label
        day_label = QLabel()
        day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        day_label.setFont(QFont("Open Sans", 14, QFont.Weight.Bold))
        layout.addWidget(day_label)
        
        # Create horizontal container for icon and precipitation
        icon_container = QWidget()
        icon_layout = QHBoxLayout(icon_container)
        # Remove margins to allow natural centering
        icon_layout.setContentsMargins(0, 0, 0, 0)
        # Increase spacing between icon and percentage
        icon_layout.setSpacing(8)
        
        # Add stretching space on the left
        icon_layout.addStretch(1)
        
        # Weather icon
        weather_icon = QLabel()
        weather_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        weather_icon.setFixedSize(64, 64)
        icon_layout.addWidget(weather_icon)
        
        # Precipitation probability
        precip_label = QLabel()
        precip_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        precip_label.setFont(QFont("Open Sans", 11))
        precip_label.setStyleSheet("""
            color: #3498db;
            margin-left: 4px;
        """)
        icon_layout.addWidget(precip_label)
        
        # Add stretching space on the right
        icon_layout.addStretch(1)
        
        layout.addWidget(icon_container)
        
        # Weather description
        weather_desc = QLabel()
        weather_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        weather_desc.setWordWrap(True)
        weather_desc.setFont(QFont("Open Sans", 12))
        layout.addWidget(weather_desc)
        
        # Temperature
        temp_label = QLabel()
        temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        temp_label.setFont(QFont("Open Sans", 13))
        layout.addWidget(temp_label)
        
        # Store labels as attributes
        panel.day_label = day_label
        panel.weather_icon = weather_icon
        panel.weather_desc = weather_desc
        panel.temp_label = temp_label
        panel.precip_label = precip_label
        
        return panel

    def load_weather_icon(self, weather_code):
        """Load weather icon based on weather code"""
        # Get absolute path to icons directory
        base_path = Path(__file__).parent
        icon_path = base_path / "data" / "weather-icons" / f"{weather_code}.png"
        
        logger.debug(f"Attempting to load icon from: {icon_path}")
        
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path))
            if pixmap.isNull():
                logger.error(f"Failed to load icon: {icon_path}")
                return QPixmap()
            logger.debug(f"Successfully loaded icon: {icon_path}")
            return pixmap
        else:
            logger.error(f"Icon file not found: {icon_path}")
            return QPixmap()

    def update_forecast_panel(self, panel, forecast):
        """Update a forecast panel with weather data"""
        try:
            # Format date
            date = datetime.strptime(forecast['date'], '%Y-%m-%d')
            panel.day_label.setText(date.strftime('%a'))
            
            # Load and set weather icon
            weather_code = forecast['weatherCode']
            icon = self.load_weather_icon(weather_code)
            if not icon.isNull():
                panel.weather_icon.setPixmap(icon.scaled(
                    64, 64,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
                panel.weather_icon.setProperty("iconLabel", "true")
            
            # Set weather description and temperature
            panel.weather_desc.setText(forecast['weatherDesc'])
            panel.temp_label.setText(f"{forecast['tempHigh']}°↑  {forecast['tempLow']}°↓")
            
            # Update precipitation probability (minimalist style)
            precip = forecast['precipitationProbability']
            panel.precip_label.setText(f"{precip}%")
            
            logger.debug(f"Updated panel - Day: {date.strftime('%a')}, "
                      f"Code: {weather_code}, "
                      f"Desc: {forecast['weatherDesc']}")
            
        except Exception as e:
            logger.error(f"Error updating forecast panel: {str(e)}")
            panel.weather_desc.setText("Error")
            panel.temp_label.setText("--")

    @pyqtSlot()
    def fetch_weather(self):
        city = self.search_input.text().strip()
        if not city:
            self.show_error("Please enter a city name")
            return

        try:
            self.weather_title.setText("Fetching weather data...")
            self.result_widget.show()
            QApplication.processEvents()

            weather = get_weather_data(city)
            if weather:
                # Update city name
                self.weather_title.setText(f"{city}")
                
                # Update current weather values
                if 'temperature' in weather:
                    self.temperature.value_label.setText(f"{weather['temperature']}°")
                    self.feels_like.value_label.setText(f"{weather['temperatureApparent']}°")
                    self.wind_speed.value_label.setText(f"{weather['windSpeed']}")
                    self.wind_direction.value_label.setText(f"{weather['windDirection']}")
                    self.wind_gust.value_label.setText(f"{weather['windGust']}")
                    self.precip_prob.value_label.setText(f"{weather['precipitationProbability']}")
                
                # Update forecast panels
                if 'forecast' in weather and weather['forecast']:
                    for i, forecast in enumerate(weather['forecast']):
                        if i < len(self.forecast_panels):
                            self.update_forecast_panel(self.forecast_panels[i], forecast)
                
                self.result_widget.show()
            else:
                self.show_error("Could not retrieve weather data")
        except Exception as e:
            print(f"Error in fetch_weather: {str(e)}")
            self.show_error(str(e))

    def show_error(self, message):
        self.weather_title.setText("Error")
        self.temperature.value_label.setText(message)
        self.feels_like.value_label.setText("")
        self.result_widget.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec())

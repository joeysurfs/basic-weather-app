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
        # Remove fixed size to allow fullscreen
        # self.setFixedSize(1400, 1200)

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
                padding: 10px;
                border: 2px solid #2980b9;
                border-radius: 8px;
                background-color: #34495e;
                color: #ecf0f1;
                font-size: 14px;
                min-height: 20px;
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
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                border: none;
                min-width: 150px;
                min-height: 40px; /* Ensure touch-friendly size */
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #1c5980;
            }

            /* ----------- Close Button ----------- */
            #closeButton {
                background-color: #c0392b;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                min-width: 60px;
                min-height: 40px;
                padding: 5px;
                margin: 8px;
            }
            #closeButton:hover {
                background-color: #e74c3c;
            }
            #closeButton:pressed {
                background-color: #a93226;
            }

            /* ----------- Result Card ----------- */
            #resultCard {
                background-color: #2c3e50;
                border: 1px solid #2c3e50;
                border-radius: 12px;
                /* Reduced padding for smaller screen */
                padding: 10px;
                margin: 10px;
            }
            
            /* ----------- Completer ----------- */
            QCompleter {
                background-color: #34495e;
                color: #ecf0f1;
            }

            /* ----------- Weather Value Labels ----------- */
            .weather-value {
                /* Decreased font size for 7-inch display */
                font-size: 24px;
                color: #ecf0f1;
                padding: 10px;
                background-color: #34495e;
                border-radius: 8px;
            }
            .weather-label {
                /* Smaller text for the descriptive label */
                font-size: 12px;
                color: #bdc3c7;
                padding: 5px;
            }

            /* ----------- Separator ----------- */
            QFrame#separator {
                background-color: #404040;
                margin: 5px 0px;
            }
            
            /* ----------- Forecast Panel ----------- */
            QWidget#forecastPanel {
                background-color: #34495e;
                border-radius: 10px;
                padding: 10px;
                min-width: 120px;
                max-width: 150px;
                min-height: 180px;
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
        
        # Reduced the margins and spacing even further for small screen
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(10)

        # Create a top bar with grid layout for better centering
        top_bar = QWidget()
        top_bar_layout = QGridLayout(top_bar)
        top_bar_layout.setContentsMargins(0, 0, 0, 0)
        top_bar_layout.setSpacing(0)
        
        # Add empty widget to first column for balance
        empty_widget = QWidget()
        empty_widget.setFixedWidth(60)  # Same width as close button
        top_bar_layout.addWidget(empty_widget, 0, 0)
        
        # Add title in the center column
        title = QLabel("Weather Forecast")
        title.setFont(QFont("Open Sans", 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_bar_layout.addWidget(title, 0, 1)
        
        # Add close button to the right column
        self.close_button = QPushButton("×")
        self.close_button.setObjectName("closeButton")
        self.close_button.setToolTip("Close Application")
        self.close_button.clicked.connect(self.close)
        top_bar_layout.addWidget(self.close_button, 0, 2, Qt.AlignmentFlag.AlignRight)
        
        # Set column stretching to ensure title stays centered
        top_bar_layout.setColumnStretch(0, 0)  # Left empty space doesn't stretch
        top_bar_layout.setColumnStretch(1, 1)  # Center column stretches
        top_bar_layout.setColumnStretch(2, 0)  # Right column doesn't stretch
        
        # Add the top bar to the main layout
        layout.addWidget(top_bar)

        # Load cities for autocomplete
        with open('src/data/cities.json', 'r') as f:
            self.cities = json.load(f)['cities']

        # Create a container for all search-related elements
        search_container = QWidget()
        search_container_layout = QVBoxLayout(search_container)
        search_container_layout.setContentsMargins(10, 10, 10, 10)
        search_container_layout.setSpacing(8)
        
        # Search input with autocomplete - now in container
        self.search_label = QLabel("Enter City (e.g., Los Angeles, CA)")
        self.search_label.setFont(QFont("Open Sans", 10))
        self.search_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        search_container_layout.addWidget(self.search_label)

        # Create a layout for search input and button
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)
        
        # Add stretch to center the input elements
        input_layout.addStretch(1)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search...")
        self.search_input.setFixedWidth(300)  # Narrower for small screen
        completer = QCompleter(self.cities)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.search_input.setCompleter(completer)
        input_layout.addWidget(self.search_input)

        # Search button
        self.search_button = QPushButton("Get Weather")
        self.search_button.setFixedWidth(150)  # Narrower but still touch-friendly
        self.search_button.clicked.connect(self.fetch_weather)
        input_layout.addWidget(self.search_button)
        
        # Add stretch to center the input elements
        input_layout.addStretch(1)
        
        # Add the input layout to the container
        search_container_layout.addLayout(input_layout)
        
        # Add search container to main layout
        layout.addWidget(search_container)

        # Results card with grid layout
        self.result_widget = QWidget()
        self.result_widget.setObjectName("resultCard")
        self.result_widget.setMinimumHeight(400)  # Reduced for smaller screen
        result_layout = QVBoxLayout(self.result_widget)

        self.weather_title = QLabel()
        self.weather_title.setFont(QFont("Open Sans", 16, QFont.Weight.Bold))
        self.weather_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.addWidget(self.weather_title)

        # Grid for weather data
        grid_layout = QGridLayout()
        # Further reduced spacing and margins for 7" display
        grid_layout.setSpacing(10)
        grid_layout.setContentsMargins(10, 10, 10, 10)

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
        forecast_label.setFont(QFont("Open Sans", 16, QFont.Weight.Bold))
        forecast_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.addWidget(forecast_label)
        
        # Create forecast container
        self.forecast_container = QWidget()
        forecast_layout = QHBoxLayout(self.forecast_container)
        forecast_layout.setSpacing(8)
        forecast_layout.setContentsMargins(5, 10, 5, 10)
        self.forecast_container.setMinimumHeight(200)  # Reduced height

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
        widget.setMinimumSize(150, 120)  # Smaller size for 7" display
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        
        value_label = QLabel()
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFont(QFont("Open Sans", 24, QFont.Weight.Bold))  # Decreased from 36
        value_label.setProperty("class", "weather-value")
        value_label.setMinimumHeight(40)
        
        desc_label = QLabel(f"{label_text}\n{unit}")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setFont(QFont("Open Sans", 12))  # Smaller font
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
        layout.setSpacing(4)  # Reduced spacing
        layout.setContentsMargins(5, 5, 5, 5)  # Reduced margins

        # Day label
        day_label = QLabel()
        day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        day_label.setFont(QFont("Open Sans", 12, QFont.Weight.Bold))  # Smaller font
        layout.addWidget(day_label)
        
        # Create horizontal container for icon and precipitation
        icon_container = QWidget()
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(4)  # Reduced spacing
        
        icon_layout.addStretch(1)
        
        # Weather icon - smaller for 7" screen
        weather_icon = QLabel()
        weather_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        weather_icon.setFixedSize(48, 48)  # Reduced size
        icon_layout.addWidget(weather_icon)
        
        # Precipitation probability
        precip_label = QLabel()
        precip_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        precip_label.setFont(QFont("Open Sans", 10))  # Smaller font
        precip_label.setStyleSheet("""
            color: #3498db;
            margin-left: 2px;
        """)
        icon_layout.addWidget(precip_label)
        
        icon_layout.addStretch(1)
        
        layout.addWidget(icon_container)
        
        # Weather description
        weather_desc = QLabel()
        weather_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        weather_desc.setWordWrap(True)
        weather_desc.setFont(QFont("Open Sans", 10))  # Smaller font
        layout.addWidget(weather_desc)
        
        # Temperature
        temp_label = QLabel()
        temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        temp_label.setFont(QFont("Open Sans", 11))  # Smaller font
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
                    48, 48,  # Reduced icon size
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
                panel.weather_icon.setProperty("iconLabel", "true")
            
            # Set weather description and temperature
            panel.weather_desc.setText(forecast['weatherDesc'])
            panel.temp_label.setText(f"{forecast['tempHigh']}°↑  {forecast['tempLow']}°↓")
            
            # Update precipitation probability
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
    window.showFullScreen()  # Show fullscreen instead of normal window
    sys.exit(app.exec())

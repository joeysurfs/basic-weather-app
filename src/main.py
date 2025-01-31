import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLineEdit, QPushButton, QLabel, QCompleter, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont, QIcon
import json
from api_handler import get_weather_data

class WeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather Forecast")
        self.setFixedSize(700, 600)  # Increased size for new data
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit {
                padding: 12px;
                border: 2px solid #333333;
                border-radius: 8px;
                background-color: #2d2d2d;
                color: #ffffff;
                font-size: 14px;
                selection-background-color: #404040;
            }
            QLineEdit:focus {
                border: 2px solid #0d47a1;
                background-color: #363636;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0a367a;
            }
            #resultCard {
                background-color: #1e1e1e;
                border-radius: 12px;
                padding: 20px;
                margin: 20px;
                border: 1px solid #1e1e1e;
            }
            QCompleter {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            .weather-value {
                font-size: 24px;
                color: #ffffff;
                padding: 10px;
            }
            .weather-label {
                font-size: 12px;
                color: #808080;
            }
            QFrame#separator {
                background-color: #404040;
                margin: 10px 0px;
            }
        """)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title
        title = QLabel("Weather Forecast")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Load cities for autocomplete
        with open('src/data/cities.json', 'r') as f:
            self.cities = json.load(f)['cities']

        # Search input with autocomplete
        self.search_label = QLabel("Enter City (e.g., Los Angeles, CA)")
        self.search_label.setFont(QFont("Segoe UI", 12))
        layout.addWidget(self.search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search...")
        completer = QCompleter(self.cities)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.search_input.setCompleter(completer)
        layout.addWidget(self.search_input)

        # Update placeholder text color
        self.search_input.setStyleSheet("""
            QLineEdit::placeholder {
                color: #808080;
            }
        """)

        # Search button
        self.search_button = QPushButton("Get Weather")
        self.search_button.clicked.connect(self.fetch_weather)
        layout.addWidget(self.search_button)

        # Results card with grid layout
        self.result_widget = QWidget()
        self.result_widget.setObjectName("resultCard")
        result_layout = QVBoxLayout(self.result_widget)

        self.weather_title = QLabel()
        self.weather_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.weather_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.addWidget(self.weather_title)

        # Grid for weather data
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        # Temperature section
        self.temperature = self.create_data_widget("Temperature", "°F")
        self.feels_like = self.create_data_widget("Feels Like", "°F")
        grid_layout.addWidget(self.temperature, 0, 0)
        grid_layout.addWidget(self.feels_like, 1, 0)

        # Add separator
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

        # Add stretching space at bottom
        layout.addStretch()

    def create_data_widget(self, label_text, unit):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        value_label = QLabel()
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFont(QFont("Segoe UI", 24))
        value_label.setProperty("class", "weather-value")
        
        desc_label = QLabel(f"{label_text}\n{unit}")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setProperty("class", "weather-label")
        
        layout.addWidget(value_label)
        layout.addWidget(desc_label)
        
        # Store labels as attributes of widget for easy access
        widget.value_label = value_label
        widget.desc_label = desc_label
        
        return widget

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
                self.weather_title.setText(f"{weather['city']}")
                
                # Update temperature values
                self.temperature.value_label.setText(f"{weather['temperature']}")
                self.feels_like.value_label.setText(f"{weather['temperatureApparent']}")
                
                # Update wind values
                self.wind_speed.value_label.setText(f"{weather['windSpeed']}")
                self.wind_direction.value_label.setText(f"{weather['windDirection']}")
                self.wind_gust.value_label.setText(f"{weather['windGust']}")
                
                # Update precipitation probability
                self.precip_prob.value_label.setText(f"{weather['precipitationProbability']}")
                
                self.result_widget.show()
            else:
                self.show_error("Could not retrieve weather data")
        except Exception as e:
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
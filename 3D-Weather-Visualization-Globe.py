import tkinter as tk
from tkinter import ttk, Frame
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import requests
from matplotlib import cm
from datetime import datetime
import random
import math

class WeatherGlobeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Weather Globe")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e2e')
        
        self.api_key = "YOUR_OPENWEATHERMAP_API_KEY"  # Replace with your actual API key
        self.setup_ui()
        self.weather_data = {}
        self.selected_location = None
        self.rotation_active = True
        self.current_lon = 0  # Starting longitude for view
        
        # Create the initial globe
        self.create_globe()
        
        # Start the rotation
        self.root.after(100, self.rotate_view)
    
    def setup_ui(self):
        """Create the application UI"""
        # Main frame
        main_frame = Frame(self.root, bg='#1e1e2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for globe
        self.globe_frame = Frame(main_frame, bg='#1e1e2e')
        self.globe_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Right panel for controls and info
        right_panel = Frame(main_frame, bg='#1e1e2e', width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        # Weather information panel
        info_frame = Frame(right_panel, bg='#282a36', padx=15, pady=15)
        info_frame.pack(fill=tk.X, pady=10)
        
        # Title
        title_label = tk.Label(info_frame, text="Weather Information", 
                             font=("Arial", 16, "bold"), bg='#282a36', fg='white')
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Location
        self.location_var = tk.StringVar(value="No location selected")
        location_label = tk.Label(info_frame, textvariable=self.location_var, 
                                font=("Arial", 12), bg='#282a36', fg='white')
        location_label.pack(anchor=tk.W, pady=5)
        
        # Weather details frame
        weather_details = Frame(info_frame, bg='#282a36')
        weather_details.pack(fill=tk.X, pady=10)
        
        # Temperature
        self.temp_var = tk.StringVar(value="-- °C")
        self.temp_label = tk.Label(weather_details, textvariable=self.temp_var, 
                                 font=("Arial", 24), bg='#282a36', fg='white')
        self.temp_label.pack(anchor=tk.W)
        
        # Weather condition
        self.condition_var = tk.StringVar(value="--")
        condition_label = tk.Label(weather_details, textvariable=self.condition_var, 
                                  font=("Arial", 12), bg='#282a36', fg='white')
        condition_label.pack(anchor=tk.W, pady=5)
        
        # Details grid
        details_grid = Frame(weather_details, bg='#282a36')
        details_grid.pack(fill=tk.X, pady=5)
        
        # Humidity
        tk.Label(details_grid, text="Humidity:", bg='#282a36', fg='#8be9fd').grid(row=0, column=0, sticky='w')
        self.humidity_var = tk.StringVar(value="-- %")
        tk.Label(details_grid, textvariable=self.humidity_var, bg='#282a36', fg='white').grid(row=0, column=1, sticky='w')
        
        # Wind
        tk.Label(details_grid, text="Wind:", bg='#282a36', fg='#8be9fd').grid(row=1, column=0, sticky='w')
        self.wind_var = tk.StringVar(value="-- m/s")
        tk.Label(details_grid, textvariable=self.wind_var, bg='#282a36', fg='white').grid(row=1, column=1, sticky='w')
        
        # Pressure
        tk.Label(details_grid, text="Pressure:", bg='#282a36', fg='#8be9fd').grid(row=2, column=0, sticky='w')
        self.pressure_var = tk.StringVar(value="-- hPa")
        tk.Label(details_grid, textvariable=self.pressure_var, bg='#282a36', fg='white').grid(row=2, column=1, sticky='w')
        
        # Controls frame
        controls_frame = Frame(right_panel, bg='#282a36', padx=15, pady=15)
        controls_frame.pack(fill=tk.X, pady=10)
        
        # Layer controls title
        tk.Label(controls_frame, text="Display Controls", font=("Arial", 12, "bold"), 
               bg='#282a36', fg='white').pack(anchor=tk.W, pady=(0, 10))
        
        # Auto-rotation toggle
        self.rotation_var = tk.BooleanVar(value=True)
        rotation_check = tk.Checkbutton(controls_frame, text="Auto-Rotation", variable=self.rotation_var, 
                                      bg='#282a36', fg='white', selectcolor='#44475a',
                                      command=self.toggle_rotation)
        rotation_check.pack(anchor=tk.W, pady=5)
        
        # Search location
        search_frame = Frame(right_panel, bg='#282a36', padx=15, pady=15)
        search_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(search_frame, text="Search Location", font=("Arial", 12, "bold"), 
               bg='#282a36', fg='white').pack(anchor=tk.W, pady=(0, 10))
        
        search_entry_frame = Frame(search_frame, bg='#282a36')
        search_entry_frame.pack(fill=tk.X, pady=5)
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_entry_frame, textvariable=self.search_var, 
                              bg='#44475a', fg='white', insertbackground='white')
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        search_button = tk.Button(search_entry_frame, text="Search", bg='#6272a4', fg='white',
                                command=self.search_location)
        search_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Popular locations
        locations_frame = Frame(search_frame, bg='#282a36')
        locations_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(locations_frame, text="Popular Locations:", bg='#282a36', fg='white').pack(anchor=tk.W, pady=(0, 5))
        
        # Location buttons
        locations_grid = Frame(locations_frame, bg='#282a36')
        locations_grid.pack(fill=tk.X)
        
        locations = [
            ("New York", 40.71, -74.01),
            ("London", 51.51, -0.13),
            ("Tokyo", 35.68, 139.77),
            ("Sydney", -33.87, 151.21),
            ("Delhi", 28.61, 77.23),
            ("Cairo", 30.04, 31.24)
        ]
        
        row, col = 0, 0
        for name, lat, lon in locations:
            location_btn = tk.Button(locations_grid, text=name, bg='#44475a', fg='white',
                                   command=lambda lat=lat, lon=lon, name=name: self.set_location(name, lat, lon))
            location_btn.grid(row=row, column=col, padx=2, pady=2, sticky='ew')
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready. Click on the globe or search for a location.")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, 
                                 bd=1, relief=tk.SUNKEN, anchor=tk.W, bg='#282a36', fg='#6272a4')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_globe(self):
        """Create the 3D globe visualization"""
        # Create figure and axes
        self.fig = plt.figure(figsize=(8, 8), facecolor='#1e1e2e')
        self.ax = self.fig.add_subplot(111, projection=ccrs.Orthographic(0, 20))
        
        # Add map features
        self.ax.stock_img()  # Use a built-in image of the Earth
        self.ax.coastlines(linewidth=0.5, color='#ffffff')
        self.ax.add_feature(cfeature.BORDERS, linewidth=0.3, color='#ffffff', alpha=0.5)
        
        # Add gridlines
        self.ax.gridlines(color='white', alpha=0.3, linestyle=':')
        
        # Embed in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.globe_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Connect click event
        self.canvas.mpl_connect('button_press_event', self.on_globe_click)
        
    def rotate_view(self):
        """Rotate the globe view"""
        if self.rotation_active:
            self.current_lon = (self.current_lon + 2) % 360
            self.ax.clear()
            self.ax.stock_img()
            self.ax.coastlines(linewidth=0.5, color='#ffffff')
            self.ax.add_feature(cfeature.BORDERS, linewidth=0.3, color='#ffffff', alpha=0.5)
            self.ax.gridlines(color='white', alpha=0.3, linestyle=':')
            
            self.ax.projection = ccrs.Orthographic(self.current_lon, 20)
            self.canvas.draw()
            
        # Schedule next rotation
        self.root.after(100, self.rotate_view)
        
    def toggle_rotation(self):
        """Toggle globe rotation on/off"""
        self.rotation_active = self.rotation_var.get()
        
    def on_globe_click(self, event):
        """Handle click on the globe"""
        if event.inaxes != self.ax:
            return
            
        try:
            # This is approximate and won't work perfectly on globe edges
            x, y = event.xdata, event.ydata
            
            # Try to convert to lat/lon - this is an approximation for the Orthographic projection
            center_lon = self.current_lon
            center_lat = 20  # Our fixed latitude center
            
            # Get the current display extent
            x_min, x_max = self.ax.get_xlim()
            y_min, y_max = self.ax.get_ylim()
            width = x_max - x_min
            height = y_max - y_min
            
            # Normalize coordinates to [-1, 1]
            x_norm = 2 * (x - x_min) / width - 1
            y_norm = 2 * (y - y_min) / height - 1
            
            # Simple approximation for orthographic projection
            # (not perfect but works for demonstration)
            if x_norm**2 + y_norm**2 <= 1:  # Check if within globe circle
                lon = center_lon + math.degrees(math.atan2(x_norm, -y_norm))
                lat = math.degrees(math.asin(y_norm)) + center_lat
                
                # Normalize longitude to [-180, 180]
                lon = ((lon + 180) % 360) - 180
                
                self.status_var.set(f"Selected location: Lat {lat:.2f}, Lon {lon:.2f}")
                self.fetch_weather_for_coords(lat, lon)
            else:
                self.status_var.set("Click inside the globe to select a location")
        except Exception as e:
            self.status_var.set(f"Error processing click: {str(e)}")
        
    def search_location(self):
        """Search for a location by name"""
        location = self.search_var.get().strip()
        if not location:
            return
            
        self.status_var.set(f"Searching for {location}...")
        
        # For a real app, use OpenWeatherMap's Geocoding API:
        # response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={self.api_key}")
        # data = response.json()
        # if data:
        #     lat = data[0]['lat']
        #     lon = data[0]['lon']
        #     name = data[0]['name']
        #     self.set_location(name, lat, lon)
        
        # For demonstration, use predefined locations or generate random ones
        common_locations = {
            "new york": (40.71, -74.01),
            "london": (51.51, -0.13),
            "paris": (48.85, 2.35),
            "tokyo": (35.68, 139.77),
            "sydney": (-33.87, 151.21),
            "delhi": (28.61, 77.23),
            "cairo": (30.04, 31.24),
            "rio": (-22.91, -43.17),
            "moscow": (55.75, 37.62),
            "beijing": (39.91, 116.40),
            "india": (20.59, 78.96),
            "usa": (37.09, -95.71),
            "china": (35.86, 104.19),
            "russia": (61.52, 105.31),
            "brazil": (-14.24, -51.92),
            "canada": (56.13, -106.35),
            "australia": (-25.27, 133.77),
            "europe": (54.53, 15.55),
            "africa": (8.78, 34.51),
            "asia": (34.05, 100.62)
        }
        
        location_lower = location.lower()
        if location_lower in common_locations:
            lat, lon = common_locations[location_lower]
            self.set_location(location.title(), lat, lon)
        else:
            # Use random location for demonstration
            lat = random.uniform(-60, 70)
            lon = random.uniform(-180, 180)
            self.set_location(f"Location near {location}", lat, lon)
        
    def set_location(self, name, lat, lon):
        """Set a specific location and fetch its weather"""
        self.status_var.set(f"Setting location to {name} ({lat:.2f}, {lon:.2f})")
        
        # Stop rotation
        self.rotation_active = False
        self.rotation_var.set(False)
        
        # Update globe view
        self.ax.clear()
        self.ax.stock_img()
        self.ax.coastlines(linewidth=0.5, color='#ffffff')
        self.ax.add_feature(cfeature.BORDERS, linewidth=0.3, color='#ffffff', alpha=0.5)
        self.ax.gridlines(color='white', alpha=0.3, linestyle=':')
        
        # Center the globe on this location
        self.ax.projection = ccrs.Orthographic(lon, lat)
        
        # Mark the location
        self.ax.plot([lon], [lat], 'ro', markersize=8, transform=ccrs.PlateCarree())
        
        # Update display
        self.canvas.draw()
        
        # Fetch weather
        self.fetch_weather_for_coords(lat, lon, name)
        
    def fetch_weather_for_coords(self, lat, lon, name=None):
        """Fetch weather data for coordinates"""
        if name is None:
            name = f"Location ({lat:.2f}, {lon:.2f})"
            
        self.status_var.set(f"Fetching weather for {name}...")
        
        # For a real app, use actual API:
        # response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={self.api_key}")
        # data = response.json()
        
        # For demonstration, generate realistic weather data based on location and date
        curr_month = datetime.now().month  # 1-12
        
        # More realistic temperature based on latitude and season
        season_factor = abs(math.sin(math.radians((curr_month - 1) * 30)))
        if lat > 0:  # Northern hemisphere
            temp_base = 30 - abs(lat) * 0.5  # Hotter at equator, colder at poles
            seasonal_temp = 15 * season_factor if curr_month >= 4 and curr_month <= 9 else -15 * season_factor
        else:  # Southern hemisphere
            temp_base = 30 - abs(lat) * 0.5
            seasonal_temp = -15 * season_factor if curr_month >= 4 and curr_month <= 9 else 15 * season_factor
            
        # Add some randomness
        temp = temp_base + seasonal_temp + random.uniform(-3, 3)
        temp = round(temp, 1)
        
        # Determine weather conditions based on temperature and randomness
        weather_types = ["Clear", "Partly Cloudy", "Cloudy", "Light Rain", "Heavy Rain", "Thunderstorm", "Snow", "Fog"]
        if temp < -5:
            weights = [0.2, 0.1, 0.1, 0, 0, 0, 0.5, 0.1]
        elif temp < 0:
            weights = [0.3, 0.2, 0.1, 0, 0, 0, 0.3, 0.1]
        elif temp < 10:
            weights = [0.3, 0.3, 0.2, 0.1, 0, 0, 0.05, 0.05]
        elif temp < 20:
            weights = [0.4, 0.2, 0.1, 0.2, 0.05, 0.05, 0, 0]
        elif temp < 30:
            weights = [0.5, 0.3, 0.1, 0.05, 0.05, 0, 0, 0]
        else:
            weights = [0.7, 0.2, 0.05, 0.05, 0, 0, 0, 0]
            
        weather = random.choices(weather_types, weights=weights)[0]
        
        # Create simulated weather data
        self.weather_data = {
            "name": name,
            "temp": temp,
            "weather": weather,
            "humidity": random.randint(30, 95),
            "pressure": random.randint(995, 1025),
            "wind_speed": round(random.uniform(0, 20), 1)
        }
        
        # Always use the same weather for the same location
        # This ensures consistent results when searching multiple times
        hash_val = hash(f"{lat:.1f},{lon:.1f}")
        random.seed(hash_val)
        self.weather_data["temp"] = round(temp_base + seasonal_temp + random.uniform(-3, 3), 1)
        self.weather_data["humidity"] = random.randint(30, 95)
        self.weather_data["pressure"] = random.randint(995, 1025)
        self.weather_data["wind_speed"] = round(random.uniform(0, 20), 1)
        
        # Reset the random seed
        random.seed()
        
        # Update UI
        self.update_weather_display()
        
    def update_weather_display(self):
        """Update the weather display with current data"""
        if not self.weather_data:
            return
            
        # Update location
        self.location_var.set(self.weather_data["name"])
        
        # Update temperature
        self.temp_var.set(f"{self.weather_data['temp']}°C")
        
        # Update condition
        self.condition_var.set(self.weather_data["weather"])
        
        # Update details
        self.humidity_var.set(f"{self.weather_data['humidity']}%")
        self.pressure_var.set(f"{self.weather_data['pressure']} hPa")
        self.wind_var.set(f"{self.weather_data['wind_speed']} m/s")
        
        # Update status
        self.status_var.set(f"Weather for {self.weather_data['name']}: {self.weather_data['temp']}°C, {self.weather_data['weather']}")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherGlobeApp(root)
    root.mainloop()
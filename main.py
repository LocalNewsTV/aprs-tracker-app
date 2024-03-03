import tkinter as tk
from tkinter import messagebox
import requests
from dotenv import load_dotenv
import os
import json
import time
import webbrowser
from datetime import datetime
from PIL import ImageTk, Image

load_dotenv()

# Image Constants
IMAGE_FOLDER = "./app_images/"
UNKNOWN_IMG = "unknown.png"
PLACEHOLDER_IMG = "smiley.png"
PARKED_IMG ="parkingspot.png"

# App Constants
CUSTOM_INFORMATION_FILE = "user_information.json"
WINDOW_SIZE = "275x275"
IMAGE_SIZE = (175, 175)  # px
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0"}

# User Information Constants
FILE = open(CUSTOM_INFORMATION_FILE, "r")
JSON_DUMP = json.load(FILE)
APP_TITLE = JSON_DUMP.get("title", "aprs.fi Companion")
CUSTOM_USER_LOCATIONS = JSON_DUMP.get('locations', {})
CUSTOM_USER_TRANSPORT = JSON_DUMP.get('transport_method', {})
API_KEY = JSON_DUMP.get('api_key', None)
class APRS_Tracker(tk.Tk):
    current_activity = "UNKNOWN"
    current_activity_image = PLACEHOLDER_IMG
    lat_long_label: tk.Label
    travel_information_label: tk.Label
    latitude: float
    longitude: float
    api_data: dict
    button: tk.Button
    isMoving: bool
    current_location: dict
    
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self.resizable(False, False)
        self.current_activity_label = tk.Label(self, text=f"Unknown")
        self.URL = f"https://api.aprs.fi/api/get?name={self.get_api_targets()}&what=loc&apikey={API_KEY}&format=json"
        picture_frame = tk.Frame(self,)
        image = Image.open(IMAGE_FOLDER + PLACEHOLDER_IMG).resize(IMAGE_SIZE, Image.LANCZOS)
        image_in_frame = ImageTk.PhotoImage(image)
        self.picture_label = tk.Label(picture_frame, image=image_in_frame)
        self.picture_label.image = image_in_frame
        self.picture_label.pack()
        
        picture_frame.pack()
        self.current_activity_label.pack()
        self.create_lat_long_label()
        self.create_travel_information_label()
        self.fetch_api_data()
        self.create_live_link_button()

    def create_travel_information_label(self,):
        """Populates the initial label for travel information (Direction + Speed)"""
        self.travel_information_label = tk.Label(self, text = "Loading Data")
        self.travel_information_label.pack()
        
    def update_travel_information_label(self,):
        course = self.api_data.get("course", None)
        speed = round(self.api_data.get("speed", 0))
        newLabel = ""
        if self.is_moving():
            newLabel = f"Travelling {course}° {self.get_direction_of_travel()} at {speed} km/h"
        self.travel_information_label.config(text=newLabel)
    
    def create_lat_long_label(self,):
        """Populates the initial Label into the application"""
        self.lat_long_label = tk.Label(self, text="Loading Data")
        self.lat_long_label.pack()
    
    def update_lat_long_label(self,):
        """Updates the label showing Latitude and Longitude with the currently stored information"""
        newLabel = f"Latitude: {self.latitude} Longitude: {self.longitude}"
        self.lat_long_label.config(text=newLabel)
    
    def create_live_link_button(self,):
        self.button = tk.Button(
            text="View in Browser",
            width=15,
            height=1,
            bg="white",
            fg="black",
        )
        self.button.bind("<Button 1>", self.handle_live_link_button_click)
        self.button.pack()
    
    def throw_error_popup(error):
        messagebox.showerror('An Error Occurred', 'Error: {error}')
    
    def handle_live_link_button_click(self, event):
        url = "https://en.aprs.fi/"
        target = self.api_data.get("name", None)
        if target:
           url += f"#!call=a%2F{target}"
        webbrowser.open(url)
    
    def get_direction_of_travel(self):
        """Converts the 'course' (angle) returned by the API into compass direction.

        Returns:
            String: Compass value based on current course
        """
        course = self.api_data.get('course', None)
        if not course:
            return ""
        if course < 22 or course > 338:
            return "N"
        elif course < 68:
            return "NE"
        elif course < 113:
            return "E"
        elif course < 158:
            return "SE"
        elif course < 203:
            return "S"
        elif course < 248:
            return "SW"
        elif course < 293:
            return "W"
        elif course <= 338:
            return "NW"
    
    def update_fields(self,):
        self.set_tracker_image_based_on_activity()
        self.update_lat_long_label()
        self.update_activity_icon()
        self.update_current_activity_label()
        self.update_travel_information_label()
        
    def update_activity_icon(self,):
        """Updates the image displayed in the app with the most recent activity"""
        try:
            image = Image.open(IMAGE_FOLDER + self.current_activity_image).resize(IMAGE_SIZE, Image.LANCZOS)
        except Exception as e:
            image = Image.open(IMAGE_FOLDER + PLACEHOLDER_IMG).resize(IMAGE_SIZE, Image.LANCZOS)
            self.throw_error_popup(e)
        image = ImageTk.PhotoImage(image)
        self.picture_label.configure(image=image)
        self.picture_label.image = image

        
    def fetch_api_data(self,):
        """Calls API to get information about all targets,
        Sorts the list of results by time and sets api_data to most recent update"""
        try:
            http_response = requests.get(url=self.URL, headers=HEADERS)
            latest_information = http_response.json().get('entries', [])
            if len(latest_information) == 0:
                return
            if len(latest_information) == 1:
                self.api_data = latest_information
            else:
                self.api_data = sorted(latest_information, key=lambda time: int(time['time']), reverse=True)[0]
            self.latitude = self.api_data.get('lat', 0)
            self.longitude = self.api_data.get('lng', 0)
            self.update_fields()
        except Exception as e:
            self.throw_error_popup(e)
        finally:
            time_til_next_update = 3 * 60 * 1000 if self.is_moving() else 15 * 60 * 1000
            self.after(time_til_next_update, lambda: self.fetch_api_data())
        
    def where_in_the_world_is_carmen_sandiego(self):
        """Using the locations in User_Information, compares latitude and longitudes to find a bounding box"""
        for location in CUSTOM_USER_LOCATIONS:
            latMin =  float(CUSTOM_USER_LOCATIONS[location]['latitude']['min']) or 0
            latMax =  float(CUSTOM_USER_LOCATIONS[location]['latitude']['max']) or 0
            longMin = float(CUSTOM_USER_LOCATIONS[location]['longitude']['min']) or 0
            longMax = float(CUSTOM_USER_LOCATIONS[location]['longitude']['max']) or 0
            if latMin < float(self.latitude) < latMax and \
                longMin < float(self.longitude) < longMax:
                self.current_location = CUSTOM_USER_LOCATIONS[location]
                return
        self.current_location = { "label": "Driving", "image": self.select_vehicle_image() }
    
    def update_current_activity_label(self,):
        """Updates the current Activity Label showing Time of last update, and activity being enacted"""
        last_captured_time = int(self.api_data.get('lasttime', 0))
        dt_object = datetime.fromtimestamp(last_captured_time)
        time_string = dt_object.strftime('%b %dth %I:%M%p')
        newLabel = f"Last seen: {time_string} {self.current_activity}"
        self.current_activity_label.config(text=newLabel)
        
    def is_moving(self, time_to_idle = 15 * 60):
        """Compares time of last broadcast to see if within params

        Args:
            time_to_idle (int, optional): User definition of when data is stale. Defaults to 15 minutes.

        Returns:
           Boolean: If current API Data is stale
        """
        last_update_time = self.api_data.get('time', 0)
        return int(last_update_time) > (int(time.time()) - time_to_idle)
    
    def set_tracker_image_based_on_activity(self,):
        """Parses the last update time and activity to determine if driving, at a location, or MIA"""
        self.where_in_the_world_is_carmen_sandiego()
        if not self.is_moving() and self.current_location['label'] == "Driving":
            self.current_location['image'] = PARKED_IMG
                
        self.current_activity = self.current_location.get('label', "Invalid Label")
        self.current_activity_image = self.current_location.get('image', PLACEHOLDER_IMG)
 
    def select_vehicle_image(self,):
        """When driving, compares the name key (Tracked ID) to match the appropriate travel image """
        last_updated_callsign = self.api_data.get('name', None)
        for entry in CUSTOM_USER_TRANSPORT:
            if CUSTOM_USER_TRANSPORT[entry]['callsign'].upper() == last_updated_callsign:
                return CUSTOM_USER_TRANSPORT[entry].get('image', PLACEHOLDER_IMG)
        return PLACEHOLDER_IMG

    def get_api_targets(self,):
        "Parses list of targets in the user_information file to use in the API Calls"
        tracking_list = ""
        for entry in CUSTOM_USER_TRANSPORT:
            tracking_list += CUSTOM_USER_TRANSPORT[entry].get("callsign", "").upper() + ","
        return tracking_list
    
if __name__ == "__main__":
    window = APRS_Tracker()
    window.mainloop()

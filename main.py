import tkinter as tk
import requests
from dotenv import load_dotenv
import os
from PIL import ImageTk, Image

load_dotenv()
TRUCK = 0
CAR = 1
TITLE = "Dad Tracker 9000"
WINDOW_SIZE = "325x325"
TRACKING_TARGETS = os.environ.get("TRACKING_TARGETS")

API_KEY = os.environ.get("API_KEY")
IMAGE_SIZE = (200, 200)  # px
TARGETS = os.environ.get("TRACKING_TARGETS").split(",")
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0"}
URL = f"https://api.aprs.fi/api/get?name={TRACKING_TARGETS}&what=loc&apikey={API_KEY}&format=json"

class DadTracker(tk.Tk):

    def __init__(self):
        self.title = TITLE
        self.config(bg='snow3')
        self.latitude = 0.00
        self.longitude = 0.00
        self.geometry(WINDOW_SIZE)
        self.resizable(False, False)
        self.api_data = {}
        self.latitude_label = tk.Label(self, text=f"Latitude: {self.latitude} Longitude: {self.longitude}")

        
        
    def fetch_api_data(self,):
        http_response = requests.get(url=URL, headers=HEADERS)
        latest = http_response.json()
        self.api_data = latest['entries'][TRUCK] if latest['entries'][TRUCK]['status_lasttime'] > latest['entries'][CAR]['status_lasttime'] else latest['entries'][CAR]
        self.after(180000, lambda: self.fetch_api_data(self))

    

def create_image_in_frame(window):
    global label
    frame = tk.Frame(window)
    image = Image.open("truck.png").resize(IMAGE_SIZE, Image.LANCZOS)
    image = ImageTk.PhotoImage(image)
    label = tk.Label(frame, image=image)
    label.image = image
    label.pack()
    frame.pack()

def create_lat_long_fields(window, api_data):
    label = tk.Label(window, text=f"Latitude: {api_data['lat']} | Longitude: {api_data['lng']}")
    label.pack()

def update_text_fields(window, api_data):
    # Update other text fields as needed
    pass

def handle_button_press(event):
    global label
    image = Image.open("car.png").resize(IMAGE_SIZE, Image.LANCZOS)
    image = ImageTk.PhotoImage(image)
    label.configure(image=image)
    label.image = image

def main():
    global api_data, label
    window = window_setup()
    fetch_api_data(window)
    create_image_in_frame(window)
    create_lat_long_fields(window, api_data)

    button = tk.Button(window, text=api_data['name'])
    button.bind("<Button-1>", handle_button_press)
    button.pack()

    # Start the event loop.
    window.mainloop()

if __name__ == "__main__":
    window = DadTracker()
    window.mainloop()

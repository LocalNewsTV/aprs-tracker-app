# aprs-tracker-app
APRS Tracker App is an unofficial companion application using the [APRS.FI](https://en.aprs.fi/) API. 

*Developed with Python 3.11 on Windows*

# Usage

The aprs-tracker-app is customizable. To start off, rename or duplicate the `user_information.template.json` file to `user_information.json`.

> Tkinter comes packaged with Windows versions of Python, additional installations may be required if using a different OS

1. get your API Key by creating an account at [APRS.fi](https://aprs.fi/account/).=
1. Optional You can add an api key from [Geoapify](https://www.geoapify.com/), this will convert your lat/long information to addresses
1. Install the python packages from requirements.txt
1. Fill out the `user_information.json` with your information
1. Run the application

## user_information.json
This file is customizable to allow for `n` entries, so you can track as many or as little callsigns / locations as needed. 

### Locations

```json
{
  "locations": {
    "your_key": {
      "label": "<Label>",
      "image": "FileName.png",
      "latitude": {
        "min": 0,
        "max": 0
      },
      "longitude": {
        "min": 0,
        "max": 0
      }
    },
  }
}
```

| Key | Description | Example |
| --- | --- | --- |
| your_key | Parent key for location object, you can name this anything | "Home" |
| label | "This is what is displayed in the application" | "at home" |
| image | filename of image you want to display when this activity is selected | "house.png" |
| latitude | Parent object of latitude min/max of fields you want to box your target in on. | N/A |
| min | Minimum Latitude range | 54.321 |
| max | Maximum Latitude range | 54.456 |
| longitude | Parent object of latitude min/max of fields you want to box your target in on.  | N/A |
| min | Minimum Longitude range | 54.321 |
| max | Maximum Longitude range | 54.456 |

### transport_method
APRS API Accepts targetting up to `20` Callsigns in one request, and so the same rule applies here

```json
  "transport_method": {
    "your_key": {
      "callsign": "<what you're tracking>",
      "image": "FileName.png"
    }
  },
```
| Key | Description | Example |
| --- | --- | --- |
| your_key | Parent key for transport object, you can name this anything | "Home" |
| callsign | This is the target you're tracking, you can get this from the information page. If you're tracking a boat you may need to use a MMSI Number value instead  | "V8V8V8" or "123456789" |
| image | filename of image you want associated with this vehicle. It will display if your vehicle is in transit, and not currently in the confines of a `locations` object | "car.png" |

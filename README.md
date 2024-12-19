
# GPX GeoCoding: A Simple Script for Reverse Geocoding


## Introduction

GPX_GeoCoding is a lightweight Python script that uses the Google Maps API to perform reverse geocoding on GPX files. It was created to help cyclists (like me!) identify the prefectures and cities they've traveled through based on their ride data.

## How it Works

The script takes a GPX file with timestamp information as input and outputs a JSON file containing the geocoded data. It's designed to work with most bicycle computer-generated GPX files.

### Requirements

-   Python 3
-   `gpxpy`  and  `googlemaps`  libraries (install using  `pip install -r requirements.txt`)
-   A valid Google Maps Platform API Key (sign up for one  [here](https://mapsplatform.google.com/))

## Getting Started

1.  Install the required dependencies:  `pip install -r requirements.txt`
2.  Get a Google Maps Platform API Key and replace the  `key`  variable in the  `main()`  function
3.  Update the  `gpx_file`  variable with the path to your GPX file
4.  Set the  `point_interval_minutes`  variable to control the time interval between each GPX point (e.g., analyze every 5 minutes)

Example configuration:

python

`gpx_file =  'path/to/your/gpx/file.gpx'  output_file = gpx_file +  '.geocoding.json'  gmaps = googlemaps.Client(key='YOUR_API_KEY_HERE')  point_interval_minutes =  5`

## Contributing

This script was created to solve a specific problem, but we'd love for you to contribute and make it better! If you have ideas or improvements, feel free to submit a pull request. We're always happy to collaborate and learn from each other.

import gpxpy
import logging
import googlemaps
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_gpx_file(file_path):
    """
    Load the GPX file from the specified path.
    
    Args:
        file_path (str): The path to the GPX file.
    
    Returns:
        gpxpy.gpx.GPX: The parsed GPX data.
    
    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If there is no permission to read the file.
        Exception: Any other exception during file loading or parsing.
    """
    try:
        with open(file_path, 'r') as f:
            return gpxpy.parse(f)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except PermissionError:
        logger.error(f"No permission to read file: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Failed to load GPX file: {e}")
        raise

def extract_points(gpx_data):
    """
    Extract all points from the GPX data and sort them by time.
    
    Args:
        gpx_data (gpxpy.gpx.GPX): The parsed GPX data.
    
    Returns:
        list: A list of sorted GPX points.
    
    Raises:
        Exception: Any exception during point extraction or sorting.
    """
    try:
        total_points = []
        for track in gpx_data.tracks:
            for segment in track.segments:
                total_points.extend(segment.points)
        return sorted(total_points, key=lambda x: x.time)
    except Exception as e:
        logger.error(f"Failed to extract points: {e}")
        raise

def select_points(points, interval_minutes):
    """
    Select points at the specified time interval.
    
    Args:
        points (list): A list of GPX points.
        interval_minutes (int): The time interval in minutes.
    
    Returns:
        list: A list of selected GPX points.
    
    Raises:
        Exception: Any exception during point selection.
    """
    try:
        if not points:
            logger.warning("No points to select from")
            return []
        
        processing_points = [points[0]]
        time_sec_passed = 0
        for i in range(1, len(points)):
            time_diff_seconds = (points[i].time - points[i-1].time).seconds
            time_sec_passed += time_diff_seconds
            if time_sec_passed >= interval_minutes * 60:
                time_sec_passed = 0
                processing_points.append(points[i])
        
        # Ensure the last point is included
        if len(processing_points) > 0 and (points[-1].time - processing_points[-1].time).seconds >= interval_minutes * 60:
            processing_points.append(points[-1])
        
        return processing_points
    except Exception as e:
        logger.error(f"Failed to select points: {e}")
        raise

def reverseGeocode(gmaps, points):
    """
    Reverse geocodes a list of GPX points using Google Maps API.

    Args:
       gmaps (googlemaps.Client): Google Maps client instance.
       points (list): List of GPX points to reverse geocode.
    """
    try:
        logger.info("Starting reverse geocoding...")
        parsed_points = []
        seen_addresses = set()  # Use a set to keep track of unique addresses
        for point in points:
            geocode_result = gmaps.reverse_geocode((point.latitude, point.longitude), language='ja',
                                                   result_type=['administrative_area_level_1', 'administrative_area_level_2', 'sublocality', 'sublocality_level_2',
                                                                'locality', 'administrative_area_level_3'])
            if geocode_result:
                newParsedAddr = {
                    'country': "",
                    'administrative_area_level_1': "",
                    'administrative_area_level_2': "",
                    'locality': "",
                    'sublocality': ""
                }
                for component in geocode_result[0]['address_components']:
                    if 'country' in component['types']:
                        newParsedAddr['country'] = component['long_name']
                    elif 'administrative_area_level_1' in component['types']:
                        newParsedAddr['administrative_area_level_1'] = component['long_name']
                    elif 'administrative_area_level_2' in component['types']:
                        newParsedAddr['administrative_area_level_2'] = component['long_name']
                    elif 'locality' in component['types']:
                        newParsedAddr['locality'] = component['long_name']
                    elif 'sublocality' in component['types']:
                        newParsedAddr['sublocality'] = component['long_name']

                # Convert the address dictionary to a tuple so it can be added to the set
                address_tuple = (
                    newParsedAddr['country'],
                    newParsedAddr['administrative_area_level_1'],
                    newParsedAddr['administrative_area_level_2'],
                    newParsedAddr['locality'],
                    newParsedAddr['sublocality']
                )

                # Check if the address has been seen before
                if address_tuple not in seen_addresses:
                    parsed_points.append(newParsedAddr)
                    seen_addresses.add(address_tuple)  # Add the address to the set
            else:
                logger.warning(f"No geocode result found for point: {point.latitude}, {point.longitude}")
        return parsed_points, len(parsed_points) == 0
    except Exception as e:
        logger.error(f"Failed to reverse geocode points: {e}")
        raise


def save_reversed_geocode_results_json(parsed_points, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            parsedJSON = json.dumps(parsed_points, indent=4, ensure_ascii=False)
            f.write(parsedJSON)

            logger.info(f"Successfully saved reversed geocode results to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save reversed geocode results: {e}")
            

def main():
    gpx_file = ''
    output_file = gpx_file + '.geocoding.json'
    gmaps = googlemaps.Client(key='')
    point_interval_minutes = 5
    try:
        gpx_data = load_gpx_file(gpx_file)
        total_points = extract_points(gpx_data)
        logger.info(f"Total Points: {len(total_points)}")
        
        processing_points = select_points(total_points, point_interval_minutes)
        logger.info(f"Total selected points: {len(processing_points)}")
        logger.info(f"Processing Points: {len(processing_points)}")
        reversed_geocode_results = reverseGeocode(gmaps, processing_points)
        save_reversed_geocode_results_json(reversed_geocode_results, output_file)
        logger.info("Reversed geocoding completed successfully.")
    except Exception as e:
        logger.error(f"Main function failed: {e}")

if __name__ == "__main__":
    main()

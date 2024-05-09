from datetime import datetime
import pytz

def convert_ist_to_utc(ist_time_str):
    # Define the format for the input string
    time_format = "%Y-%m-%d %H:%M"
    
    # Create a datetime object from the input string
    ist_time = datetime.strptime(ist_time_str, time_format)
    
    # Define the IST timezone
    ist_zone = pytz.timezone('Asia/Kolkata')
    
    # Localize the datetime object to IST
    localized_ist_time = ist_zone.localize(ist_time)
    
    # Convert the localized IST time to UTC
    utc_time = localized_ist_time.astimezone(pytz.utc)
    
    # Return the UTC time in the same format
    return utc_time.strftime(time_format)

# Example usage
ist_input = {"call_time": "2023-10-02 15:30"}
utc_time = convert_ist_to_utc(ist_input["call_time"])
print(f"UTC Time: {utc_time}")
import pytz

def convert_ist_to_utc(ist_datetime):
    # Define the IST timezone
    ist_zone = pytz.timezone('Asia/Kolkata')
    
    # Localize the datetime object to IST
    localized_ist_time = ist_zone.localize(ist_datetime)
    
    # Convert the localized IST time to UTC
    utc_time = localized_ist_time.astimezone(pytz.utc)
    
    return utc_time
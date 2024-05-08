from dotenv import load_dotenv
from retell import Retell
import os

load_dotenv(override=True)
retell = Retell(api_key=os.environ["RETELL_API_KEY"])

def make_call():
    try:
        call = retell.call.create(
            from_number="+14159936908",  # replace with the number you purchased
            to_number="+916350317505"    # replace with the number you want to call
        )
        print(f"Call initiated: {call}")
    except Exception as e:
        print(f"Failed to make call: {e}")
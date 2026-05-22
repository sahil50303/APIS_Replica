import json
import urllib.request
import urllib.error

def run_test():
    url = "http://127.0.0.1:8000/api/nssapi/ashram/InsertAnnounceCreation"
    
    # Headers using our custom API Key
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "NSS-LOCAL-TESTKEY-2026-XYZ"  # Default developer seed key
    }
    
    # Payload matching client structure
    payload = {
        "annoucePurposeList": [
            {
                "yojna_id": "9",
                "qty": "1",
                "amount": 5000.0,
                "bhojan_date": ""
            }
        ],
        "ashri": "MR.",
        "ashri_oth": "N.A.",
        "announcer_name": "hxxhchchchchc",
        "announce_amount": 5000.0,
        "address1": "hdchfhfhf",
        "address2": "hfhfuf",
        "address3": "",
        "ph_no": 0,
        "mob_no": "70734521314",
        "announce_through": "WHATSAPP",
        "announce_date": None,
        "announce_time": None,
        "std_code": 0,
        "email_id": "",
        "purpose": 0,
        "due_date": "06/11/2025",
        "due_time": "9:30 AM",
        "completed": 0,
        "remark1": "4",
        "first_remark": None,
        "second_remark": None,
        "third_remark": None,
        "city_code": None,
        "district_code": "1597.0",
        "state_code": "68.0",
        "remark2": "fhfhchc",
        "channel_code": 0,
        "pandit_code": 0,
        "bhag_city_code": 0,
        "user_name": "JATAN SINGH",
        "emp_code": 0,
        "live": "N",
        "ash_event_id": "0",
        "event_name": "",
        "user_id": "70",
        "cash_pickup": "N",
        "other_type": 0,
        "currency_id": "4.0",
        "cause_id": 0,
        "ngcode": "0",
        "data_flag": "GANGOTRI",
        "fy_id": "21",
        "dmobilewhatsapp1": "",
        "aadhar_number": "988989898986",
        "pan_number": "FHVJJ3456Q",
        "pincode_code": "76595.0",
        "country_code": "22",
        "pincode": "313001"
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    print("Sending POST request to localhost replication endpoint...")
    print(f"URL: {url}")
    print(f"X-API-Key: {headers['X-API-Key']}")
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            print("\n[SUCCESS] Server responded with status code 200.")
            print("Response Body:")
            print(json.dumps(json.loads(res_body), indent=4))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        print(f"\n[ERROR] HTTP Error {e.code}: {e.reason}")
        try:
            print("Error details:")
            print(json.dumps(json.loads(err_body), indent=4))
        except:
            print(err_body)
    except urllib.error.URLError as e:
        print(f"\n[CONNECTION ERROR] Could not connect to the server: {e.reason}")
        print("Is the FastAPI server running locally at http://127.0.0.1:8000?")

if __name__ == "__main__":
    run_test()

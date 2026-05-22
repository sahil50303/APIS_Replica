# main.py

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from supabase import create_client
from dotenv import load_dotenv
import os
import random

# ==========================================
# LOAD ENV
# ==========================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
API_KEY = os.getenv("API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

# ==========================================
# REQUIRED FIELDS
# ==========================================

REQUIRED_FIELDS = [
    "annoucePurposeList",
    "ashri",
    "ashri_oth",
    "announcer_name",
    "announce_amount",
    "address1",
    "address2",
    "address3",
    "ph_no",
    "mob_no",
    "announce_through",
    "announce_date",
    "announce_time",
    "std_code",
    "email_id",
    "purpose",
    "due_date",
    "due_time",
    "completed",
    "remark1",
    "first_remark",
    "second_remark",
    "third_remark",
    "city_code",
    "district_code",
    "state_code",
    "remark2",
    "channel_code",
    "pandit_code",
    "bhag_city_code",
    "user_name",
    "emp_code",
    "live",
    "ash_event_id",
    "event_name",
    "user_id",
    "cash_pickup",
    "other_type",
    "currency_id",
    "cause_id",
    "ngcode",
    "data_flag",
    "fy_id",
    "dmobilewhatsapp1",
    "aadhar_number",
    "pan_number",
    "pincode_code",
    "country_code",
    "pincode"
]

# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/")
def health():
    return {"status": "running"}

# ==========================================
# MAIN API
# ==========================================

@app.post("/api/nssapi/ashram/InsertAnnounceCreation")
def create_announcement(
    payload: dict,
    APIKey: str = Header(None)
):

    # ==========================================
    # API KEY CHECK
    # ==========================================

    if APIKey != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    # ==========================================
    # CHECK ALL REQUIRED FIELDS
    # ==========================================

    missing_fields = []

    for field in REQUIRED_FIELDS:
        if field not in payload:
            missing_fields.append(field)

    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Missing required fields",
                "missing_fields": missing_fields
            }
        )

    # ==========================================
    # MANDATORY VALUE CHECK
    # ==========================================

    if not payload.get("data_flag"):
        raise HTTPException(
            status_code=400,
            detail="data_flag is mandatory"
        )

    if not payload.get("mob_no"):
        raise HTTPException(
            status_code=400,
            detail="mob_no is mandatory"
        )

    # ==========================================
    # DUPLICATE MOBILE CHECK
    # ==========================================

    duplicate = (
        supabase.table("announcement_purposes")
        .select("id")
        .eq("mob_no", payload["mob_no"])
        .execute()
    )

    if duplicate.data:
        raise HTTPException(
            status_code=409,
            detail="Announcement already exists with this mobile number"
        )

    try:

        # ==========================================
        # EXTRACT FIRST PURPOSE ITEM
        # ==========================================

        purpose_list = payload.get("annoucePurposeList", [])

        first_purpose = {}

        if len(purpose_list) > 0:
            first_purpose = purpose_list[0]

        # ==========================================
        # GENERATE ANNOUNCE CODE
        # ==========================================

        announce_code = random.randint(100000, 999999)

        # ==========================================
        # INSERT INTO EXISTING TABLE
        # ==========================================

        insert_data = {
            "announcement_id": announce_code,
            "yojna_id": first_purpose.get("yojna_id"),
            "qty": first_purpose.get("qty"),
            "amount": first_purpose.get("amount"),
            "bhojan_date": first_purpose.get("bhojan_date"),
            "raw_aannounce_json": payload,
            "mob_no": payload.get("mob_no")
        }

        (
            supabase.table("announcement_purposes")
            .insert(insert_data)
            .execute()
        )

        # ==========================================
        # SUCCESS RESPONSE
        # ==========================================

        return JSONResponse(
            status_code=201,
            content={
                "masterDetails": [
                    {
                        "code": announce_code,
                        "msg": f"Announce Id:{announce_code} created Successfully",
                        "status": "success"
                    }
                ]
            }
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

import argparse
import pandas as pd
import requests
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import FileResponse
from io import BytesIO

app = FastAPI()

def get_access_token():
    url = "https://api.baubuddy.de/index.php/login"
    payload = {
        "username": "365",
        "password": "1"
    }
    headers = {
        "Authorization": "Basic QVBJX0V4cGxvcmVyOjEyMzQ1NmlzQUxhbWVQYXNz",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    datas = response.json()
    access_token = datas["oauth"]["access_token"]
    return access_token

def download_data(access_token, keys, colored):
    url = "https://api.baubuddy.de/dev/index.php/v1/vehicles/select/active"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    vehicle_data = response.json()

    # Filter out resources without hu field
    filtered_data = [item for item in vehicle_data if item.get("hu")]

    # If labelIds are given, resolve colorCodes
    if "labelIds" in keys:
        label_ids = set()
        for item in filtered_data:
            if "labelIds" in item:
                label_ids.update(item["labelIds"])
        color_codes = {}
        for label_id in label_ids:
            label_url = f"https://api.baubuddy.de/dev/index.php/v1/labels/{label_id}"
            label_response = requests.get(label_url, headers=headers)
            color_codes[label_id] = label_response.json().get("colorCode")

        for item in filtered_data:
            if "labelIds" in item:
                item["labelColors"] = [color_codes.get(label_id) for label_id in item["labelIds"]]

    df = pd.DataFrame(filtered_data)
    
    if keys:
        for key in keys:
            if key != "labelIds":
                df[key] = df[key]

    if colored:
        df["hu"] = pd.to_datetime(df["hu"])
        current_date = datetime.now()
        df["color"] = ""
        for index, row in df.iterrows():
            delta = current_date - row["hu"]
            if delta.days <= 90:
                df.at[index, "color"] = "#007500"  # Green
            elif delta.days <= 365:
                df.at[index, "color"] = "#FFA500"  # Orange
            else:
                df.at[index, "color"] = "#b30000"  # Red

    df = df.sort_values(by=["gruppe"])
    df = df[['rnr'] + keys + ['color']]

    return df

@app.post("/generate_excel")
async def generate_excel(keys: list, colored: bool = True):
    access_token = get_access_token()
    df = download_data(access_token, keys, colored)

    current_date_iso_formatted = datetime.now().isoformat()
    file_name = f"vehicles_{current_date_iso_formatted}.xlsx"
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name="Vehicles", index=False)
    output.seek(0)
    
    return FileResponse(output, headers={"Content-Disposition": f"attachment; filename={file_name}"})

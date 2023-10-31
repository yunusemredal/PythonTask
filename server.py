from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import List
import requests
import json
import pandas as pd

app = FastAPI()

@app.post("/upload_csv/")
async def upload_csv(file: UploadFile = File(...), keys: List[str] = Form(...), colored: bool = Form(True)):
    file_content = await file.read()
    with open("uploaded.csv", "wb") as f:
        f.write(file_content)
    
    uploaded_df = pd.read_csv("vehciles.csv")

    client_api_url = "http://localhost:8000/generate_excel"
    data = {"keys": keys, "colored": colored}
    response = requests.post(client_api_url, json=data)
    excel_file = response.content

    return {"status": "success", "message": "Excel file generated successfully", "file": excel_file}

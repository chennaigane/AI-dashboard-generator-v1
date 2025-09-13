from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
from io import BytesIO
from app.services.insights import generate_dashboard_spec_and_insights

router = APIRouter()

@router.post("/upload")
async def upload_and_analyze(file: UploadFile = File(...)):
    try:
        content = await file.read()
        name = file.filename or "uploaded_file"
        if name.lower().endswith(".csv"):
            df = pd.read_csv(BytesIO(content))
        elif name.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(BytesIO(content))
        else:
            return {"error": "Unsupported file type. Please upload CSV or Excel."}

        # Limit preview to avoid huge payloads
        preview = df.head(5).to_dict(orient="records")

        # Generate dashboard spec & insights
        result = generate_dashboard_spec_and_insights(df)

        return {
            "filename": name,
            "rows": len(df),
            "columns": list(df.columns),
            "preview": preview,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

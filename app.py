from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import boto3

app = FastAPI(title="FastAPI S3 Upload")

s3 = boto3.client("s3")

BUCKET_NAME = "mi-bucket-fastapi-final"

ALLOWED_TYPES = ["image/png", "image/jpeg"]

@app.post("/upload")
async def upload_image(username: str, file: UploadFile = File(...)):

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Formato inválido. Solo PNG y JPG/JPEG."
        )

    key = f"{username}/{file.filename}"

    s3.upload_fileobj(file.file, BUCKET_NAME, key)

    return {
        "message": "Imagen subida correctamente",
        "user": username,
        "file": file.filename
    }

@app.get("/image")
def get_image(username: str, filename: str):

    key = f"{username}/{filename}"

    try:

        response = s3.head_object(
            Bucket=BUCKET_NAME,
            Key=key
        )

        url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": key
            },
            ExpiresIn=3600
        )

        return {
            "message": "Imagen encontrada",
            "url": url,
            "uploaded_at": str(response["LastModified"])
        }

    except Exception:

        return JSONResponse(
            status_code=404,
            content={
                "message": "Usuario o imagen no encontrados"
            }
        )
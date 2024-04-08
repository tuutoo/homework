from mangum import Mangum
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
import io
from ultralytics import YOLO
import uuid
import math
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = YOLO('blackboard_best.pt')
model.info()

@app.get("/")
def read_root():
    return {"message": "Hello, World"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))
    results = model.predict(image)
    predictions = format_predictions(results)
    return JSONResponse(content={"predictions": predictions})

def format_predictions(results):
    predictions = []
    for result in results:
        boxes = result.boxes
        if boxes.data is not None and len(boxes.data) > 0:
            sorted_boxes = sorted(boxes.data, key=lambda x: x[4], reverse=True)  # Sort by confidence in descending order
            x1, y1, x2, y2, conf, cls = sorted_boxes[0]  # Only take the one with the highest confidence
            predictions.append({
                "x": round(x1.item(), 1),
                "y": round(y1.item(), 1),
                "width": math.ceil((x2 - x1).item()),
                "height": math.ceil((y2 - y1).item()),
                "confidence": round(conf.item(), 3),
                "class": result.names[int(cls.item())],
                "class_id": int(cls.item()),
                "detection_id": str(uuid.uuid4())
            })
    # If predictions is empty, i.e., no results were detected, or if only the result with the highest confidence is requested
    if predictions:
        return predictions[0]  # Only return the one with the highest confidence
    else:
        return None  # If no results were detected, return None

@app.post("/invert/")
async def invert_image(file: UploadFile = File(...), ai: Optional[str] = Form(None)):
    file_ext = file.filename.split(".")[-1]
    supported_formats = ["jpeg", "jpg", "png"]
    ai_bool = ai.lower() == 'true' if ai else False  # Convert ai parameter to boolean

    if file_ext.lower() not in supported_formats:
        return {"error": "Unsupported file format, only jpg and png are supported."}

    if ai_bool:  # If the ai parameter is true
        # First, perform blackboard detection
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        results = model.predict(image)
        prediction = format_predictions(results)  # Now expecting to get a dictionary, not a list of dictionaries

        if prediction is not None and prediction["class"].lower() == "blackboard":
            # Crop the blackboard area
            x = prediction["x"]
            y = prediction["y"]
            width = prediction["width"]
            height = prediction["height"]
            blackboard_region = image.crop((x, y, x + width, y + height))
        else:
            # If no blackboard is found, use the entire image
            blackboard_region = image

    else:
        # If the ai parameter is false, use the entire image
        image_bytes = await file.read()
        blackboard_region = Image.open(io.BytesIO(image_bytes))

    # Perform inversion on the selected area or the entire image
    image_array = np.array(blackboard_region)
    inverted_image_array = 255 - image_array
    inverted_image = Image.fromarray(np.uint8(inverted_image_array))

    byte_io = io.BytesIO()
    file_ext = "JPEG" if file_ext.lower() == "jpg" else file_ext.upper()
    inverted_image.save(byte_io, file_ext)
    byte_io.seek(0)

    return StreamingResponse(byte_io, media_type=f"image/{file_ext}", headers={"Content-Disposition": f"attachment; filename=inverted_image.{file_ext}"})

handler = Mangum(app)

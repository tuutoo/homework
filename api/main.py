from mangum import Mangum
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from PIL import Image
import numpy as np
import io

from ultralytics import YOLO
import uuid
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 假设你的YOLOv9模型加载方式
# 请根据实际情况替换成适合你的模型的代码
model = YOLO('blackboard_best.pt')

# Display model information (optional)
model.info()

@app.get("/")
def read_root():
    return {"message": "Hello, World"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    # 将上传的文件读取为字节
    image_bytes = await file.read()

    # 使用PIL读取图片
    image = Image.open(io.BytesIO(image_bytes))

    # # 确保图片是RGB格式
    # if image.mode != 'RGB':
    #     image = image.convert('RGB')

    # 使用模型进行预测
    results = model.predict(image)

    # 打印results的结构来查看
    print(results[0].boxes)

    # 将结果处理为可以序列化的格式
    predictions = format_predictions(results)

    return JSONResponse(content={"predictions": predictions})

    # 根据results的实际结构进行处理...
def format_predictions(results):
    predictions = []
    # 假设results是一个列表，其中每个元素代表一张图片的预测结果
    for result in results:
        # 访问每个结果的boxes属性
        boxes = result.boxes
        # 检查是否有检测到的对象
        if boxes.data is not None and len(boxes.data) > 0:
            for i in range(len(boxes.data)):
                x1, y1, x2, y2, conf, cls = boxes.data[i]
                predictions.append({
                    "x": round(x1.item(), 1),  # 保留一位小数
                    "y": round(y1.item(), 1),  # 保留一位小数
                    "width": math.ceil((x2 - x1).item()),  # 向上取整
                    "height": math.ceil((y2 - y1).item()),  # 向上取整
                    "confidence": round(conf.item(), 3),  # 保留三位小数
                    "class": result.names[int(cls.item())],  # 使用索引从names中获取类名
                    "class_id": int(cls.item()),
                    "detection_id": str(uuid.uuid4())
                })
    return predictions

@app.post("/invert/")
async def invert_image(file: UploadFile = File(...)):
    file_ext = file.filename.split(".")[-1]  # 获取文件扩展名
    supported_formats = ["jpeg", "jpg", "png"]

    if file_ext.lower() not in supported_formats:
        return {"error": "Unsupported file format, only jpg and png are supportted."}

    # 使用 PIL 打开图片
    image = Image.open(io.BytesIO(await file.read()))

    # 将图片转换为 NumPy 数组
    image_array = np.array(image)

    # 执行反色操作
    inverted_image_array = 255 - image_array

    # 将 NumPy 数组转回为 PIL 图片
    inverted_image = Image.fromarray(np.uint8(inverted_image_array))

    # 保存到一个字节流中，以便可以直接返回
    byte_io = io.BytesIO()

    file_ext = file_ext.upper()
    if file_ext == "JPG":
        file_ext = "JPEG"
    inverted_image.save(byte_io, file_ext)

    byte_io.seek(0)

    return StreamingResponse(byte_io, media_type=f"image/{file_ext}", headers={"Content-Disposition": f"attachment; filename=inverted_image.{file_ext}"})

handler = Mangum(app)

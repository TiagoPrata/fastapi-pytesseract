from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from ocr_module import OCRDetector

app = FastAPI()
hd = OCRDetector()


@app.get("/")
async def root():
    return {"message": "Hello World"}


class InputImg(BaseModel):
    img_base64str : str


@app.post("/process_ocr/")
def find_hands(d:InputImg, confLevel: int = 75):
    hd.process_ocr(d.img_base64str, confLevel)
    return hd.processed_img()


@app.post("/get_img_and_texts/")
def get_angle_img_and_value(d:InputImg, confLevel: int = 75):
    hd.process_ocr(d.img_base64str, confLevel)

    ret = {'img': hd.processed_img(), 'texts': hd.texts}
    
    return ret


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
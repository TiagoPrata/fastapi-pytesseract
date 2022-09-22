import base64
import io
from PIL import Image
import pytesseract
import cv2
import numpy as np


def base64str_to_PILImage(base64str):
    """Convert a Base64 Image to a Pillow Image

    Args:
        base64str (str): Image in Base64 string

    Returns:
        Image: Pillow image (https://pillow.readthedocs.io/en/stable/reference/Image.html)
    """

    base64_img_bytes = base64str.encode('utf-8')
    base64bytes = base64.b64decode(base64_img_bytes)
    bytesObj = io.BytesIO(base64bytes)
    img = Image.open(bytesObj)
    return img


def PILImage_to_base64str(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())

    return img_str.decode()


def base64img_to_np_array(image: str):
    pillow_img = base64str_to_PILImage(image)
    return np.array(pillow_img)


def np_array_to_base64img(image):
    pillow_img = Image.fromarray(image)
    return PILImage_to_base64str(pillow_img)

def PILImage_to_np_array(image):
    # im is a PIL Image object
    im_arr = np.asarray(image)
    # convert rgb array to opencv's bgr format
    im_arr_bgr = cv2.cvtColor(im_arr, cv2.COLOR_RGB2BGR)
    return im_arr_bgr

def np_array_to_PILImage(image):
    # img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    im_pil = Image.fromarray(image)
    return im_pil

class OCRLine:
    def __init__(self, level, page_num, block_num, par_num, line_num, word_num, left, top, width, height, conf, text):
        self.level = level
        self.page_num = page_num
        self.block_num = block_num
        self.par_num = par_num
        self.line_num = line_num
        self.word_num = word_num
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.conf = conf
        self.text = text

class OCRDataParser:
    def __init__(self):
        self.ocr_lines = []

    def parse(self, text: str, first_line_is_header: bool = True):
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if i == 0 and first_line_is_header: continue
            data = line.split('\t')
            if len(data) == 12:
                level = data[0]
                page_num = data[1]
                block_num = data[2]
                par_num = data[3]
                line_num = data[4]
                word_num = data[5]
                left = data[6]
                top = data[7]
                width = data[8]
                height = data[9]
                conf = data[10]
                text = data[11]
                text = text.strip()
                
                if text != '':
                    ocr_line = OCRLine(level, page_num, block_num, par_num, line_num, word_num, left, top, width, height, conf, text)
                    self.ocr_lines.append(ocr_line)

    def get_coordenates_and_texts(self):
        items_list = []
        
        for line in self.ocr_lines:
            start_point = (int(line.left), int(line.top))
            end_point = (int(line.left) + int(line.width), int(line.top) + int(line.height))
            items_list.append((start_point, end_point, int(line.conf), line.text))

        return items_list


class OCRDetector:
    def __init__(self):
        pass

    def putText(self, text: str, location, fontScale = 3, color = (255,0,0), thickness = 3):
        cv2.putText(self.img, text, location, cv2.FONT_HERSHEY_COMPLEX, fontScale, color, thickness)


    def processed_img(self):
        return PILImage_to_base64str(self.img)


    def process_ocr(self, img_base64: str, confLevel: int):
        ocr_parser = OCRDataParser()
        self.texts = ""
                
        self.img = base64str_to_PILImage(img_base64)
        open_cv_img = base64img_to_np_array(img_base64)
        # print(pytesseract.image_to_string(self.img))
        # print(pytesseract.image_to_data(self.img))
        ocr_parser.parse(pytesseract.image_to_data(self.img))
        # print(ocr_parser.get_coordenates_and_texts())
        for item in ocr_parser.get_coordenates_and_texts():
            start_point = item[0]
            end_point = item[1]
            conf = item[2]
            text = item[3]

            if conf >= confLevel:
                cv2.rectangle(open_cv_img, start_point, end_point, (255,0,0), 3)
                self.texts = ''.join([self.texts, "|", text])

        self.img = np_array_to_PILImage(open_cv_img)
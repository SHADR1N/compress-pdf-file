from fpdf import FPDF
from PIL import Image
from compressIMG import compressing_img
import fitz
import json
from pathlib import Path
import os 
from time import sleep

# pip install PyMuPDF
# pip install fpdf


with open('compression_parameters.json') as f:
    parameters = json.load(f)


if not os.path.exists(path = parameters["input_folder"]):
    os.mkdir(path = parameters["input_folder"])

if not os.path.exists(path = parameters["output_folder"]):
    os.mkdir(path = parameters["output_folder"])


doc = fitz.open(parameters["input_pdf"])
for i in range(len(doc)):
    for img in doc.getPageImageList(i):
        xref = img[0]
        pix = fitz.Pixmap(doc, xref)
        if pix.n < 5:       # this is GRAY or RGB
            pix.writePNG("%s/sss%s.jpg" % (parameters["input_folder"], i))
        else:               # CMYK: convert to RGB first
            pix1 = fitz.Pixmap(fitz.csRGB, pix)
            pix1.writePNG("%s/sss%s.jpg" % (parameters["input_folder"], i))
            pix1 = None
        pix = None


""" Run compressing image """
compressing_img()

""" Create new PDF file """
imagelist = os.listdir(path = parameters["output_folder"])

pdf = FPDF()
for image in imagelist:
    """ Image path """
    image = parameters["output_folder"] + '/' + image

    """ Get size image """
    im = Image.open(image)
    width, height = im.size

    pdf.add_page()
    pdf.image(image, h=int(255))

pdf.output(parameters["output_pdf"], "F")



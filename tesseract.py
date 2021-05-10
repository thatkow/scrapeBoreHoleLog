# Import libraries
from PIL import Image
import pytesseract
import sys
from pdf2image import convert_from_path
import os
import subprocess
import time
import re
import pdf2image
import tabula
from PyPDF2 import PdfFileWriter, PdfFileReader
import json
import PyPDF2

selectIdx = (110, 188, 388, 971)
dim = (826, 1169)

PDF_file = "example.pdf"
'''
Part #1 : Converting PDF to images
'''

pdf = PyPDF2.PdfFileReader(PDF_file)
image_counter = 1


def cropAndParse(im, filepath, yLow, yHigh):
    crp = im.crop((0, yLow, im.size[0], yHigh))
    filepath_with_ext = filepath+".jpeg"
    crp.save(filepath_with_ext, 'JPEG')
    text = str((pytesseract.image_to_string(crp)))
    finalText = ""
    for t in re.split("\n\n+", text.replace("\x0c", "").strip()):
        finalText += t.replace("\n", " ") + "\n\n"
    return finalText.strip()

workingRoot = PDF_file+".parts."+time.strftime("%Y%m%d-%H%M%S")
os.mkdir(workingRoot)


for pageIdx in range(0, pdf.getNumPages()):

    descriptions = []
    ladderValues = []

    pdfPage = pdf.getPage(pageIdx)
    pdfPage.scaleBy(4)  # float representing scale factor - this happens in-place
    writer = PyPDF2.PdfFileWriter()  # create a writer to save the updated results
    writer.addPage(pdfPage)
    tempPdf = workingRoot + os.path.sep + "scaledPdf.pdf"
    with open(tempPdf, "wb+") as f:
        writer.write(f)
    page = convert_from_path(tempPdf)[0]

    print("Processing page: " + str(image_counter))
    cropIdx = (selectIdx[0]/dim[0] * page.size[0], selectIdx[1]/dim[1] * page.size[1], selectIdx[2]/dim[0] * page.size[0], selectIdx[3]/dim[1] * page.size[1])
    prefix = "page_" + str(image_counter)

    cropped = page.crop((cropIdx[0]+1, cropIdx[1], cropIdx[2], cropIdx[3]))
    pageRoot = workingRoot + os.path.sep + prefix
    os.mkdir(pageRoot)
    filename = prefix + ".jpg"
    cropped.save(pageRoot + os.path.sep + filename, 'JPEG')

    verticalIntensity = list(range(0, cropped.size[1]))
    for r in verticalIntensity:
        blackPointMax = 0
        blackPointCount = 0
        for c in range(0, cropped.size[0]):
            rgb = cropped.getpixel((c, r))
            intensity = rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722
            if intensity < 100:
                blackPointCount += 1
        verticalIntensity[r] = blackPointCount

    verticalIntensityIdx = [i for i in range(0, len(verticalIntensity)) if verticalIntensity[i] > cropped.size[0] * 0.65]
    if len(verticalIntensityIdx) > 0:
        verticalIntensityIdx = [verticalIntensityIdx[0]] + [verticalIntensityIdx[i] for i in
                                                            range(1, len(verticalIntensityIdx)) if
                                                            verticalIntensityIdx[i] - verticalIntensityIdx[i - 1] > 1]
        descriptions += [cropAndParse(cropped, pageRoot + os.path.sep + prefix + "_part_" + str(0),
                     0, verticalIntensityIdx[0])]  # First
        for vidx in range(1, len(verticalIntensityIdx)):
            descriptions += [cropAndParse(cropped, pageRoot + os.path.sep + prefix + "_part_" + str(vidx),
                         verticalIntensityIdx[vidx-1], verticalIntensityIdx[vidx])]  # Last
        descriptions += [cropAndParse(cropped,pageRoot + os.path.sep + prefix + "_part_" + str(len(verticalIntensityIdx)-1), verticalIntensityIdx[len(verticalIntensityIdx) - 1], cropped.size[1])] # Last
    imLadder = page.crop((cropIdx[0]-200, cropIdx[1], cropIdx[0]-1, cropIdx[3]))
    imLadder.save(pageRoot + os.path.sep + prefix + "_ladder" + ".jpg")
    parse = str((pytesseract.image_to_string(imLadder)))
    ladderValues += [float(i) for i in list(filter(None, re.sub("[^0-9\\n\\.]", "", parse).splitlines()))]
    print(str(len(ladderValues))+", "+str(len(descriptions)))
    print(ladderValues)
    print(descriptions)
    image_counter = image_counter + 1



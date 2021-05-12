import sys

import pytesseract
from pdf2image import convert_from_path
import os
import time
import re
import PyPDF2
import csv
import argparse

parser = argparse.ArgumentParser(description='Scrape borehole depth and descriptions')
parser.add_argument('--pdfFile',  type=str, help='Borehole PDF', required=True)
parser.add_argument('--pageSets',  type=str,  help='Example: 1-3,4-6,7-9', required=True)
parser.add_argument('--ladderLeft',  type=int,  help='Left position of ladder (px, required=True)', required=True)
parser.add_argument('--ladderRight',  type=int,  help='Right position of ladder (px, required=True)', required=True)
parser.add_argument('--ladderTop',  type=int,  help='Top position of ladder (px, required=True)', required=True)
parser.add_argument('--ladderBottom',  type=int,  help='Bottom position of ladder (px, required=True)', required=True)
parser.add_argument('--descriptionLeft',  type=int,  help='Left position of description (px, required=True)', required=True)
parser.add_argument('--descriptionRight',  type=int,  help='Right position of description (px, required=True)', required=True)
parser.add_argument('--descriptionTop',  type=int,  help='Top position of description (px, required=True)', required=True)
parser.add_argument('--descriptionBottom',  type=int,  help='Bottom position of description (px, required=True)', required=True)
parser.add_argument('--width',  type=int,  help='Height of pdf page (px, required=True)', required=True)
parser.add_argument('--height',  type=int,  help='Width of pdf page (px)')

args = parser.parse_args()
descriptionBox = (args.descriptionLeft, args.descriptionTop, args.descriptionRight, args.descriptionBottom)
ladderBox = (args.ladderLeft, args.ladderTop, args.ladderRight, args.ladderBottom)
dim = (args.width, args.height)
pageSets = args.pageSets
PDF_file = args.pdfFile

# # For debugging in pycharm
# descriptionBox = (111, 189, 388, 971)
# ladderBox = (90, 189, 109, 971)
# dim = (826, 1169)
# pageSets = "7-9"
# PDF_file = "exampleEdit.pdf"

pdf = PyPDF2.PdfFileReader(PDF_file)
def cropAndParse(im, filepath, yLow, yHigh):
    crp = im.crop((0, yLow, im.size[0], yHigh))
    filepath_with_ext = filepath+".jpeg"
    crp.save(filepath_with_ext, 'JPEG')
    text = str((pytesseract.image_to_string(crp)))
    finalText = ""
    for t in re.split("\n\n+", text.replace("\x0c", "").strip()):
        finalText += t.replace("\n", " ") + "\n\n"
    return finalText.strip()


execRoot = "borehole_parser_"+PDF_file+".parts."+time.strftime("%Y%m%d-%H%M%S")
os.mkdir(execRoot)

for pageSet in pageSets.split(","):
    firstPage = int(pageSet.split("-")[0]) - 1
    lastPage = int(pageSet.split("-")[1]) - 1

    workingRoot = execRoot + os.path.sep + "pageSet"+pageSet
    os.mkdir(workingRoot)
    descriptions = []
    ladderValues = [0.0]
    for pageIdx in range(firstPage, lastPage):
        prefix = "page_" + str(pageIdx + 1)
        pageRoot = workingRoot + os.path.sep + prefix
        os.mkdir(pageRoot)

        pdfPage = pdf.getPage(pageIdx)
        pdfPage.scaleBy(4)  # float representing scale factor - this happens in-place
        writer = PyPDF2.PdfFileWriter()  # create a writer to save the updated results
        writer.addPage(pdfPage)
        tempPdf = pageRoot + os.path.sep + "scaledPdf.pdf"
        with open(tempPdf, "wb+") as f:
            writer.write(f)
        page = convert_from_path(tempPdf)[0]


        cropIdx = (descriptionBox[0]/dim[0] * page.size[0], descriptionBox[1]/dim[1] * page.size[1], descriptionBox[2]/dim[0] * page.size[0], descriptionBox[3]/dim[1] * page.size[1])


        cropped = page.crop((cropIdx[0]+1, cropIdx[1], cropIdx[2], cropIdx[3]))

        filename = prefix + "_descriptions.jpg"
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
            firstDescriptionOnPage = cropAndParse(cropped, pageRoot + os.path.sep + prefix + "_part_" + str(0),
                         0, verticalIntensityIdx[0])
            if pageIdx != firstPage:
                descriptions[len(descriptions)-1] += firstDescriptionOnPage  # Spillover from previous page
            else:
                descriptions += [firstDescriptionOnPage]  # First
            for vidx in range(1, len(verticalIntensityIdx)):
                descriptions += [cropAndParse(
                                    cropped,
                                    pageRoot + os.path.sep + prefix + "_part_" + str(vidx),
                                    verticalIntensityIdx[vidx-1],
                                    verticalIntensityIdx[vidx])]  # Last
            descriptions += [cropAndParse(cropped,pageRoot + os.path.sep + prefix + "_part_" + str(len(verticalIntensityIdx)-1), verticalIntensityIdx[len(verticalIntensityIdx) - 1], cropped.size[1])] # Last
        print("Processed page: " + str(pageIdx + 1))
        cropIdx = (ladderBox[0]/dim[0] * page.size[0], ladderBox[1]/dim[1] * page.size[1],
                   ladderBox[2]/dim[0] * page.size[0], ladderBox[3]/dim[1] * page.size[1])
        imLadder = page.crop((cropIdx[0], cropIdx[1], cropIdx[2], cropIdx[3]))
        imLadder.save(pageRoot + os.path.sep + prefix + "_ladder" + ".jpg")
        parse = str((pytesseract.image_to_string(imLadder)))
        nextLadder = [float(i) for i in list(filter(None, re.sub("[^0-9\\n\\.]", "", parse).splitlines()))]
        ladderValues += nextLadder
    newFile = os.path.splitext(PDF_file)[0] + pageSet + '.csv'
    with open(newFile, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Depth", "Description"])
        for i in range(0, max(len(ladderValues), len(descriptions))):
            ld = ""
            dsc = ""
            if i < len(ladderValues):
                ld = ladderValues[i]
            if i < len(descriptions):
                dsc = descriptions[i]
            writer.writerow([ld, dsc])
    if len(ladderValues) != len(descriptions):
        sys.stderr.write("Mismatch between scraped ladder values (" + str(len(ladderValues)) + ") "
                                           "and strata descriptions (" + str(
            len(descriptions)) + ") for file : " + newFile)
    else:
        print("Created file:\n"+os.path.abspath(newFile))



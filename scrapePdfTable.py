import tabula
import re # String replacement
import argparse

# Taken from https://stackoverflow.com/a/39120610
parser = argparse.ArgumentParser(description='Parse pdf table data')
parser.add_argument('inputfile', action='store', type=str, help='The input pdf file to scrape.')

args = parser.parse_args() # Parse arguments
print("Reading file "+args.inputfile)
df = tabula.read_pdf(args.inputfile,pages=1,output_format="json")
depthRaw = df[0]['data'][2][1]['text'].split('\r')
depthRawRemoveRulerRegex = re.compile('^\d+$')
depths = list(map(float,[x for x in depthRaw if not depthRawRemoveRulerRegex.match(x)]))

descriptionsRaw = [df[0]['data'][i][0]['text'] for i in list(range(0,len(df[0]['data'])))]
print("Converted to "+outputfile)


cropIdx = (224,376,767,1941)

from PyPDF2 import PdfFileWriter, PdfFileReader
in_f="example.pdf"
input1 = PdfFileReader(in_f)
output = PdfFileWriter()
i=0
page = input1.getPage(i)
pageRect = page.cropBox
page.cropBox.lowerLeft = (cropIdx[0]/im.size[0]*float(pageRect[2]),float(pageRect[3])  * (1 - cropIdx[3]/im.size[1]))
page.cropBox.upperRight = (cropIdx[2]/im.size[0]*float(pageRect[2]),float(pageRect[3])  * (1 - cropIdx[1]/im.size[1]))
output.addPage(page)
with open("out.pdf", "wb") as out_f:
    output.write(out_f)
    



import pdf2image
from PIL import Image, ImageDraw

images = pdf2image.convert_from_path('example.pdf')
im = images[0]
draw = ImageDraw.Draw(im)
cropped = img.crop((224,376,767,1941))


verticalIntensity = list(range(0,cropped.size[1]))
for r in verticalIntensity:
    blackPointMax = 0
    blackPointCount = 0
    for c in range(0,cropped.size[0]):
        rgb = cropped.getpixel((c,r))
        intensity = rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722
        if intensity < 100 :
            blackPointCount += 1
    verticalIntensity[r] = blackPointCount

verticalIntensityIdx = [i for i in range(0,len(verticalIntensity)) if verticalIntensity[i] > cropped.size[0] * 0.5]
verticalIntensityIdx = [verticalIntensityIdx[0]]+[verticalIntensityIdx[i] for i in range(1,len(verticalIntensityIdx)) if verticalIntensityIdx[i] -  verticalIntensityIdx[i-1] > 1]
verticalIntensityIdx

cropped.save('out.jpeg',"JPEG")



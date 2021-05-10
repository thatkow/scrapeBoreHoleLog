import subprocess
import re
import pdf2image
import tabula
from PyPDF2 import PdfFileWriter, PdfFileReader
import json

images = pdf2image.convert_from_path('example.pdf')
i = 0

im = images[i]

cropIdx = (224,376,767,1941)
in_f = "example.pdf"
input1 = PdfFileReader(in_f)
output = PdfFileWriter()
page = input1.getPage(i)
pageRect = page.cropBox
page.cropBox.lowerLeft = ( cropIdx[0] / im.size[0] * float(pageRect[2]), float(pageRect[3]) * (1 - cropIdx[3] / im.size[1]))
page.cropBox.upperRight = ( cropIdx[2] / im.size[0] * float(pageRect[2]), float(pageRect[3]) * (1 - cropIdx[1] / im.size[1]))
output.addPage(page)
outputfilepath = "out.pdf"
with open(outputfilepath, "wb") as out_f:
    output.write(out_f)
bashCmd = ["firefox", outputfilepath]
subprocess.Popen(bashCmd, stdout=subprocess.PIPE)

df = tabula.read_pdf(outputfilepath, pages=1, output_format="json")

with open('data.json', 'w') as f:
    json.dump(df, f)
subprocess.Popen(["firefox", 'data.json'], stdout=subprocess.PIPE)

depthRaw = df[0]['data'][2][1]['text'].split('\r')
depthRawRemoveRulerRegex = re.compile('^\d+$')
depths = list(map(float, [x for x in depthRaw if not depthRawRemoveRulerRegex.match(x)]))

descriptionsRaw = [df[0]['data'][i][0]['text'] for i in list(range(0, len(df[0]['data'])))]

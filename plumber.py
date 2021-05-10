import pdfplumber
with pdfplumber.open(r'/tmp/mozilla_andrew0/pdfresizer.com-pdf-crop.pdf') as pdf:
    first_page = pdf.pages[0]
    print(first_page.extract_text())
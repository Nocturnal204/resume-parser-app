import re
import nltk
import spacy
from spacy.matcher import Matcher
import pandas as pd
from nltk.corpus import stopwords
from resume_parser.settings import MEDIA_URL_SKILLS
import docx2txt
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger, PdfReader
# load pre-trained model
nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)
nltk.download('stopwords')
stop = stopwords.words('english')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
# Grad all general stop words
STOPWORDS = set(stopwords.words('english'))
# Education Degrees
EDUCATION = [
    'S.S.C', 'SSC', 's.s.c', 'ssc', 'H.S.C', 'HSC', 'h.s.c', 'hsc', 'B.A', 'BA', 'b.a', 'ba', 'M.A', 'MA', 'm.a', 'ma', 'B.COM', 'Bcom', 'b.com', 'bcom', 'M.COM', 'Mcom', 'm.com', 'mcom',
    'B.TECH', 'Btech', 'b.tech', 'btech', 'M.TECH', 'Mtech', 'm.tech', 'mtech', 'B.E', 'BE', 'b.e', 'be', 'M.E', 'ME', 'm.e', 'me',
    'B.B.A', 'BBA', 'b.b.a', 'bba', 'M.B.A', 'MBA', 'm.b.a', 'mba', 'B.C.A', 'BCA', 'b.c.a', 'bca', 'M.C.A', 'MCA', 'm.c.a', 'mca',
    'B.ARCH', 'BARCH', 'b.arch', 'barch', 'M.ARCH', 'B.DES', 'BDES', 'b.des', 'bdes', 'M.DES', 'MDES', 'm.des', 'mdes',
    'B.PHARM', 'BPHARM', 'b.pharm', 'bpharm', 'M.PHARM', 'MPHARM', 'm.pharm', 'mpharm', 'B.SC', 'BSC', 'b.sc', 'bsc', 'M.SC', 'MSC', 'm.sc', 'msc',
    'B.ED', 'BED', 'b.ed', 'bed', 'M.ED', 'MED', 'm.ed', 'med', 'B.P.ED', 'BPED', 'b.p.ed', 'bped', 'M.P.ED', 'MPED', 'm.p.ed', 'mped',
    'Master', 'master', 'Masters', 'masters', 'Bachelor', 'bachelor', 'Bachelors', 'bachelors', 'Diploma', 'diploma', 'DIPLOMA', 'Diplomas', 'diplomas', 'DIPLOMAS',
]


def parse_resume(resume_file):
    parsed_data = {'name': None, 'email': None, 'mobile': None,
                   'skills': None, 'education': None}
    # Handle .docx files
    if resume_file.name.endswith('.docx'):
        textinput = doctotext(resume_file)
        extract_name(textinput)
        extract_mobile_number(textinput)
        extract_email_addresses(textinput)
        extract_skills(textinput)
        extract_education(textinput)
        # Insert parsed data into database
        parsed_data['name'] = extract_name(textinput)
        parsed_data['email'] = extract_email_addresses(textinput)
        parsed_data['mobile'] = extract_mobile_number(textinput)
        parsed_data['skills'] = extract_skills(textinput)
        parsed_data['education'] = extract_education(textinput)

    # Handle .pdf files
    elif resume_file.name.endswith('.pdf'):
        textinput = pdftotext(resume_file)
        extract_name(textinput)
        extract_mobile_number(textinput)
        extract_email_addresses(textinput)
        extract_skills(textinput)
        extract_education(textinput)

        # Insert parsed data into database
        parsed_data['name'] = extract_name(textinput)
        parsed_data['email'] = extract_email_addresses(textinput)
        parsed_data['mobile'] = extract_mobile_number(textinput)
        parsed_data['skills'] = extract_skills(textinput)
        parsed_data['education'] = extract_education(textinput)
        
    else:
        print("File format not supported")

    # Extract text from resume file uploaded the parsed data
    return parsed_data

# Extracting text from DOCX

def doctotext(m):
    temp = docx2txt.process(m)
    resume_text = [line.replace('\t', ' ')
                   for line in temp.split('\n') if line]
    text = ' '.join(resume_text)
    return (text)

# Extracting text from PDF

def pdftotext(uploaded_file):
    # Use the read method to get the content of the uploaded file
    pdf_content = uploaded_file.read()
    # Create a BytesIO object to simulate a file-like object
    from io import BytesIO
    pdfFileObj = BytesIO(pdf_content)
    # Create a PdfReader object
    pdfFileReader = PdfReader(pdfFileObj)
    # Number of pages in the PDF
    num_pages = len(pdfFileReader.pages)
    currentPageNumber = 0
    text = ''
    # Loop through all the PDF pages
    while currentPageNumber < num_pages:
        # Get the specified PDF page object
        pdfPage = pdfFileReader.pages[currentPageNumber]
        # Get PDF page text
        text = text + pdfPage.extract_text()
        # Move to the next page
        currentPageNumber += 1

    return text

# Extracting name

def extract_name(resume_text):
    nlp_text = nlp(resume_text)
    # First name and Last name are always Proper Nouns
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    matcher.add('NAME', [pattern])  # Wrap the pattern in a list
    matches = matcher(nlp_text)
    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text

# Extracting education

def extract_education(resume_text):
    nlp_text = nlp(resume_text)
    # Use sentence boundaries directly on the Doc object
    nlp_text = [sent.text.strip() for sent in nlp_text.sents]
    edu = {}
    # Extract education degree
    for index, text in enumerate(nlp_text):
        for tex in text.split():
            # Replace all special symbols
            tex = re.sub(r'[?|$|.|!|,]', r'', tex)
            if tex.upper() in EDUCATION and tex.lower() not in STOPWORDS:
                # Check if the next sentence is available before accessing
                next_sentence = nlp_text[index +
                                         1] if index + 1 < len(nlp_text) else ""
                edu[tex] = text + next_sentence

    # Extract year
    education = []
    for key in edu.keys():
        year = re.search(re.compile(r'((20|19)\d{2})'), edu[key])
        if year:
            education.append((key, year.group(0)))
        else:
            education.append(key)
    return education

# Extracting skills

def extract_skills(resume_text):
    nlp_text = nlp(resume_text)
    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]
    # reading the csv file
    data = pd.read_csv(MEDIA_URL_SKILLS)
    # extract values
    skills = list(data.columns.values)
    skillset = []
    # check for one-grams
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)

    # check for bi-grams and tri-grams
    for token in nlp_text.noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)

    return [i.capitalize() for i in set([i.lower() for i in skillset])]

# Extracting mobile number

def extract_mobile_number(resume_text):
    phone = re.findall(re.compile(
        r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), resume_text)

    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            return number
        else:
            return number
    else:
        return None

# Extracting email addresses

def extract_email_addresses(string):
    r = re.compile(r'[\w\.-]+@[\w\.-]+')
    return r.findall(string)

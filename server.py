import sys
import os
import fitz
import re

from flask import Flask, jsonify, request, flash, send_file
import json
import subprocess
import os
import shutil
import random
import logging


class Redactor:

    # static methods work independent of class object
    @staticmethod
    def get_sensitive_data(lines):
        """ Function to get all the lines """

        # email regex
        EMAIL_REG = r"([\w\.\d]+\@[\w\d]+\.[\w\d]+)"
        # WEBSITE_URL_REG = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        WEBSITE_URL_REG = r"([\w\d]+\.[\w\d]+\.[\w\d]+)"
        PHONE = '([(]?\+84[)]?[ ]*\d{1,3}|0\d{2,4})[ ]?(-|\.)?[ ]?\d{3,4}[ ]?(-|\.)?[ ]?\d{3,4}'
        for line in lines:

            # matching the regex to each line
            if re.search(EMAIL_REG, line, re.IGNORECASE):
                search = re.search(EMAIL_REG, line, re.IGNORECASE)

                # yields creates a generator
                # generator is used to return
                # values in between function iterations
                print(search.group())
                yield search.group(1)
            if re.search(PHONE, line, re.IGNORECASE):
                search = re.search(PHONE, line, re.IGNORECASE)

                # yields creates a generator
                # generator is used to return
                # values in between function iterations
                print(search.group())
                yield search.group()
            if re.search(WEBSITE_URL_REG, line, re.IGNORECASE):
                search = re.search(WEBSITE_URL_REG, line, re.IGNORECASE)

                # yields creates a generator
                # generator is used to return
                # values in between function iterations
                print(search.group())
                yield search.group()

    # constructor
    def __init__(self, path):
        self.path = path

    def redaction(self):
        """ main redactor code """

        # opening the pdf
        doc = fitz.open(self.path)

        # iterating through pages
        for page in doc:

            # _wrapContents is needed for fixing
            # alignment issues with rect boxes in some
            # cases where there is alignment issue
            # page._wrapContents()

            # geting the rect boxes which consists the matching email regex
            sensitive = self.get_sensitive_data(page.getText("text")
                                                .split('\n'))
            for data in sensitive:
                areas = page.searchFor(data)

                # drawing outline over sensitive datas
                [page.addRedactAnnot(area, fill=(255, 255, 0))
                 for area in areas]

            # applying the redaction
            page.apply_redactions()

        # saving it to a new pdf
        doc.save('redacted.pdf')
        print("Successfully redacted")


try:
    from flask_cors import CORS  # The typical way to import flask-cors
except ImportError:
    # Path hack allows examples to be run without installation.
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.sys.path.insert(0, parentdir)

    from flask_cors import CORS

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)
logging.basicConfig(level=logging.INFO)

TMP_PATH = 'temporary_data/'

DATA_PATH = 'data/'


@app.route('/parser', methods=['POST'])
def get_request():
    pdf_file = request.files.getlist('file')[0]
    check_folder()

    # rand = random.randint(0, 1000000)
    # path_file = TMP_PATH + str(rand) + '/'
    # while os.path.isdir(path_file):
    #     rand = random.randint(0, 1000000)
    #     path_file = TMP_PATH + str(rand) + '/'
    # os.mkdir(path_file)
    
    pdf_file.save('%s/%s' % (DATA_PATH, pdf_file.filename.replace(" ", "_")))

    # cv_parser = CvParser()

    result = None
    # try:
    # if language(path_file) == 'vi':
    #     redactor = Redactor('%s/%s' % (path_file, pdf_file.filename.replace(" ", "_")))
    #     redactor.redaction()
    # else:
    #     # TODO parser for english cv
    #     result = cv_parser.get_list_json()

    # clear(path_file)
    redactor = Redactor('%s/%s' % (DATA_PATH, pdf_file.filename.replace(" ", "_")))
    redactor.redaction()
    return send_file('redacted.pdf')

    # except:
    # 	return jsonify({"error": "can't parse file"}), 400


def check_folder():
    if not os.path.isdir(TMP_PATH):
        os.mkdir(TMP_PATH)
    if not os.path.isdir(DATA_PATH):
        os.mkdir(DATA_PATH)


def clear(path_file):
    for filename in os.listdir(path_file):
        if filename.endswith('.pdf'):
            shutil.copyfile(path_file + filename,
                            '%s%s' % (DATA_PATH, filename))
            logging.info(
                f'\tFile {filename} is saved at {DATA_PATH}{filename}')
            logging.info(f'\tParsed file')

    shutil.rmtree(path_file)


def language(path_file):
    return 'vi'


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000,
                        type=int, help='port listening')
    args = parser.parse_args()
    port = args.port
    app.secret_key = 'super secret key'
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True, processes=1)

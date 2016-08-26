import os
import argparse
import logging
from validate_email import validate_email
from google import search as google_search

SUPPORTED_FILE_TYPES = ['.csv', '.xls']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', 'Path to data.')

    logger = logging.Logger(__name__, logging.DEBUG)
    args = parser.parse_args()
    if os.path.exists(args.file):
        file_name, file_ext = os.path.splitext(args.file)
        if not file_ext:
            logger.log(logging.ERROR, 'File without extension.')
            return
        if file_ext not in SUPPORTED_FILE_TYPES:
            logger.log(logging.ERROR, 'File type not supported.')
            return

def parse_domain(company_name):
    domain = list(google_search(company_name, stop=1, num=1))[0]
    return domain[11:-1]


def make_variations(fname, lname, domain):
    fchar = fname[0]
    lchar = lname[0]
    a = [
        fname + '@' + domain,
        fname + lname + '@' + domain,
        fname + '_' + lname + '@' + domain,
        fname + '.' + lname + '@' + domain,
        fchar + lname + '@' + domain,
        fchar + '_' + lname + '@' + domain,
        fchar + '.' + lname + '@' + domain,
        fname + lchar + '@' + domain,
        fname + '_' + lchar + '@' + domain,
        fname + '.' + lchar + '@' + domain,
        fchar + lchar + '@' + domain,
        fname + '@gmail.com',
        fname + lname + '@gmail.com',
        fname + '_' + lname + '@gmail.com',
        fname + '.' + lname + '@gmail.com',
        fchar + lname + '@gmail.com',
        fchar + '_' + lname + '@gmail.com',
        fchar + '.' + lname + '@gmail.com',
        fname + lchar + '@gmail.com',
        fname + '_' + lchar + '@gmail.com',
        fname + '.' + lchar + '@gmail.com',
        fchar + lchar + '@gmail.com',
        ]
    return a

def validate(possible_emails_list):
    for x in possible_emails_list:
        if validate_email(x,verify=True):
            return x
    return 'Not found'

if __name__ == '__main__':
    main()

import os
import argparse
import logging
from validate_email import validate_email
from google import search as google_search
import csv

SUPPORTED_FILE_TYPES = ['.csv']


def csv_reader(filepath):
    with open(filepath, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            yield row


done = 0
def main():
    counter = 0
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='Path to data.', required=True)
    args = parser.parse_args()

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s] - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if os.path.exists(args.file):
        file_name, file_ext = os.path.splitext(args.file)
        if not file_ext:
            logger.error('File without extension.')
            return
        if file_ext not in SUPPORTED_FILE_TYPES:
            logger.error('File type not supported.')
            return

        for row in csv_reader(args.file):
            if counter == 1000:
                break
            if counter > 0:
                try:
                    name, lastname = row[0].split(' ')
                    domain = parse_domain(row[1])
                    validate(make_variations(name, lastname, domain))
                except ValueError:
                    pass

            counter += 1
        print str(done)  +  '/' + str(counter) + ' emails found'

    else:
        logger.error('File doesn\'t exist.')
        return


def parse_domain(company_name):
    if 'freelance' in company_name or 'google' in company_name:
        return 'gmail.com'
    domain = list(google_search(company_name, stop=1, num=1))[0]
    if 'https://' in domain:
        domain = domain[12:-1]
        if '/' in domain:
            return domain[:domain.index('/')]
    domain = domain[11:-1]
    if '/' in domain:
        domain = domain[:domain.index('/')]
    return domain


def make_variations(fname, lname, domain):
    try:
        fchar = fname[0]
        lchar = lname[0]
    except IndexError:
        return
    try:
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
    except UnicodeDecodeError:
        return
    return a


def validate(possible_emails_list):
    if possible_emails_list:
        for x in possible_emails_list:
            print x
            if validate_email(x,verify=True):
                global done
                done += 1
                print 'valid email: ' + x

                return x
    return None


if __name__ == '__main__':
    main()

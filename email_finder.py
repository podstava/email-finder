import os
import argparse
import logging
from validate_email import validate_email
from urlparse import urlparse
# from google import search as google_search
import csv

from selenium import webdriver, common
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def google_search(company_name):
    print '-----starting search-------'
    driver = webdriver.Firefox()
    driver.get("http://www.google.com")
    input_element = driver.find_element_by_name("q")
    try:
        input_element.send_keys(company_name)
        input_element.submit()

        RESULTS_LOCATOR = "//div/cite"

        WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, RESULTS_LOCATOR)))

        page1_results = driver.find_elements(By.XPATH, RESULTS_LOCATOR)
        res_list = []
        for item in page1_results[0:4]:
            print 'url found ' + item.text
            res_list.append(item.text)
        driver.close()
        return res_list
        # input_element.clear()
    except common.exceptions.TimeoutException:
        driver.close()
        driver = webdriver.Firefox()
        driver.get("http://www.google.com")



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
            try:
                name, lastname = row[0].split(' ')
                domain = parse_domains(row[1])
                validate(make_variations(name, lastname, domain))
                percents = (counter * 100) / 1000
                print str(percents) + '% done'

            except ValueError:
                pass

            counter += 1
        global done
        print str(done) + '/' + str(counter) + ' emails found'

    else:
        logger.error('File doesn\'t exist.')
        return


def parse_domains(company_name):
    print 'company: ' + company_name
    if 'Freelance' in company_name or 'Google' in company_name or company_name == '':
        return ['gmail.com']
    domains = google_search(company_name)
    res_list = []
    for domain in domains:
        if urlparse(domain)[1] == '':
            domain = urlparse(domain)[2]
        else:
            domain = urlparse(domain)[1]
        if 'www.' in domain:
            domain = domain[4:]
        if '/' in domain:
            domain = domain[:domain.index('/')]
        if '\\' in domain:
            domain = domain[:domain.index('\\')]

        res_list.append(domain)
    res_list.append('gmail.com')
    return res_list


def make_variations(fname, lname, domains):
    print '-------- start making variations -------'
    print domains
    try:
        print 'zalupa'
        fchar = fname[0]
        lchar = lname[0]
    except IndexError:
        print 'index error'
        return
    a = []
    try:
        for domain in domains:
            a += ['{}@{}'.format(fname, domain)]
            a += ['{}{}@{}'.format(fname, lname, domain)]
            a += ['{}_{}@{}'.format(fname, lname, domain)]
            a += ['{}.{}@{}'.format(fname, lname, domain)]
            a += ['{}{}@{}'.format(fchar, lname, domain)]
            a += ['{}_{}@{}'.format(fchar, lname, domain)]
            a += ['{}.{}@{}'.format(fchar, lname, domain)]
            a += ['{}{}@{}'.format(fname, lchar, domain)]
            a += ['{}_{}@{}'.format(fname, lchar, domain)]
            a += ['{}.{}@{}'.format(fname, lchar, domain)]
            a += ['{}{}@{}'.format(fchar, lchar, domain)]
            print a
    except UnicodeDecodeError:
        print 'Name contains specific symbols'
        return
    for x in a:
        print x
    print '--- end variations ---'
    return a


def validate(possible_emails_list):
    print '******validation started ******'
    if possible_emails_list:
        for x in possible_emails_list:
            print x
            if validate_email(x,verify=True):
                global done
                done += 1
                print '******valid email: ' + x + '********'

                return x
    return None


if __name__ == '__main__':
    main()

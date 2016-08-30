import os
import argparse
import logging

import timeit
from validate_email import validate_email
from urlparse import urlparse
import DNS
from DNS.Base import TimeoutError

import csv

from selenium import webdriver, common
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DNS.defaults['server'].append('208.67.222.222')
DNS.defaults['server'].append('208.67.222.220')
DNS.defaults['server'].append('8.8.8.8 ')

DNS.defaults['timeout'] = 1


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s] - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def google_search(company_name):
    logger.info('starting search for domain of {}'.format(company_name))
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
            logger.info('url found {}'.format(item.text))
            res_list += [item.text]
        driver.close()
        return res_list
    except common.exceptions.TimeoutException:
        logger.info('got timeout')
        driver.close()
        driver = webdriver.Firefox()
        driver.get("http://www.google.com")


SUPPORTED_FILE_TYPES = ['.csv']


def csv_reader(filepath):
    with open(filepath, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            yield row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='Path to data.', required=True)
    args = parser.parse_args()

    if os.path.exists(args.file):
        file_name, file_ext = os.path.splitext(args.file)
        if not file_ext:
            logger.error('File without extension.')
            return
        if file_ext not in SUPPORTED_FILE_TYPES:
            logger.error('File type not supported.')
            return

        counter = 0
        done = 0
        limit = 100
        start = timeit.default_timer()
        for row in csv_reader(args.file):
            if counter == limit:
                break
            try:
                name, lastname = row[0].lower().split(' ')
                domain = parse_domains(row[1])
                done += 1 if validate(make_variations(name, lastname, domain)) else 0
                percents = (counter * 100.0) / limit
                logger.info('{:.2f}% processed.'.format(percents))

            except ValueError:
                logger.info('name contains more than two words')
                pass

            counter += 1
        logger.info('{}/{} emails found'.format(done, counter))
        logger.info('finished for {}'.format(timeit.default_timer() - start))

    else:
        logger.error('File doesn\'t exist.')
        return

stop_domains = ['linkedin.com',
                'twitter.com',
                'facebook.com',
                'vk.com',
                'microsoft.com',
                'microsoftstore.com'
                'en.wikipedia.org',
                'uk.wikipedia.org',
                'ru.wikipedia.org',
                'pt.wikipedia.org',
                'de.wikipedia.org'
                'wikipedia.org',
                'tripadvisor.com',
                'youtube.com',
                'amazon.com',
                'jobs.dou.ua',
                'uk-ua.facebook.com',
                'ru-ru.facebook.com',
                'en-gb.facebook.com',
                'es-es.facebook.com',
                'es-la.facebook.com',
                'ain.ua',
                'twich.tv',
                'play.google.com',
                'itunes.apple.com',
                'sourceforge.net',
                'INTERNETUA',
                'FINANCE.UA',
                'crunchbase.com',
                'hotline.ua',
                'stackoverflow.com',
                'bloomberg.com',
                'dictionary.com',
                'fortune.com',
               ]
def parse_domains(company_name):
    logger.info('company: {}'.format(company_name))
    if 'freelance' in company_name.lower() or 'google' in company_name.lower() or company_name == '' or company_name == '-':
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
        if domain not in stop_domains and domain not in res_list:
            res_list += [domain]
    res_list += ['gmail.com']
    return res_list


def make_variations(fname, lname, domains):
    logger.info('-------- start making variations --------')
    try:
        fchar = fname[0]
        lchar = lname[0]
    except IndexError:
        logger.error('index error')
        return
    emails = []
    try:
        for domain in domains:
            emails += ['{}@{}'.format(fname, domain)]
            emails += ['{}{}@{}'.format(fname, lname, domain)]
            emails += ['{}_{}@{}'.format(fname, lname, domain)]
            emails += ['{}.{}@{}'.format(fname, lname, domain)]
            emails += ['{}{}@{}'.format(lname, fname, domain)]
            emails += ['{}_{}@{}'.format(lname, fname, domain)]
            emails += ['{}.{}@{}'.format(lname, fname, domain)]
            emails += ['{}{}@{}'.format(fchar, lname, domain)]
            emails += ['{}_{}@{}'.format(fchar, lname, domain)]
            emails += ['{}.{}@{}'.format(fchar, lname, domain)]
            emails += ['{}{}@{}'.format(fname, lchar, domain)]
            emails += ['{}_{}@{}'.format(fname, lchar, domain)]
            emails += ['{}.{}@{}'.format(fname, lchar, domain)]
            emails += ['{}{}@{}'.format(fchar, lchar, domain)]
            emails += ['{}{}@{}'.format(lchar, fname, domain)]
            emails += ['{}_{}@{}'.format(lchar, fname, domain)]
            emails += ['{}.{}@{}'.format(lchar, fname, domain)]
            emails += ['{}{}@{}'.format(lname, fchar, domain)]
            emails += ['{}_{}@{}'.format(lname, fchar, domain)]
            emails += ['{}.{}@{}'.format(lname, fchar, domain)]
            emails += ['{}{}@{}'.format(lchar, fchar, domain)]
            emails += ['{}@{}'.format(lname, domain)]
    except UnicodeDecodeError:
        logger.error('Name contains specific symbols')
        return
    logger.info('variations for {} {}'.format(fname, lname))
    for email in emails:
        logger.info(email)
    logger.info('-------- end variations --------')
    return emails


def validate(emails):
    logger.info('-------- validation started --------')
    if emails:
        try:
            for email in emails:
                if validate_email(email, verify=True):
                    logger.info('*** valid email: {} ***'.format(email))
                    logger.info('-------- validation ended --------')
                    return email
                logger.info('invalid email: {}'.format(email))
        except TimeoutError:
           logger.info('-------- Timeout error --------')
    return None


if __name__ == '__main__':
    main()

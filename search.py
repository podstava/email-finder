import os
import logging

import timeit
from urlparse import urlparse

import csv

from validate_email import validate_email
import itertools

from selenium import webdriver, common
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from threading import Thread
from Queue import Queue as Q
import Queue


FILE = 'attendees.csv'

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

        result_location = "//div/cite"

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, result_location)))

        page1_results = driver.find_elements(By.XPATH, result_location)
        driver.quit()
        res_list = []
        for item in page1_results[0:4]:
            logger.info('url found {}'.format(item.text))
            res_list += [item.text]

        return res_list
    except common.exceptions.TimeoutException:
        driver.quit()
        pass


def csv_reader(file_path):
    with open(file_path, 'rb') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            yield row


def parse_domains(company_name):
    stop_domains = ['linkedin.com',
                    'twitter.com',
                    'facebook.com',
                    'vk.com',
                    'microsoft.com',
                    'wikipedia.com',
                    'tripadvisor.com',
                    'youtube.com',
                    'ru - ru.facebook.com']

    logger.info('company: {}'.format(company_name))
    if 'freelance' in company_name.lower() \
                    or 'google' in company_name.lower() \
                    or company_name == ''\
                    or company_name == '-':
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
        if domain not in stop_domains:
            res_list += [domain]
    return res_list


def make_variations(name_list, domains):
    logger.info('-------- start making variations --------')
    if not domains:
        return
    names = []
    parsed_names = []
    emails = []
    try:
        for L in range(0, len(name_list) + 1):
            for subset in itertools.combinations(name_list, L):
                names += [subset]
        for x in names:
            if x == () or x == ('',):
                continue
            parsed_names += ['_'.join(x).lower()]
            if ''.join(x).lower() in parsed_names:
                continue
            parsed_names += [''.join(x).lower()]
            parsed_names += ['.'.join(x).lower()]

        for domain in domains:
            for res in parsed_names:
                emails += [res + '@' + domain]
    except UnicodeDecodeError:
        logger.error('Name contains specific symbols')
        return
    for email in emails:
        logger.info(email)
    logger.info('-------- end variations --------')
    return emails


def validate(emails):
    logger.info('-------- validation started --------')
    if emails:
        for email in emails:
            if validate_email(email, verify=True):
                logger.info('*** valid email: {} ***'.format(email))
                logger.info('-------- validation ended --------')
                return email
            logger.info('invalid email: {}'.format(email))
    return None


def handler_thread():
    while True:
        try:
            row = q_initial.get(block=False)
            name_list = list(row[0].lower().split(' '))
            domain = parse_domains(row[1])
            email = make_variations(name_list, domain)
            if validate(email):
                q_result.put(validate(email))
            # done += 1 if validate(make_variations(name, last_name, domain)) else 0
            # percents = (counter * 100) / limit
            # logger.info('{:.2f}% processed.'.format(percents))
        except Queue.Empty:
            break
        except ValueError:
            logger.info('name contains more than two words')


def writer_thread():
    """Write output to file here."""
    while True:
        try:
            with open('results.txt', 'a') as result_file:
                result_file.write(str(q_result.get()) + '\n')
        except Queue.Empty:
            break


q_initial = Q()
q_result = Q()


def threads_start(file_reader, csv_file, threads_count):
    counter = 0
    end = 2000
    start = 1100
    for row in file_reader(csv_file):
        if counter < start:
            counter += 1
            continue
        if counter == end:
            break
        q_initial.put(row)
        print counter
        counter += 1

    threads = []

    for i in xrange(threads_count):
        th = Thread(target=handler_thread)
        th.start()
        threads.append(th)

        tw = Thread(target=writer_thread)
        tw.start()
        threads.append(tw)

    for t in threads:
        t.join()

        print threads


if __name__ == '__main__':
    start = timeit.default_timer()
    threads_start(csv_reader, FILE, 4)
    print 'finished for {}'.format(timeit.default_timer() - start)

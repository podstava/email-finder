import os
import argparse
import logging

SUPPORTED_FILE_TYPES = ['.csv', '.xls']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', 'Path to data.')
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
    else:
        logger.error('File doesn\'t exist.')
        return


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

if __name__ == '__main__':
    main()

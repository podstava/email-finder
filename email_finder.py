import os
import argparse
import logging

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

if __name__ == '__main__':
    main()

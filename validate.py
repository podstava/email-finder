import re

from pyexcel_xls import get_data, save_data
from collections import OrderedDict
from google import search
from validate_email import validate_email


class ExcelMixin(object):

    def __init__(self, path_to_file):
        self.file = path_to_file
        self.__read_from_file()
        self.__data_for_write = OrderedDict()

    def __read_from_file(self):
        self.data = get_data(self.file)

    def _print_data(self):
        print self.data

    def _get_first_sheet_rows(self):
        return self.data.items()[0][1]

    def __write_into_file(self, path_to_file):
        save_data(path_to_file, self.__data_for_write)

    def _set_data_for_first_sheet(self, sheet_name, rows):
        """Adds rows to variable which will be saved to the excel file"""
        self.__data_for_write.update({sheet_name: rows})

    def get_excel(self):
        self._set_data_for_first_sheet('Sheet 1', [["row 1", "row 2", "row 3"]])
        self.__write_into_file('test_result.xls')


class GoogleSearchMixin(object):
    _search_results = None
    _search_stop = 8

    def _make_search(self, query_words):
        self._search_results = search(query_words, stop=self._search_stop)

    def _get_search_results(self):
        return self._search_results

    @staticmethod
    def search(query, stop):
        return search(query, stop=stop)


class ValidationEmailMixin(object):
    _email = None

    def _email_is_valid(self):
        validate_email(self._email, verify=True)

    @staticmethod
    def _match_domain(url):
        return re.search('\w+.\w+$', url).group(0)


class EmailFinder(ExcelMixin, GoogleSearchMixin, ValidationEmailMixin):

    def __init__(self, excel_file_name):
        super(EmailFinder, self).__init__(excel_file_name)

    def generate(self):
        result = []
        for row in self._get_first_sheet_rows():
            name = row[0]
            company = row[1]
            country = row[2]
            self._make_search(' '.join([company, country]))
            for url in self._get_search_results():
                if self._match_domain(url):
                    pass


if __name__ == "__main__":
    print ExcelMixin('/home/vs/Downloads/attendees.xls')._get_first_sheet_rows()
    # ExcelMixin('test.xls')._print_data()
    # ExcelMixin('test.xls').get_excel()
    # gs = GoogleSearchMixin()
    # gs._make_search('search')
    # for d in gs._get_search_results():
    #     print d
    print ValidationEmailMixin._match_domain('https://www.filepicker.io')

from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='email-search',
    version='1.0',
    download_url='https://github.com:podstave/email-finder.git',
    py_modules=('search',),
    author='py3d_team',
    author_email='uriah_S@ukr.net',
    description='validate_email verifies if an email address is valid and really exists.',
    keywords='email finder with verification mx verify',
    url='http://github.com/podstava/email-finder',
    license='All_rights_reserved',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    install_requires=['validate_email==1.3'],
    include_package_data=True,
)


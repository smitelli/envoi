import re
from setuptools import setup, find_packages

with open('envoi/__init__.py', 'r') as fh:
    version = re.search(r"__version__ = '(.*?)'", fh.read()).group(1)

with open('README.md', 'r') as fh:
    readme = fh.read()

setup(
    name='envoi',
    version=version,
    author='Scott Smitelli',
    author_email='scott@smitelli.com',
    description='Converts YAML invoice data into reasonably well-formatted PDFs.',
    long_description=readme,
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=['fpdf2 ~= 2.7.9', 'PyYAML ~= 6.0.1'],
    extras_require={
        'dev': ['flake8 ~= 7.1.0']},
    entry_points={
        'console_scripts': [
            'envoi = envoi:cli'
        ]
    },
)

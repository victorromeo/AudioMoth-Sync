from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup (
    name='audiomothsync',
    version='0.1.0',
    description='Utility to capture audio and visual data on motion',
    long_description=readme,
    author='victorromeo',
    author_email='',
    url='https://github.com/victorromeo/AudioMoth-Sync',
    license=license,
    packages=find_packages(exclude=('apps', 'archive', 'capture', 'doc', 'firmware', 'housing', 'tests'))
)
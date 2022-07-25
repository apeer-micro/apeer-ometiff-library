import setuptools
from setuptools import setup

setup(name='apeer-ometiff-library',
      version='1.10.1',
      description='Library to read and write ometiff images',
      url='https://github.com/apeer-micro/apeer-ometiff-library',
      author='apeer-micro',
      packages=setuptools.find_packages(),
      install_requires=['numpy>=1.18.5','tifffile==2020.6.3', 'imagecodecs==2020.5.30'],
      license='MIT',
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ])

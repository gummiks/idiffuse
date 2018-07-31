from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='idiffuse',
      version='0.0.1',
      description='A tool to calculate on-sky diffuser-assisted photometric precisions',
      long_description=readme(),
      url='https://github.com/gummiks/idiffuse',
      author='Gudmundur Stefansson',
      author_email='gummiks@gmail.com',
      install_requires=['pysynphot','pandas>0.20.0','numpy>1.11','matplotlib>1.5.3'],
      packages=['idiffuse'],
      license='GPLv3',
      classifiers=['Topic :: Scientific/Engineering :: Astronomy'],
      keywords='Diffusers Photometry Astronomy',
      include_package_data=True
      )

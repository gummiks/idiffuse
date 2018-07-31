# Installation

There are two main ways to install `iDiffuse`:


## From Git
`iDiffuse` can be installed from Git in the following way:
```
git clone https://github.com/gummiks/idiffuse.git
python setup.py install
```

## From pip
`iDiffuse` can be installed from pip with the following command:
```
pip install idiffuse
```

## Notes
`iDiffuse` depends on `pysynphot`, which can be set up to include a number of additional setup files as defined by the `PYSYN_CDBS` environment variable, and `pysynphot` will throw a warning if this variable is not set saying:
```
UserWarning: PYSYN_CDBS is undefined; functionality will be SEVERELY crippled.
```
However, `idiffuse` does not currently depend on that functionality in `pysynphot`, and this warning can be ignored.

If the warning is annoying and/or you want to use more of the functionalities `pysynphot` has to offer, you can follow the `pysynphot` installation instruction <a href='https://pysynphot.readthedocs.io/en/latest/#installation-and-setup'>here</a>

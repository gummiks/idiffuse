import numpy as np

def phot_error(star_ADU,n_pix,n_b,sky_ADU,dark,read,gain=1.0):
    """
    Photometric error including 

    INPUT:
        star_ADU - stellar flux in ADU (total ADU counts within aperture)
        n_pix - number of pixels in aperture
        n_b  - number of background pixels
        sky_ADU - in ADU/pix
        dark - in e/pix 
        read - in e^2/pix
        gain - gain in e/ADU

    OUTPUT:
        Photometric error N in ADUs

    NOTES:
        This is not the normalized error. To normalize, have to do sigma_rel = N / star_ADU
        This does not include scintillation
    """
    noise = np.sqrt( gain*star_ADU + n_pix *((1. + n_pix/n_b) * (gain*sky_ADU + dark + read**2. + (gain*0.289)**2. )) )/gain
    return noise

def scintillation_noise(diameter,airmass,exptime,altitude,wavelength=None,withextra=True):
    """
    See eq B4 on page 22 in AIJ paper (Collins et al. 2017)
    
    INPUT:
        diameter - diameter of telescope in cm
        airmass  - airmass 
        exptime  - exposure time in s
        altitude -altitude of the observatory in m
        wavelength - if not None, include (lambda/550nm)**-7/12 dependence from Birney et al. 2006. Units: nm
        withextra - True, recommended extra factor of 1.5 as suggested by Osborn et al. 2011, 2015
    
    OUTPUT:
        sigma_scintillation - the scintillation noise
    
    EXAMPLE:
        diameter = 61. #cm
        airmass = 1. #varies 1 - 2
        exptime = 120. # in s
        altitude = 360. # in m
        scint_noise = scintillation_noise(diameter,airmass,exptime,altitude)
    """
    scint_err = 0.09*(diameter**(-2./3.))*(airmass**1.75)*((2.*exptime)**-0.5)*np.exp(-altitude/8000.)
    if withextra==True:
        # Extra factor of 1.5 according to Osborn et al. 2011 / 2015
        scint_err *= 1.5
    if wavelength != None:
        return scint_err * (wavelength/550.)**(-7./12.)
    else:
        return scint_err

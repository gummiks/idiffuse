import numpy as np

def calculate_diffuser_fwhm(opening_angle,distance_from_detector,pix_size):
    """
    Calculate the diffuser FWHM for a given opening angle
    
    INPUT:
        opening_angle - opening angle in degrees (full cone angle)
        distance_from_detector - distance in mm
        pix_size - pixel size in micron
    
    OUTPUT:
        FWHM in pixels
        
    EXAMPLE:
        calculate_diffuser_fwhm(0.34,200.,13.5)
    """
    return (2.*np.tan((opening_angle/2.)*np.pi/180.))*distance_from_detector/(pix_size/1000.)

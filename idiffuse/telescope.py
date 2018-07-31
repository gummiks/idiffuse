from __future__ import print_function
import numpy as np
import pandas as pd
import idiffuse.photometry as photometry
import idiffuse.diffuser as diffuser
import pysynphot as S
import matplotlib.pyplot as plt
import os
import glob


class Telescope(object):
    """
    A Telescope Object to use for diffuser calculations.

    Can be used to calculate 

    NOTES:
        - Depends on pysynphot for flux calculations

    EXAMPLE:
        See TelescopeARC() class, which implements the ARC 3.5m telescope at APO
    """
    # Get filter names, save as a dict
    DIRNAME = os.path.dirname(__file__)
    FILTER_DIRNAME = os.path.join(DIRNAME,'filters')
    FILTER_FILENAMES = glob.glob(os.path.join(FILTER_DIRNAME,"*"))
    FILTER_BASENAMES = [os.path.basename(i) for i in FILTER_FILENAMES]
    FILTER_DICT = dict(zip(FILTER_BASENAMES, FILTER_FILENAMES))
    def __init__(self,
                 name,
                 diameter,
                 fnum,
                 flength,
                 gain,
                 pix_size,
                 fov,
                 num_pix,
                 plt_scale,
                 dark_noise,
                 read_noise,
                 altitude,
                 central_obstruction,
                 QE,
                 Throughput,
                 diffuser_angle,
                 diffuser_dist_from_detector):
        """
        INPUT:
             diameter   - diameter in cm
             fnum       - fnumber of telescope
             flength    - focal length of telescope
             gain       - gain in e/adu
             pix_size   - pix size in micron
             fov        - fov in arcmin, e.g., 8 (currently not being used)
             num_pix    - number of x-axis pixels in detector (currently not being used)
             plt_scale  - plate scale in arcsec/pix
             dark_noise - dark noise in e/pix/s
             read_noise - read noise in e^2
             altitude   - altitude in m
             central_obstruction - central obstruction, number from 0-1
             QE         - pysynphot.FileSpectralElement
             Throughput - pysynphot.UniformTransmission
             diffuser_angle - diffuser opening angle in degrees
             diffuser_dist_from_detector - distance of diffuser from detector in mm
        EXAMPLE:
        """
        self.name                        = name
        self.diameter                    = diameter
        self.fnum                        = fnum
        self.flength                     = flength
        self.gain                        = gain
        self.pix_size                    = pix_size
        self.fov                         = fov
        self.num_pix                     = num_pix
        self.plt_scale                   = plt_scale
        self.dark_noise                  = dark_noise
        self.read_noise                  = read_noise
        self.altitude                    = altitude
        self.central_obstruction         = central_obstruction
        self.QE                          = QE
        self.Throughput                  = Throughput
        self.area                        = np.pi*((self.diameter/2.)**2.)*(1-self.central_obstruction)

        # Diffuser related values
        self.diffuser_angle              = diffuser_angle
        self.diffuser_dist_from_detector = diffuser_dist_from_detector
        self.diffuser_fwhm_pix = diffuser.calculate_diffuser_fwhm(self.diffuser_angle,
                                                                  self.diffuser_dist_from_detector,
                                                                  self.pix_size)
        self.diffuser_fwhm_arcsec = self.diffuser_fwhm_pix*self.plt_scale
        self.diffuser_fwhm_total_npix = np.pi*(self.diffuser_fwhm_pix/2.)**2.0

    def __str__(self):
        outstring = ""
        outstring += "Telescope: \t\t\t{}".format(self.name)+"\n"
        outstring += "Throughput (flat) (%): \t\t{:0.3f}".format(100*float(str(self.Throughput)))+"\n"
        outstring += "Diameter (cm):\t\t\t{:0.3f}".format(self.diameter)+"\n"
        outstring += "Fnum: \t\t\t\t{:0.3f}".format(self.fnum)+"\n"
        outstring += "Focal length (m): \t\t{:0.3f}".format(self.flength)+"\n"
        outstring += "Gain: \t\t\t\t{:0.3f}".format(self.gain)+"\n"
        outstring += "Pixel size (um): \t\t{:0.3f}".format(self.pix_size)+"\n"
        outstring += "Num pixels: \t\t\t{:0.3f}".format(self.num_pix)+"\n"
        outstring += 'Plate scale (arcsec/pix): \t{:0.3f}'.format(self.plt_scale)+"\n"
        outstring += "FOV (arcmin): \t\t\t{:0.3f}".format(self.plt_scale*self.num_pix/60.)+"\n"
        outstring += "Dark Noise (e/s/pix): \t\t{:0.3f}".format(self.dark_noise)+"\n"
        outstring += "Read Noise (e/pix):   \t\t{:0.3f}".format(self.read_noise)+"\n"
        outstring += "Altitude (m):   \t\t{:0.3f}".format(self.altitude)+"\n"
        outstring += "Central Obstruction (%): \t{:0.3f}".format(self.central_obstruction*100)+"\n"
        outstring += "Diffuser dist to detector (mm):\t{:0.3f}".format(self.diffuser_dist_from_detector)+"\n"
        outstring += "{} available filters in folder:\t{}".format(len(self.FILTER_DICT),self.FILTER_DIRNAME)+"\n"
        return outstring

    def get_filter_filenames(self):
        """
        Return available filter filenames (full absolute paths)
        """
        return sorted(self.FILTER_DICT.values())

    def plot_throughput(self,bandpass=None,bandpass_name='Supplied BandPass'):
        """
        Plot a throughput plot of the telescope.

        INPUT:
            bandpass - plot and additional bandpass (optional)

        OUTPUT:
            plot
        """

        if bandpass is not None:
            combined = self.QE * self.Throughput * bandpass
        else:
            combined = self.QE * self.Throughput

        # Plot
        fig, ax = plt.subplots(dpi=200,figsize=(8,4))

        # Plot QE
        ax.plot(self.QE.wave,self.QE.throughput,lw=2,label='Quantum Efficiency')
        # Plot throughput. Hack if Throughput is a flat throughput
        if self.Throughput.wave is None:
            ax.hlines(self.Throughput.throughput[0],*ax.get_xlim(),color='orange',lw=1,label='Atmospheric+Telescope Throughput (assumed)',linestyle='--')
        else:
            ax.plot(self.Throughput.wave,self.Throughput.throughput,lw=2,label='Atmospheric+Telescope Throughput (assumed)')
        # Plot BandPass
        if bandpass is not None:
            ax.plot(bandpass.wave,bandpass.throughput,lw=1,label=bandpass_name)
        # Plot Combined
        ax.plot(combined.wave,combined.throughput,lw=1,label='Combined transmission')

        ax.minorticks_on()
        ax.grid(lw=0.5,alpha=0.5)
        ax.tick_params(pad=3,labelsize=10)
        ax.set_xlabel('Wavelength [A]',fontsize=15)
        ax.set_ylabel('Throughput',fontsize=15)
        ax.legend(fontsize=10,loc='upper left')
        ax.set_ylim(-0.05,1.5)
        ax.set_title('Throughput: {}'.format(self.name),fontsize=15)

    def __repr__(self):
        return '{} D={:0.1f}cm Throughput={:0.3f}%'.format(self.__class__,self.diameter,100*float(str(self.Throughput)))

    def get_adu_per_sec(self,vegamag,BandPass):
        """
        Get the photon count in phot/s for a star with a Vega magnitude of *vegamag* in a given pysynphot.BandPass

        These are the total photon counts the telescope/imager will see.

        INPUT:
            vegamag  - Vega magnitude in a given bandpass
            BandPass - pysynphot.BandPass class

        OUTPUT:
            photons per second

        NOTES:
            Accounts for QE
        """
        # Convolve QE, BandPass, and Throughput
        CombinedBP = self.QE*self.Throughput*BandPass
        # Use Vega magnitudes
        VegaSpectrum = S.Vega.renorm(vegamag,'vegamag',CombinedBP)
        # Define observation
        obs = S.Observation(VegaSpectrum, CombinedBP)
        # pysynphot is automatically set up to calculate for Hubble, we just need to scale the area
        hubble_area = S.refs.PRIMARY_AREA
        electrons_per_sec = (obs.countrate()/hubble_area)*self.area # electrons per second, as we are using QE information
        # convert to adu_per_sec
        adu_per_sec = electrons_per_sec / self.gain
        return adu_per_sec

    def get_exptime_for_adu(self,vegamag,BandPass,max_adu_per_pixel=40000.,binning=1):
        """
        Get the maximum exposure time to expose for a given ADU. This assumes a perfectly flat-top-hat diffused PSF.

        INPUT:
            vegamag - vegamagnitude of star in given bandpass
            BandPass - pysynphot.bandpass
            max_adu_per_pixel - maximum adu in the diffused PSF
            binning - binning (1, 2 or 4 for ARCTIC)

        OUTPUT:
            exposure time in s to reach the *max_adu_per_pixel* counts

        NOTES:
        """
        diffuser_fwhm_total_npix = self.diffuser_fwhm_total_npix/(binning*binning)
        adu_per_sec = self.get_adu_per_sec(vegamag,BandPass) 
        total_adu_in_aperture = diffuser_fwhm_total_npix * max_adu_per_pixel
        max_exptime = total_adu_in_aperture/adu_per_sec
        return max_exptime

    def get_err_cad_for_adu(self,
                            vegamag,
                            BandPass,
                            max_adu_per_pixel=40000.,
                            binning=2.,
                            num_ref_stars=1.,
                            airmass=1.5,
                            read_time=2.5,
                            sky_mag_per_arcsec=17.5,
                            verbose=True):
        """
        Calculate the total photometric error and cadence, assuming a top-hat PSF for the self.diffuser_opening_angle.

        This calculates the cadence needed to expose on the telescope to reach a maximum of *max_adu_per_pixel* counts
        per pixel on the detector, assuming a top-hat diffused PSF.

        INPUT:
            vegamag           - vegamagnitude in the bandpass supplied
            BandPass          - pysynphot.BandPass of the observation
            max_adu_per_pixel - maximum ADU counts per pixel, assumes a top-hat PSF
            binning           - binning mode used
            num_ref_stars     - number of equally bright reference stars as the target
            airmass           - airmass of observation
            read_time         - read time in seconds
            sky_mag_per_arcsec- sky magnitude of the sky in the full PSF
            verbose=True      - if True, print out useful results

        OUTPUT:
            tot_error - total photometric error including: photon, dark, read, sky, digitization and scintillation noise
            cadence   - total cadence (including read_time) corresponding to the photometric precision returned

        NOTES:
        """
        diffuser_fwhm_pix = self.diffuser_fwhm_pix/binning
        diffuser_fwhm_total_npix = self.diffuser_fwhm_total_npix/(binning**2.) # Total number of pixels in aperture

        # Reference star factor, assuming all refstars are same flux as target star
        refstar_factor = np.sqrt(1.+1./num_ref_stars)

        # Apertures and annuli
        ap_r = diffuser_fwhm_pix/2.
        ap_annul_1 = ap_r*1.5
        ap_annul_2 = ap_r*2.0
        n_pix = diffuser_fwhm_total_npix # Total number of pixels in aperture
        n_b   = (ap_annul_2**2.-ap_annul_1**2.)*np.pi #number of background pixels

        # Get exptime
        exptime = self.get_exptime_for_adu(vegamag,BandPass,max_adu_per_pixel,binning)

        # Total ADU counts
        star_adu = max_adu_per_pixel * n_pix

        # Sky signal, assume sky magnitude is given as mag/arcsec2
        sky_adu_per_arcsec2 = self.get_adu_per_sec(sky_mag_per_arcsec,BandPass) * exptime
        sky_adu = sky_adu_per_arcsec2*np.pi*(self.diffuser_fwhm_arcsec/2.)**2.
        sky_adu_per_pixel = sky_adu/n_pix

        # photon noise in ppm, just calculate this as a reference
        photon_noise = (1e6/np.sqrt(star_adu*self.gain))*refstar_factor

        # Total photometric noise including: photon, sky, dark, read, digitization and refstars
        photometric_noise = (1e6*photometry.phot_error(star_adu,
                                                       n_pix,
                                                       n_b,
                                                       sky_adu_per_pixel,
                                                       dark=self.dark_noise,
                                                       read=self.read_noise,
                                                       gain=self.gain)/star_adu)*refstar_factor

        # Scintillation noise in ppm
        scint_noise = photometry.scintillation_noise(self.diameter,airmass,exptime,
                                                     self.altitude,withextra=True)*1e6*refstar_factor

        # Cadence
        cadence = exptime + read_time
        num_exp_in_1_min = 60./cadence
        num_exp_in_30_min = 1800./cadence

        # total noise
        tot_noise = np.sqrt(photometric_noise**2.+scint_noise**2.)
        tot_noise_in_1_min = tot_noise/np.sqrt(num_exp_in_1_min)
        tot_noise_in_30_min = tot_noise/np.sqrt(num_exp_in_30_min)

        if verbose:
            print('##### Exptime #####')
            print('Exptime [s]:                  {:0.3f}'.format(exptime))
            print('Total cadence [s]:            {:0.3f}'.format(cadence))
            print('Obs. Efficiency [%]:          {:0.2f}'.format(100.*exptime/cadence))
            print('npix [pix]:                   {:0.2f}'.format(n_pix))
            print('n_b [pix]:                    {:0.2f}'.format(n_b))
            print('')
            print('##### Counts #####')
            print('Star counts - Total [adu]:    {:0.2f} '.format(star_adu))
            print('Star counts - /pix [adu/pix]: {:0.2f} '.format(star_adu/n_pix))
            print('Sky counts - Total [adu]:     {:0.2f}'.format(sky_adu))
            print('Sky counts - /pix [adu/pix]:  {:0.2f}'.format(sky_adu_per_pixel))
            print('')
            print('##### Noise in exptime={:0.2f}s ######'.format(exptime))
            print('Photometric noise [ppm]       {:0.2f}'.format(photometric_noise))
            print('Photon noise [ppm]:           {:0.2f}'.format(photon_noise))
            print('Scintillation noise [ppm]:    {:0.2f}'.format(scint_noise))
            print('Total noise [ppm]:            {:0.2f}'.format(tot_noise))
            print('')
            print('##### Noise ######')
            print('Noise in 1min [ppm]:          {:0.2f}'.format(tot_noise_in_1_min))
            print('Noise in 30min [ppm]:         {:0.2f}'.format(tot_noise_in_30_min))
            print('#####')

        return tot_noise, cadence

# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------

class TelescopeARC(Telescope):
    """
    Telescope class implementing the ARC 3.5m at Apache Point observatory for use with ARCTIC

    NOTES:
        Inherits Telescope()
        Can use this as a blueprint to create different classes that implement other telescopes
    """
    qe_file = Telescope.FILTER_DICT['arctic_qe.txt']
    def __init__(self):
        # Transmission / reflectivity of different elements to calculate throughput
        _e_diff         = 0.90 # transmission
        _e_lens         = 0.99*0.99*0.99*0.99
        _e_mirr         = 0.96*0.96
        _e_atmosphere   = 0.5 # fudgefactor for atmosphere, assume 50%
        _tot_throughput = _e_diff*_e_lens*_e_mirr*_e_atmosphere
        Telescope.__init__(self,
                           name='ARC 3.5m',          #Name of the telescope
                           diameter=350.,            #cm
                           fnum=8.0,                 #
                           flength=28.,              #m
                           gain=2.0,                 #e/ADU
                           pix_size=15.,             #microns
                           fov=8.,                   #arcmin, not really needed
                           num_pix=4096.,            #pixels on x-axis of detector
                           plt_scale=0.11,           #arcsec/pix
                           dark_noise=0.,            #electrons
                           read_noise=3.7,           #e^2
                           altitude=2788.,           #m
                           central_obstruction=0.09, # from 0 to 1
                           QE=S.FileBandpass(self.qe_file), 
                           Throughput=S.UniformTransmission(_tot_throughput),
                           diffuser_angle = 0.34,
                           diffuser_dist_from_detector = 200.)    # from 0 to 1

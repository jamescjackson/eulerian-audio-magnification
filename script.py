import sys
import optparse
import argparse
from scipy.io import wavfile
import numpy as np

import utils

from optparse import OptionParser



if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-s", type="float", dest="start_time", default=1)
    parser.add_option("-f", type="float", dest="end_time", default=16)
    (options, args) = parser.parse_args()

    if len(args)==0:
	    filename = "Queen_mono.wav"
    else:
	    filename = args[0]
    print options

    window = 1024
    step = window / 4

    (nyq, signal) = utils.slurp_wav(filename, int(options.start_time * 44100), int(44100 * options.end_time))
    print "computing spectrogram"
    spectrogram = utils.stft(signal)
    print "computing power"
    power = utils.estimate_spectral_power(spectrogram)

    print "whitening spectrum"
    whitened = spectrogram / np.sqrt(power)
    whitened = utils.normalize_total_power(whitened, utils.total_power(spectrogram))

    print "unwhitening spectrum"
    unwhitened = whitened * np.sqrt(power)
    unwhitened = utils.normalize_total_power(unwhitened, utils.total_power(spectrogram))

    print "resynthesizing from whitened-unwhitened spectrogram"
    resynth = utils.resynthesize(unwhitened)
    wavfile.write("resynth.wav", int(2 * nyq), resynth)

    print "constructing Laplacian pyramid"
    pyr = utils.stft_laplacian_pyramid(spectrogram)

    print "amplifying components of Laplacian pyramid"
    passband = [0.5, 1.0]
    fs = 44100 / step
    gain = 10.0
    amplified_pyr = utils.amplify_pyramid(pyr, passband=passband, fs=fs, gain=gain)

    print "resynthesizing spectrogram from amplified Laplacian pyramid"
    pyramid_resynth = utils.resynthesize(amplified_pyr.sum(axis=-1))
    wavfile.write("resynth_pyramid.wav", int(2 * nyq), pyramid_resynth)

#    print "computing remodulated whitened spectrogram"
#    gain = 5.0
#    passband = [0.1, 0.5]
#    remodulated_whitened_spectrogram = utils.amplify_modulation(
#        whitened, (2.0 * nyq / step), passband=passband, gain=gain)
#    print "unwhitening remodulated spectrum"
#    remodulated_spectrogram = remodulated_whitened_spectrogram * np.sqrt(power)
#    remodulated_spectrogram = utils.normalize_total_power(remodulated_spectrogram, utils.total_power(spectrogram))
#    print "resynthesizing from unwhitened remodulated spectrogram"
#    remodulated_resynth = utils.resynthesize(remodulated_spectrogram)
#    wavfile.write("resynth_remodulated.wav", int(2 * nyq), remodulated_resynth)

#    print "computing truncated whitened spectrogram after singular value decomposition"
#    k = [0]
#    #k = range(20)
#    #k = range(1024)
#    truncated_whitened_spectrogram = utils.svd_truncation(whitened, k=k)
#
#    print "unwhitening truncated spectrum"
#    truncated_spectrogram = truncated_whitened_spectrogram * np.sqrt(power)
#    truncated_spectrogram = utils.normalize_total_power(truncated_spectrogram, utils.total_power(spectrogram))
#
#    print "resynthesizing from unwhitened truncated spectrogram"
#    truncated_resynth = utils.resynthesize(truncated_spectrogram)
#    wavfile.write("resynth_truncated.wav", int(2 * nyq), truncated_resynth)



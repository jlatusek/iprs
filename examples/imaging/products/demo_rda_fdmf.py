#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-18 10:14:12
# @Author  : Yan Liu & Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$
import os
import iprs
import time
import numpy as np
import matplotlib.pyplot as plt

disk = 'mnt/d'
# disk = 'D:/'
rootfolder = '/DataSets/sar/'

ftshift = True
savemat = False
savetiff = True
mffdmod = 'way1'
usercmc = True
# usercmc = False

# downsampling
ratio = (0.5, 1.)
# ratio = (1., 0.5)
ratio = (0.5, 0.5)
# ratio = (1., 1.)
dsmethod = 'fillzeros'
dsmethod = 'throwaway'

nlooks = (1, 1)
isflipud = False
maxp, minp = (5e4, None)
sensor_name = 'ALOSPALSAR'
acquis_name = 'ALOSPALSAR'
fmt = '.mat'
filepath = 'ALPSRP050500980/ALPSRP050500980-L1.0/ALOS_PALSAR_RAW=IMG-HH-ALPSRP050500980-H1(sl=1el=35345)'
# filepath = 'ALPSRP273680670/ALPSRP273680670-L1.0/ALOS_PALSAR_RAW=IMG-HH-ALPSRP273680670-H1(sl=1el=35345)'

nlooks = (5, 1)
isflipud = True
maxp, minp = (1.8e4, None)
sensor_name = 'ERS'
acquis_name = 'ERS'
fmt = '.mat'
filepath = 'E2_81988_STD_F327/E2_81988_STD_L0_F327/ERS2_SAR_RAW=E2_81988_STD_L0_F327(sl=1el=28698)'


datafile = iprs.pathjoin(disk, rootfolder, sensor_name, fmt[1:], filepath + fmt)

sardata, sarplat = iprs.sarread(datafile)
sarplat.params = {'GeometryMode': 'SG'}

ROI = {
    'SubSceneArea': None,  # SceneArea
    # 'SubSceneArea': [0.5, 0.5, 0.5, 0.5],  # SceneArea/2.0
    'SubEchoAnchor': [0, 0],
    # 'SubEchoAnchor': [3000, 2000],  # Airport
    # 'SubEchoAnchor': [3000, 6000],  # Airport
    # 'SubEchoAnchor': [6000, 3000],  # Ships
    # 'SubEchoAnchor': [6000, 6000],
    # 'SubEchoAnchor': [5000, 5000],  # Ships
    # 'SubEchoAnchor': [3000, 0],  # Ships
    # 'SubEchoAnchor': [10000, 0],
    # 'SubEchoAnchor': [16300, 3000],
    # 'SubEchoSize': [35345, 10344],
    # 'SubEchoSize': [8192, 8192],
    # 'SubEchoSize': [32768, 8192],
    # 'SubEchoSize': [16384, 8192],
    # 'SubEchoSize': [8192, 4096],
    'SubEchoSize': [4096, 4096],
    # 'SubEchoSize': [4096, 1024],
    # 'SubEchoSize': [2048, 2048],
    # 'SubEchoSize': [1024, 1024],
    # 'SubEchoSize': [28698, 5616],
    # 'SubEchoSize': ES,
}

sarplat.params = None  # recompute parameters
sarplat.selection = ROI
sarplat.printsp()

SA = sarplat.acquisition['SceneArea']
SSA = sarplat.selection['SubSceneArea']
SSES = sarplat.selection['SubEchoSize']


cmap = 'jet'
extent = SSA

Fc = sarplat.sensor['Fc']
Tp = sarplat.sensor['Tp']
Wl = sarplat.sensor['Wl']
Br = sarplat.sensor['B']
La = sarplat.sensor['La']
Lr = sarplat.sensor['Lr']
Fs = sarplat.sensor['Fs']
Kr = sarplat.sensor['Kr']
Ar = sarplat.acquisition['Ar']

V = sarplat.sensor['V']
Vg = sarplat.sensor['Vg']
H = sarplat.sensor['H']
PRF = sarplat.sensor['PRF']
Ka = sarplat.params['Ka']
Rnear = sarplat.params['SubRnear']
Rfar = sarplat.params['SubRfar']
FPa = sarplat.params['SubFPa']
DA = sarplat.params['DA']
Nsar = sarplat.params['Nsar']
tr = sarplat.params['trSub']
ta = sarplat.params['taSub']
fr = sarplat.params['frSub']
fa = sarplat.params['faSub']

# Rnear = 850615['2240484538']
# V = 7176.

La = float(La)
Lr = float(Lr)
Vr = float(V)
Fsa = PRF
Fsr = Fs
Nfpa = round(FPa / DA)
BWa = 0.886 * Wl / La
Tpa = Rnear * BWa / Vg

ncpb = [Nfpa, 32]
# ncpb = [Na, Nr]

(sa, sr) = ROI['SubEchoAnchor']

ea, er = iprs.ebeo((sa, sr), SSES, '+')
print(sa, sr, ea, er)

(path, filename, ext) = iprs.fileparts(datafile)

Sr = sardata.rawdata
Sr = Sr[sa:ea, sr:er, :]
sardata = None
print("SAR raw data: ", Sr.shape, Sr.dtype)

print(Sr.min(), Sr.max())
Sr, Flag = iprs.iq_correction(Sr)
print(Flag)
# Sr, Flag = iprs.iq_correction(Sr)
# print(Flag)
print(Sr.min(), Sr.max())
print(np.mean(Sr))
print(Sr.shape, Sr.dtype)

Na, Nr, Nc = Sr.shape
print(Sr[0:10, 0:10])

Sr0 = iprs.dnsampling(Sr, ratio=ratio, axis=(0, 1), mod='uniform', method=dsmethod)
print(Sr[0:10, 0:10])
# if dsmethod is 'throwaway':
    # Fsa, Fsr = (Fsa * ratio[0], Fsr * ratio[1])
    # ta = iprs.dnsampling(ta, ratio=ratio[0], axis=0, mod='uniform', method=dsmethod)
    # tr = iprs.dnsampling(tr, ratio=ratio[1], axis=0, mod='uniform', method=dsmethod)
    # fa = iprs.dnsampling(fa, ratio=ratio[0], axis=0, mod='uniform', method=dsmethod)
    # fr = iprs.dnsampling(fr, ratio=ratio[1], axis=0, mod='uniform', method=dsmethod)

print(Na, Nr, Nc, "====")
Sr = iprs.upsampling(Sr0, shape=(Na, Nr, Nc), axis=-1, method='Lanczos')
print(Sr[0:10, 0:10])
print(Na, Nr, Nc, "====")

print(Sr.min(), Sr.max())
print(np.mean(Sr))
print(Sr.shape, Sr.dtype)

Sr = Sr[:, :, 0] + 1j * Sr[:, :, 1]

Na, Nr = Sr.shape
print("SAR raw data: ", Sr.shape, Sr.dtype)


Nh = round(Fsr * Tp)
N = int(Nr + Nh - 1)
Nfftr = 2**iprs.nextpow2(N)
# Nfftr = N
# Nfftr = Nr
print("Nfftr: ", Nfftr)

time_start = time.time()

# ===Range compression
Hr, _ = iprs.chirp_mf_fd(Kr, Tp, Fsr, Fc=0., Nfft=Nfftr, mod=mffdmod, win=None, ftshift=ftshift)
# Hr = Hr * np.kaiser(len(Hr), 2.)

Sr = iprs.fft(Sr, n=Nfftr, axis=1, norm=None, shift=ftshift)

# ---Estimate doppler centroid frequency
fadc, fbdc, Ma = iprs.dce_wda(Sr, Fsr, Fsa, Fc, ncpb=ncpb, tr=tr, isplot=False, isfftr=False)

for n in range(Na):
    Sr[n, :] = Sr[n, :] * Hr

Sr = iprs.ifft(Sr, n=Nfftr, axis=1, norm=None, shift=ftshift)

Sr = iprs.mfpc_throwaway(Sr, Nr, Nh, axis=1, mffdmod=mffdmod, ftshift=ftshift)


# print(fadc, fbdc, Ma)
fdc = iprs.fullfadc(fadc, [Na, Nr])
fdc = iprs.fullfadc(fbdc, [Na, Nr])
# fdc = np.zeros((Na, Nr))

Hc = np.exp(-2j * np.pi * fdc * np.reshape(ta.repeat(Nr), (Na, Nr)))
Sr = Sr * Hc

# ===Azimuth compression

Noff = np.linspace(0, Nr, Nr)
Rp = iprs.min_slant_range(Fsr, Noff, Rnear)

Nh = round(Fsa * Tpa)
N = int(Na + Nh - 1)
Nffta = 2**iprs.nextpow2(N)
# Nffta = N
# Nffta = Na

print(Sr.shape, Nffta)
Sr = iprs.fft(Sr, n=Nffta, axis=0, norm=None, shift=ftshift)
print(Sr.shape, Nffta)

fa = iprs.fftfreq(Fsa, n=Nffta, shift=ftshift, norm=False)

# ===RCMC
if usercmc:
    # D = np.sqrt(1.0 - (Wl * (fa * fdc) / (2.0 * Vr))**2)
    D = np.sqrt(1.0 - (Wl * (fa) / (2.0 * Vr))**2)
    Srrcmc = np.zeros((Nffta, Nr), dtype='complex64')
    for n in range(Nffta):
        Rrcmc = Rp / D[n]
        # Rrcmc = Rp / D[n, :]
        Srrcmc[n, :] = np.interp(Rrcmc, Rp, Sr[n, :])
    Sr = Srrcmc

# Rdc = Rp / np.sqrt(1.0 - (Wl * fdc / (2.0 * Vr))**2)
Rdc = Rp
Ka = (-2. * (Vr * np.cos(Ar))**2 / Wl) / Rdc
BWa = 0.886 * Wl / La
# Tpa = Rdc * BWa / Vg

for n in range(Nr):
    Ha, _ = iprs.chirp_mf_fd(Ka[n], Tpa, Fsa, Fc=0., Nfft=Nffta,
                             mod=mffdmod, win=None, ftshift=ftshift)
    # Ha = Ha * np.kaiser(len(Ha), 2.)

    Sr[:, n] = Sr[:, n] * Ha


Sr = iprs.ifft(Sr, n=Nffta, axis=0, norm=None, shift=ftshift)
Sr = iprs.mfpc_throwaway(Sr, Na, Nh, axis=0, mffdmod=mffdmod, ftshift=ftshift)


time_end = time.time()
print('time cost: ', time_end - time_start, 's')

if savemat:
    iprs.savemat('./out/' + filename + '.mat', {'Sr': Sr}, fmt='5')

Sr = np.abs(Sr)
SI = iprs.multilook_spatial(Sr, nlooks)

if isflipud:
    SI = np.flipud(SI)

SI = iprs.imadjust(SI, (minp, maxp), (0, 255))

# SI = iprs.imresize(SI, [8192, 8192])

SI = SI.astype('uint8')

if savetiff:
    iprs.imsave('./out/' + filename + 'Looks(' + str(nlooks) + ')' + 'FD.tiff', SI)
    # iprs.imsave('./data/image' + 'RDA_' + sensor_name + "_" + str(nlooks) + 'Looks_' +
    #             '(sa' + str(sa) + 'ea' + str(ea) + 'sr' + str(sr) + 'er' + str(er) + ')' + '.tiff', SI)

exit()

Title = 'Imaging Result of RDA'

Title = Title + '\n ('
if usercmc:
    Title = Title + 'RCMC+'
Title = Title + ")"

cmap = 'gray'
# cmap = 'hot'
# cmap = None

extent = SSA

plt.figure()
plt.subplot(211)
plt.imshow(np.abs(Sr), cmap=cmap)
plt.title("SAR raw data(Amplitude)")
plt.xlabel("Range")
plt.ylabel("Azimuth")
plt.subplot(212)
plt.imshow(SI, extent=extent, cmap=cmap)
# plt.imshow(SI, cmap=cmap)
plt.title(Title)
plt.tight_layout()
plt.show()

plt.figure()
plt.imshow(SI, extent=extent, cmap=cmap)
plt.xlabel("Range/m")
plt.ylabel("Azimuth/m")
plt.title(Title)
plt.show()

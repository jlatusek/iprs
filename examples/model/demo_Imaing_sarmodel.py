#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-26 23:34:49
# @Author  : Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$
import sys
import iprs
import numpy as np
import matplotlib.pyplot as plt


sensor_name = 'DIY7'  # 32x32
acquis_name = 'DIY9'  # 32x32

# sensor_name = 'DIY9'  # 32x32
# acquis_name = 'DIY10'  # 64x64

# sensor_name = 'DIY8'  # 32x32
# acquis_name = 'DIY8'  # 128x128



sensor_name = 'DIY7'  # 64x64
acquis_name = 'DIY10'  # 64x64

sensor_name = 'DIY9'  # 64x64
acquis_name = 'DIY8'  # 128x128

# sensor_name = 'DIY7'  # 128x128
# acquis_name = 'DIY8'  # 128x128

# sensor_name = 'DIY10'  # 128x128
# acquis_name = 'DIY10'  # 64x64


sarplat = iprs.SarPlat()
sarplat.name = "sensor=" + sensor_name + "_acquisition=" + acquis_name
sarplat.sensor = iprs.SENSORS[sensor_name]
sarplat.acquisition = iprs.ACQUISITION[acquis_name]
sarplat.params = None
sarplat.printsp()

Na = sarplat.params['Na']
Nr = sarplat.params['Nr']

c = 0.0001
isregen = False
isregen = True

# imgfilepath = '../data/fig/radarsat/Tokyoradarsat004_128.tif'
# imgfilepath = '../data/fig/radarsat/Tokyoradarsat004_256.tif'

# imgfilepath = '/mnt/d/DataSets/zhi/SAR/SIMSAR/SIMSAR/samples/'
imgfilepath = '../../data/img/points32.png'
imgfilepath = '../../data/img/pointsx32.png'
# imgfilepath = '../../data/img/ship32.png'
# imgfilepath = '../../data/img/Lotus32.png'
# imgfilepath = '../../data/img/000002AirPlane32.png'
# imgfilepath = '../../data/img/000003Ground32.png'
# imgfilepath = '../../data/img/points64.png'
imgfilepath = '../../data/img/pointsx64.png'
# imgfilepath = '../../data/img/ship64.png'
# imgfilepath = '../../data/img/Lotus64.png'
# imgfilepath = '../../data/img/000002AirPlane64.png'
# imgfilepath = '../../data/img/000003Ground64.png'
# imgfilepath = '../../data/img/Lotus128.png'
# imgfilepath = '../../data/img/points128.png'
imgfilepath = '../../data/img/pointsx128.png'
# imgfilepath = '../../data/img/ship128.png'
# imgfilepath = '../../data/img/000002AirPlane128.png'
# imgfilepath = '../../data/img/000003Ground128.png'

imgRGB = iprs.imread(imgfilepath)
print(type(imgRGB), imgRGB.shape)
if np.ndim(imgRGB) > 2:
    grayimg = imgRGB[:, :, 0]
else:
    grayimg = imgRGB
print("grayimg.shape: ", grayimg.shape)
[H, W] = grayimg.shape

bgv = 0
Ssim, targets = iprs.img2rawdata(
    sarplat, grayimg, bg=bgv, noise=None, TH=0, verbose=True)
iprs.show_amplitude_phase(Ssim)

print(Ssim.shape)

fileA = '../../data/model/' + 'sensor' + \
    sensor_name + "acquis" + acquis_name + '.pkl'

if isregen:
    A = iprs.sarmodel(sarplat, mod='2D1')
    AH = A.conj()
    AH = AH.transpose()

    N, L = A.shape
    print("---N, L, c", N, L, c)
    if N <= L:
        In = np.eye(N, dtype='complex128')
        invA = np.matmul(AH, np.linalg.inv(c * In + np.matmul(A, AH)))
    else:
        Il = np.eye(L, dtype='complex128')
        invA = np.matmul(np.linalg.inv(c * Il + np.matmul(AH, A)), AH)

    # invA = np.linalg.pinv(A)

    print("A.shape, invA.shape: ", A.shape, invA.shape)

    print("===saving mapping matrix...")
    iprs.save_sarmodel(A=A, invA=invA, datafile=fileA)

# ===load mapping matrix
print("===loading mapping matrix...")

A, invA = iprs.load_sarmodel(fileA, mod='AinvA')
print("A.shape, invA.shape: ", A.shape, invA.shape)


# ===========================for imaging tesing

SNR = 30
imgns = iprs.imnoise(grayimg, SNR=SNR)

img = imgns.flatten() / 255.0
# img = grayimg.flatten() / 255.0
print("img.shape: ", img.shape)

# ---------gen echo by s=Ag
Smodel = np.matmul(A, img)
print("Smodel.shape", Smodel.shape)
Smodel = np.reshape(Smodel, (Na, Nr))

# ---------reconstruct image by g=inv(A)*s
print("reconstruct image by g=inv(A)*s")

IpinvASsim = np.matmul(invA, Ssim.flatten())
IpinvASsim = np.reshape(IpinvASsim, (H, W))
print("IpinvASsim.shape:", IpinvASsim.shape)


IpinvASmodel = np.matmul(invA, Smodel.flatten())
IpinvASmodel = np.reshape(IpinvASmodel, (H, W))
print("IpinvASmodel.shape:", IpinvASmodel.shape)


# ---------reconstruct image by g=A^H*s
print("reconstruct image by g=A^H*s")
AH = A.conj()
AH = AH.transpose()
IAHSsim = np.matmul(AH, Ssim.flatten())
IAHSsim = np.reshape(IAHSsim, (H, W))
print("IAHSsim.shape: ", IAHSsim.shape)

IAHSmodel = np.matmul(AH, Smodel.flatten())
IAHSmodel = np.reshape(IAHSmodel, (H, W))
print("IAHSmodel.shape: ", IAHSmodel.shape)


# ================= show result

print("===imaging from echo signal simulated")
RDASsim = iprs.rda_adv(
    Ssim, sarplat, usezpa=True, usesrc=True, usermc=False, verbose=True)

# ----------------reconstruct image by range doppler
print("Smodel.shape", Smodel.shape)

print("===imaging from echo signal generated by: s=Ag")
# Smodel_img, ta, tr = iprs.rda(Smodel, sarplat, verbose=False)
RDASmodel = iprs.rda_adv(
    Smodel, sarplat, usezpa=True, usesrc=False, usermc=False, verbose=True)


# ===========================display diff

print("error: ||Smodel-Ssim||", np.linalg.norm(Smodel - Ssim, ord=2))
print("error: ||RDASmodel-RDASsim||", np.linalg.norm(RDASmodel - RDASsim, ord=2))
# print(Smodel, Ssim)

plt.figure()
plt.imshow(imgRGB)
plt.show()

plt.figure()
plt.subplot(321)
plt.imshow(np.abs(IpinvASsim))
plt.xlabel('Range')
plt.ylabel('Amplitude')
plt.title('g=A^+s, s:simulated')

plt.subplot(322)
plt.imshow(np.abs(IpinvASmodel))
plt.xlabel('Range')
plt.ylabel('Amplitude')
plt.title('g=A^+s, s=Ag')

plt.subplot(323)
plt.imshow(np.abs(IAHSsim))
plt.xlabel('Range')
plt.ylabel('Amplitude')
plt.title('g=A^Hs, s:simulated')

plt.subplot(324)
plt.imshow(np.abs(IAHSmodel))
plt.xlabel('Range')
plt.ylabel('Amplitude')
plt.title('g=A^Hs, s=Ag')

plt.subplot(325)
plt.imshow(np.abs(RDASsim))
plt.xlabel('Range')
plt.ylabel('Amplitude')
plt.title('RDA, s:simulated')

plt.subplot(326)
plt.imshow(np.abs(RDASmodel))
plt.xlabel('Range')
plt.ylabel('Amplitude')
plt.title('RDA, s=Ag')
plt.tight_layout()
plt.show()
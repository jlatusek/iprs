#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-03-13 11:06:13
# @Author  : Yan Liu & Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$

import sys
import iprs
import numpy as np
import matplotlib.pyplot as plt

# ===SA: 128x128, S: 32x32
sensor_name = 'DIY1'
acquis_name = 'DIY1'

sarplat = iprs.SarPlat()
sarplat.name = "sensor=" + sensor_name + "_acquisition=" + acquis_name
sensor = iprs.SENSORS[sensor_name]

PRF = sensor['PRF']
Tp = sensor['Tp']
Fsa = PRF
Tsa = 1.0 / PRF
Tsr = 5.1 * Tp
Na = 2
Nr = 1


sarplat.sensor = sensor
sarplat.acquisition = iprs.ACQUISITION[acquis_name]
sarplat.params = {
    "GeometryMode": "SG",
    "Fsr": 32.317e6,
    "Fsa": Fsa,
    "Tsa": Tsa,
    "Tsr": Tsr,
    "Na": Na,
    "Nr": Nr,
    "Rnear": 1,
    "Rfar": 1,
    "FPr": 1,
    "Lsar": 1,
    "FPa": 1,
}
sarplat.selection = None
sarplat.printsp()


isregen = False
# isregen = True

cmap = 'gray'
cmap = None
cmap = 'jet'

imgfilepath = '../../../data/img/points32.png'
# imgfilepath = '../../../data/img/Lotus32.png'
# imgfilepath = '../../../data/img/ship32.png'
# imgfilepath = '../../../data/img/Lotus128.png'
# imgfilepath = '../../../data/img/ship128.png'
# imgfilepath = '../../../data/img/points128.png'
imgfilepath = '../../../data/img/000043.png'
imgfilepath = '../../../data/img/000010.png'
imgfilepath = '../../../data/img/000237.png'
imgfilepath = '../../../data/img/000066.png'


optim = 'Lasso'
norm = 1

# optim = 'OMP'
# norm = 0

imgRGB = iprs.imread(imgfilepath)

grayimg = imgRGB
# grayimg = imgRGB[:, :, 0]
SNR = 30
imgns = iprs.imnoise(grayimg, SNR=SNR)
img = iprs.scale(grayimg, [0.0, 255.0], [0.0, 1.0])
print("img.shape: ", img.shape)
H, W = img.shape
# gdshape = (H * 2, W * 2)
gdshape = (H, W)

bgv = 0
Ssim, targets = iprs.img2rawdata(
    sarplat, grayimg, bg=bgv, noise=None, TH=0, verbose=True)
iprs.show_amplitude_phase(Ssim)
plt.show()

print(Ssim.shape)

fileA = '../../../data/model/' + 'sensor' + \
    sensor_name + "acquis" + acquis_name + '.pkl'

if isregen:
    A = iprs.sarmodel(sarplat, mod='2D1')
    invA = np.linalg.pinv(A)

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

# img = imgns.flatten() / 255.0
img = grayimg.flatten() / 255.0
print("img.shape: ", img.shape)

# ---------gen echo by s=Ag
Smodel = np.matmul(A, img)
print("Smodel.shape", Smodel.shape)
Smodel = np.reshape(Smodel, (Na, Nr))

# ---------reconstruct image by regularization l1
print("reconstruct image by " + optim)
ICS_Ssim = iprs.cs1d_sar(s=Ssim, A=A, D=None, axis=-1, norm=norm, factor=0.1,
                             optim=optim, max_iter=1000, tol=0.00001, gdshape=gdshape, verbose=True)

ICS_Smodel = iprs.cs1d_sar(s=Smodel, A=A, D=None, axis=-1, norm=norm, factor=0.1,
                               optim=optim, max_iter=1000, tol=0.00001, gdshape=gdshape, verbose=True)

Dict = 'DCT'
D = iprs.dctdic((H * W, H * W), axis=-1, isnorm=True)
# Dict = 'I'
# D = np.eye(H * W)

# plt.figure()
# plt.imshow(D)
# plt.title('Dictionary: ' + Dict)
# plt.show()

ICS_DICT_Ssim = iprs.cs1d_sar(s=Ssim, A=A, D=D, axis=-1, norm=norm, factor=0.1,
                                  optim=optim, max_iter=1000, tol=0.00001, gdshape=gdshape, verbose=True)

ICS_DICT_Smodel = iprs.cs1d_sar(s=Smodel, A=A, D=D, axis=-1, norm=norm, factor=0.1,
                                    optim=optim, max_iter=1000, tol=0.00001, gdshape=gdshape, verbose=True)


# ----------------reconstruct image by range doppler
print("reconstruct image by RDA(simulated)")
RDASsim = iprs.rda_adv(
    Ssim, sarplat, usezpa=True, usesrc=True, usermc=False, verbose=True)

print("reconstruct image by RDA(model)")
RDASmodel = iprs.rda_adv(
    Smodel, sarplat, usezpa=True, usesrc=False, usermc=False, verbose=True)

# ===========================display diff

print("error: ||Smodel-Ssim||", np.linalg.norm(Smodel - Ssim, ord=2))
print("error: ||RDASmodel-RDASsim||",
      np.linalg.norm(RDASmodel - RDASsim, ord=2))


plt.figure()
plt.subplot(321)
plt.imshow(np.abs(ICS_Ssim), cmap=cmap)
plt.xlabel('Range')
plt.ylabel('Amplitude')
plt.title('CS-' + optim + ', ' + 'Dict: ' + 'None, ' + 's:simulated')

plt.subplot(322)
plt.imshow(np.abs(ICS_Smodel), cmap=cmap)
plt.xlabel('Range')
plt.ylabel('Amplitude')
plt.title('CS-' + optim + ', ' + 'Dict: ' + 'None, ' + ' s=Ag')

plt.subplot(323)
plt.imshow(np.abs(ICS_DICT_Ssim), cmap=cmap)
plt.xlabel('Range')
plt.ylabel('Amplitude')
plt.title('CS-' + optim + ', ' + 'Dict: ' + Dict + ', s:simulated')

plt.subplot(324)
plt.imshow(np.abs(ICS_DICT_Smodel), cmap=cmap)
plt.xlabel('Range')
plt.ylabel('Amplitude')
plt.title('CS-' + optim + ', ' + 'Dict: ' + Dict + ', s=Ag')

plt.subplot(325)
plt.imshow(np.abs(RDASsim), cmap=cmap)
plt.xlabel('Range')
plt.ylabel('Amplitude')
plt.title('RDA, s:simulated')

plt.subplot(326)
plt.imshow(np.abs(RDASmodel), cmap=cmap)
plt.xlabel('Range')
plt.ylabel('Amplitude')
plt.title('RDA, s=Ag')
plt.tight_layout()
plt.show()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-02-18 10:14:12
# @Author  : Yan Liu & Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$

import iprs
import numpy as np

sensor_name = 'RADARSAT1'
acquis_name = 'RADARSAT1'
#sensor_name = 'SIMSARv1a'
#acquis_name = 'SIMSARv1a'
#sensor_name = 'DIY1'
#acquis_name = 'DIY1'

sarplat = iprs.SarPlat()
sarplat.name = "sensor=" + sensor_name + "_acquisition=" + acquis_name
sarplat.sensor = iprs.SENSORS[sensor_name]
sarplat.acquisition = iprs.ACQUISITION[acquis_name]
sarplat.params = {'GeometryMode': 'SG'}
sarplat.params = None
sarplat.selection = None
sarplat.printsp()

SC = sarplat.acquisition['SceneCenter']
Xc = SC[0]
Yc = SC[1]
SA = sarplat.acquisition['SceneArea']

datasetname = 'point'
outfolder = '../../data/sar/point/'

imagingMethod = 'RangeDoppler'
# imagingMethod = 'OmegaK'
# imagingMethod = 'ChirpScaling'

# targets = [
#     [100, 100, 0, 0, 0, 0, 1],
#     [-110, -50, 0, 0, 0, 0, 1],
#     [0, 0, 0, 0, 0, 0, 1],
#     [100, 0, 0, 0, 0, 0, 1],
#     [120, -20, 0, 0, 0, 0, 1],
# ]

targets = [
    [0, 0, 0, 0, 0, 0, 1],
    [0, 60, 0, 0, 0, 0, 1],
    [100, 0, 0, 0, 0, 0, 1],

]

# targets = []
# for i in range(10):
#     targets.append([i, i, 0, 0, 0, 0, 1])


imgshape = (128, 128)
#imgshape = (SA[3] - SA[2], SA[1] - SA[0])

SS = [int(SA[3] - SA[1]), int(SA[1] - SA[0])]
imgshape = SS


SrI = iprs.show_targets(targets, SA, imgshape)

Sr, ta, tr = iprs.tgs2rawdata(sarplat, targets, verbose=True)

print(Sr.shape)
# visualize
#iprs.show_amplitude_phase(Sr)

# store
sardata = iprs.SarData()
sardata.name = datasetname
sardata.rawdata = Sr
sardata.image = SrI

# outfilename_prefix = outfolder + sarplat.name + \
#     "_" + datasetname + str(len(targets))

# outfile = outfilename_prefix + '.pkl'

# iprs.sarstore(sardata, sarplat, outfile)
# sardata, sarplat = iprs.sarread(outfile)

# --------------------------------------------
# do RD imaging
verbose = True
verbose = False

#ftshift = True
ftshift = False
#zpadar = (256, 256)
zpadar = False
zpadar = True
# zpadar = None
usesrc = True
# usesrc = False
usedpc = True
# usedpc = False
rcmc = False
rcmc = 4

if imagingMethod is 'RangeDoppler':
    # do RD imaging
    # SrIr = iprs.rda_adv(Sr, sarplat, zpadar=zpadar,
    #                     usesrc=usesrc, usedpc=usedpc, rcmc=rcmc, verbose=verbose)
    SrIr = iprs.rda(Sr, sarplat, zpadar=zpadar, rcmc=rcmc, verbose=verbose)
elif imagingMethod is 'OmegaK':
    SrIr, ta, tr = iprs.wka(Sr, sarplat, verbose=verbose)
elif imagingMethod is 'ChirpScaling':
    SrIr = iprs.csa(Sr, sarplat, verbose=verbose)

print("==", np.sum(SrIr))


axismod = 'Image'
# axismod = 'SceneAbsolute'
axismod = 'SceneRelative'
title = 'Reconstructed Image using ' + imagingMethod
# title = 'Reconstructed Image using omega-k'
iprs.show_sarimage(SrIr, sarplat, axismod=axismod, title=title, aspect=None)

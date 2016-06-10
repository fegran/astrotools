from __future__ import division
import matplotlib.pyplot as plt
from astropy.io import ascii
import numpy as np
import warnings
import sys
import os

if len(sys.argv) < 2:
    os.system('clear')
    print '\n'
    print 'How to run this script:\t python %s info_file.dat' %sys.argv[0]
    print 'Output of this script:\t info_file.sel'
    print '\n'
    sys.exit(True)

#################################
#          USER   INPUT
info_file = sys.argv[1]
#################################

if '.sel' in info_file:
    os.system('clear')
    print 'Archivo info no valido: ".sel"'
    print 'Cambiar nombre o archivo'
    sys.exit(True)

out_file = info_file[:info_file.find('.')]+'.sel'
warnings.filterwarnings('ignore')
if os.path.exists(out_file):
    os.system('rm %s' %out_file)

def phaser(mjd, P):
    return (mjd / P) % 1

def plotter(i, ids, P1, P2, P3):

    mjd, mag, err = np.genfromtxt('%d.dat' %ids, usecols=(0,1,2), unpack=True)
    mean = np.average(mag, weights=1/err**2)
    amp = np.abs(np.min(mag)-np.max(mag))

    plt.figure(figsize=(8,6))
    for j, P in enumerate([P1, P2, P3, 1]):
        phase = phaser(mjd,P)
        plt.subplot(2,2,j+1)
        plt.suptitle(r'ID: $%d$' %ids, size=16)
        plt.gca().invert_yaxis()
        if P != 1.:
            plt.title(r'$P_{%d} = %3.3f$' %(j+1,P) )
            plt.xlabel('Phase')
            plt.errorbar(phase,mag,err,fmt='ko',alpha=0.5)
            plt.errorbar(phase+1,mag,err,fmt='ko',alpha=0.5)
            plt.xlim(-0.1,2.1)
        else:
            mjd_0 = np.round(mjd[0] / 50) * 50
            plt.errorbar(mjd-mjd_0,mag,err,fmt='ko',alpha=0.5)
            plt.xlabel('MJD - %d' %mjd_0)
            plt.xlim(np.min(mjd)-mjd_0-100, np.max(mjd)-mjd_0+100)
            plt.title(r'$\langle K_{\rm s} \rangle = %1.2f \quad \Delta K_{\rm s} = %1.2f$' %(mean, amp))
        if j in (0,2):
            plt.ylabel(r'$K_{\rm s}$', size=16)

    plt.tight_layout()
    plt.draw()
    plt.show(block=False)
    return

ids, P1, P2, P3 = np.genfromtxt(info_file, usecols=(0,12,13,14), unpack=True)
final_election = np.zeros_like(ids).astype(int)

i = 0
while True:

    if i >= len(ids):
        break

    plotter(i, ids[i], P1[i], P2[i], P3[i])

    election = 'VVV'
    while election not in ['s', '', 'p', 'q']:
        election = raw_input('Eleccion para esta curva %d/%d: (s) save, (ENTER) next, (p) previous, (q) quit: \n' %(i+1,len(ids)))

    if election == 's':
        final_election[i] = 1
        plt.savefig('%d.pdf' %ids[i], format='ps')
        i = i + 1
        plt.close()
    if election == '':
        final_election[i] = 0
        i = i + 1
        plt.close()
    if election == 'p':
        plt.close()
        if i == 0:
            print 'No puedes retroceder de la posicion 1!!'
            continue
        i = i - 1
        continue
    if election == 'q':
        print '-'*40
        print '*'*40
        print 'Ultimo ID con eleccion valida : %d' %ids[i-1]
        print '*'*40
        print '-'*40
        break

if np.sum(final_election) != 0:
    data = ascii.read(info_file)
    data = data[final_election.astype(bool)]
    ascii.write(data, out_file, delimiter=' ', format='fixed_width', formats={'%7.0f','%8.8f','%8.8f','%5.2f','%6.4f','%5.3f','%8.2f','%8.2f','%7.4f','%7.4f','%7.4f','%7.4f','%11.6f','%11.6f','%11.6f','%11.6f','%5.0f','%5.0f'})
    os.system('sed -i "" "s/ID/%sID/g" %s' %('#',out_file))

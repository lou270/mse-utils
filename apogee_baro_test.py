###############################
# Project       : MSE Avionics
# Description   : Apogee barometer algorithm test
# Licence       : CC BY-NC-SA 
# Author        : Louis Barbier
# https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode
##############################

import csv
import math
import random
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicSpline

def pression_atmospherique(altitude):
    P0 = 1013.25  # Pression standard au niveau de la mer en hPa
    L = 0.0065   # Gradient de température adiabatique en K/m
    T0 = 288.15  # Température standard au niveau de la mer en K
    g = 9.81     # Accélération due à la gravité en m/s²
    M = 0.029    # Masse molaire de l'air sec en kg/mol
    R = 8.314    # Constante des gaz en J/(mol·K)

    exponent = (-g * M * altitude) / (R * T0)
    pressure = P0 * math.pow(1 - (L * altitude / T0), (g * M) / (R * L))

    return pressure

# baro_filename = './mse-utils/MS0_baro_data.txt'
baro_filename = './mse-utils/Kriptonit_baro_simulated.txt'

time = []
baro_raw = []

with open(baro_filename, 'r') as fp:
    csvreader = csv.reader(fp, delimiter=';')
    for line in csvreader:
        if (len(time) > 0):
            if (float(line[0]) != time[-1]):
                time.append(float(line[0]))
                baro_raw.append(float(line[1]))
        else:
            time.append(float(line[0]))
            baro_raw.append(float(line[1]))

# with open('test.txt', 'w') as fp:
#     for bar in baro_raw:
#         true_baro = 1013.25*(1-(bar/44307.694))**5.25530
#         fp.write("{:3f}\n".format(true_baro))

# exit()

time_ms = np.array(list(map(lambda x: x*1000, time)))
baro = np.array(list(map(lambda x: x, baro_raw)))
print(len(baro))

time_target_ms = list(range(0, 17000, int(1000.0/75.0)))
coefficients = np.polyfit(time_ms, baro, 2)
f = np.poly1d(coefficients) 
baro_interp = list(map(lambda x: f(x)+random.uniform(-0.05,0.05), time_target_ms))
print(len(baro_interp))

apogee_time = time_target_ms[baro_interp.index(min(baro_interp))]
print("Apogee: {:.2f} ms".format(apogee_time))

baro_interp_mean = []
time_target_ms_mean = []
mean_nb = 8
for i in range(0, len(baro_interp), mean_nb):
    list_tmp = baro_interp[i:i + mean_nb]
    mean_list = sum(list_tmp) / len(list_tmp)
    time_target_ms_mean.append(time_target_ms[i])
    baro_interp_mean.append(mean_list)

# print(len(time_ms))
# print(len(time_target_ms_mean))

ind_apogee_mean = time_target_ms_mean[baro_interp_mean.index(min(baro_interp_mean))]

ind_1s5 = time_target_ms_mean.index(min(time_target_ms_mean, key=lambda x:abs(x-apogee_time+1500)))
ind_2s = time_target_ms_mean.index(min(time_target_ms_mean, key=lambda x:abs(x-apogee_time+2000)))
ind_2s5 = time_target_ms_mean.index(min(time_target_ms_mean, key=lambda x:abs(x-apogee_time+2500)))

print(ind_1s5)
print(ind_2s)
print(ind_2s5)

deriv_baro_interp = []
first = True
for i in range(len(time_target_ms_mean)-1):
    deriv_baro_interp.append((baro_interp_mean[i+1] - baro_interp_mean[i])/(time_target_ms_mean[i+1] - time_target_ms_mean[i]))
    if first:
        if (deriv_baro_interp[-1] > -0.0015):
            first = False
            ind_declanchement = i-1
# Display
fig_1 = plt.figure(figsize=(1, 1))

ax1 = plt.subplot(1, 1, 1)
ax1.plot(time_ms, baro, label='Raw')
ax1.plot(time_target_ms, baro_interp, label='Interpolate')
ax1.axvline(x=apogee_time, color='black', linestyle='-.')
ax1.set_xlabel('Time [ms]')
ax1.set_ylabel('Pressure [mBar]')
ax1.set_title('Barometer pressure', fontsize=16, fontweight='bold', color='blue')
plt.legend()

ax2 = ax1.twinx()

ax2.plot(time_target_ms_mean[:-1], deriv_baro_interp, label='Derivate')
ax2.axvline(x=time_target_ms_mean[ind_declanchement], color='r', linestyle='--')
ax2.axhline(y=deriv_baro_interp[ind_declanchement], color='red', linestyle='--')
ax2.text(time_target_ms_mean[ind_declanchement], max(deriv_baro_interp), "Firing", ha='center', va='bottom')
ax2.text(max(time_target_ms_mean), deriv_baro_interp[ind_declanchement], "Firing", ha='center', va='bottom')

ax2.axvline(x=time_target_ms_mean[ind_1s5], color='g', linestyle=':')
ax2.text(time_target_ms_mean[ind_1s5], min(deriv_baro_interp), "1.5s", ha='center', va='bottom')
ax2.axvline(x=time_target_ms_mean[ind_2s], color='g', linestyle=':')
ax2.text(time_target_ms_mean[ind_2s], min(deriv_baro_interp), "2s", ha='center', va='bottom')
ax2.axvline(x=time_target_ms_mean[ind_2s5], color='g', linestyle=':')
ax2.text(time_target_ms_mean[ind_2s5], min(deriv_baro_interp), "2,5s", ha='center', va='bottom')
ax2.set_ylabel('Pressure derivate [mBar/s]')
plt.legend()

plt.tight_layout()
plt.show()


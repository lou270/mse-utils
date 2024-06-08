###############################
# Project       : MSE Avionics
# Description   : LittleFS utils functions for Pico board
# Author        : Louis Barbier
# Licence       : CC BY-NC-SA 
# https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode
##############################
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import struct
import csv
import subprocess
import time
import os
import re
import sys
import shutil

# Extract filesystem from Pico board
def extract_fs_from_pico():
    canvas1.itemconfig(cercle1, fill="red")
    # Reboot Pico in bootsel mode
    exec_cmd("picotool reboot -u -f") #TODO Add bus / address
    time.sleep(2)

    # Save FS from Pico flash
    create_dir("raw_fs/")
    fs_filename = get_new_name("raw_fs/", "fs_")
    exec_cmd("picotool save -r 100FF000 10FFF000 raw_fs/"+fs_filename+".bin")

    # Extract FS from Pico flash binary file
    extracted_fs_path = os.path.abspath("extracted_fs/"+fs_filename)
    if(os.path.exists(extracted_fs_path)):
        shutil.rmtree(extracted_fs_path)
    exec_cmd("littlefs_extract -b 4096 -c 3840 -i raw_fs/"+fs_filename+".bin -d "+extracted_fs_path)

    # Open extracted FS folder
    if sys.platform.startswith('win'):
        # Windows
        subprocess.Popen(f'explorer {extracted_fs_path}')
    elif sys.platform.startswith('linux'):
        # Linux
        subprocess.Popen(f'xdg-open {extracted_fs_path}')
    
    canvas1.itemconfig(cercle1, fill="green")

def get_new_name(folder, basename):
    max_cnt = -1
    files = os.listdir(os.path.abspath(folder))
    for file in files:
        file = file.split(".")[0]
        if file.startswith(basename):
            cnt_file = file.split("_")[-1]
            try:
                cnt = int(cnt_file)
                max_cnt = max(max_cnt, cnt)
            except ValueError:
                pass
    return basename+str(max_cnt+1)

def create_dir(folder):
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except OSError as e:
            print(f"Erreur lors de la création du dossier : {e}")

def exec_cmd(commande):
    try:
        subprocess.run(commande, shell=True, check=True)
        # process = subprocess.Popen(commande, stdout=subprocess.STDOUT, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande : {e}")
        messagebox.showerror("Erreur", f"Command execution error:\n{e}")

# Extract filesystem from Pico board
def extract_rocketdata_from_file():
    canvas2.itemconfig(cercle2, fill="red")
    file = filedialog.askopenfilename(initialdir="./")
    if not file:
        print("Error: No file selected !")
        messagebox.showerror("Error", f"No file selected")
        return -1
    
    # Définir le format de la structure C
    # format_structure = '<Qiiiihhhhhhhhh'
    format_structure = '<Qiiihhhhhhhhhh'
    byte_number = struct.calcsize(format_structure)

    # Lire les données binaires à partir du fichier
    output_data = []
    with open(file, 'rb') as fp:
        while True:
            bin_data = fp.read(byte_number)
            if not bin_data or len(bin_data) < byte_number :
                break
            
            # Extraire les données binaires en utilisant le format de la structure
            donnees_extraites = struct.unpack(format_structure, bin_data)

            # Assigner les valeurs extraites aux variables correspondantes
            rocketSts, gnssLat, gnssLon, pressure, gnssAlt, temperature, accX, accY, accZ, gyrX, gyrY, gyrZ, sensorAdc0, sensorAdc1 = donnees_extraites

            # Retourner les données extraites sous forme de dictionnaire
            donnees = {
                'rocketSts': rocketSts,
                'gnssLat': gnssLat,
                'gnssLon': gnssLon,
                'gnssAlt': gnssAlt,
                'pressure': pressure,
                'temperature': temperature,
                'accX': accX,
                'accY': accY,
                'accZ': accZ,
                'gyrX': gyrX,
                'gyrY': gyrY,
                'gyrZ': gyrZ,
                'sensorAdc0': sensorAdc0,
                'sensorAdc1': sensorAdc1
            }

            decoded_data = decode_data(donnees)

            output_data.append(decoded_data)

    create_dir("out_data")
    exporter_csv("out_data/test1.csv", output_data)
    canvas2.itemconfig(cercle2, fill="green")
    return output_data

def decode_data(data):
    decoded_data = []
    time = data['rocketSts'] >> 8 & 0xFFFFFFFFFFFFFF
    sts = data['rocketSts'] & 0xFF
    gnssLat = data['gnssLat']*1e-7
    gnssLon = data['gnssLon']*1e-7
    gnssAlt = data['gnssAlt']*1.0/1000
    pressure = data['pressure'] # TODO
    temperature = data['temperature'] # TODO
    accX = data['accX'] # TODO
    accY = data['accY'] # TODO
    accZ = data['accZ'] # TODO
    gyrX = data['gyrX'] # TODO
    gyrY = data['gyrY'] # TODO
    gyrZ = data['gyrZ'] # TODO
    sensorAdc0 = data['sensorAdc0'] # TODO
    sensorAdc1 = data['sensorAdc1'] # TODO

    decoded_data.append(time)
    decoded_data.append(sts)
    decoded_data.append(gnssLat)
    decoded_data.append(gnssLon)
    decoded_data.append(gnssAlt)
    decoded_data.append(pressure)
    decoded_data.append(temperature)
    decoded_data.append(accX)
    decoded_data.append(accY)
    decoded_data.append(accZ)
    decoded_data.append(gyrX)
    decoded_data.append(gyrY)
    decoded_data.append(gyrZ)
    decoded_data.append(sensorAdc0)
    decoded_data.append(sensorAdc1)

    return decoded_data

def exporter_csv(fichier_csv, donnees):
    entetes = ["Time", "sts", "gnssLat", "gnssLon", "gnssAlt", "pressure", "temperature", "accX", "accY", "accZ", "gyrX", "gyrY", "gyrZ", "sensorAdc0", "sensorAdc1"]

    with open(fichier_csv, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(entetes)
        writer.writerows(donnees)

    print("Exportation CSV terminée.")

# Create window
fenetre = tk.Tk()
fenetre.geometry("300x100")
fenetre.title("Pico utils")
fenetre.iconbitmap(default="pico.ico")

fenetre.columnconfigure(0, weight=1)
fenetre.rowconfigure(0, weight=1)
fenetre.rowconfigure(1, weight=1)

frame_boutons = tk.Frame(fenetre)
frame_boutons.grid(row=0, column=0, padx=5)

frame_cercles = tk.Frame(fenetre)
frame_cercles.grid(row=0, column=1, padx=5)

# Create buttons
bt_extract_fs = tk.Button(frame_boutons, text="Extract FS from Pico", command=extract_fs_from_pico)
bt_extract_fs.grid(row=0, column=0, sticky="ew", pady=5)
bt_extract_data = tk.Button(frame_boutons, text="Extract Rocket data from file", command=extract_rocketdata_from_file)
bt_extract_data.grid(row=1, column=0, sticky="ew", pady=5)

# # Créer une barre de progression
# progress_bar = ttk.Progressbar(fenetre, length=200)
# progress_bar.pack(pady=10)
# progress_bar.step(0)

# percentCmd = tk.StringVar()
# percentCmd.set("0%")
# label_pourcentage = tk.Label(fenetre, textvariable=percentCmd)
# label_pourcentage.pack()


canvas1 = tk.Canvas(frame_cercles, width=40, height=40)
cercle1 = canvas1.create_oval(10, 10, 30, 30, fill="red")
canvas1.grid(row=0, column=0)

canvas2 = tk.Canvas(frame_cercles, width=40, height=40)
cercle2 = canvas2.create_oval(10, 10, 30, 30, fill="red")
canvas2.grid(row=1, column=0)

# Lancer la boucle principale de l'interface
fenetre.mainloop()


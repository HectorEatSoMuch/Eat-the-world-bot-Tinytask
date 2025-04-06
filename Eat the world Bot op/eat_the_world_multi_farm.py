import os
base_dir = os.path.dirname(__file__)
import time
import random
import pyautogui  # Pour F6 uniquement
from pynput.keyboard import Controller
import signal
import sys
import subprocess
from datetime import datetime, timedelta

# Chemins des fichiers
AUTOCICK_PATH = os.path.join(base_dir, "Autoclick_statue.txt")
CHEST_PATH = os.path.join(base_dir, "Chest_statue.txt")

# Création d'un objet pour contrôler le clavier avec pynput
keyboard = Controller()

# Liste pour suivre les touches utilisées
key_order = ['z', 's', 'q', 'd']
used_keys = []  # Historique des touches pressées

def get_next_key():
    """Retourne la prochaine touche à presser en suivant l'ordre défini."""
    global used_keys
    
    # Filtrer les touches restantes
    remaining_keys = [key for key in key_order if key not in used_keys]

    # Si toutes les touches ont été utilisées, on reset
    if not remaining_keys:
        used_keys = []
        remaining_keys = key_order.copy()

    # Prendre la première touche disponible et l'ajouter à l'historique
    next_key = remaining_keys[0]
    used_keys.append(next_key)
    return next_key

def press_key_random():
    """Simuler la pression de la touche 'o' et d'une touche définie par l'ordre pendant 2 secondes."""
    random_key = get_next_key()  # Obtenir la touche selon l'ordre
    
    keyboard.press('o')
    keyboard.press(random_key)
    time.sleep(1)  # Maintien pendant 2 secondes
    keyboard.release('o')
    keyboard.release(random_key)

def simulate_click(key):
    """Simuler un clic sur la touche F6 avec pyautogui."""
    pyautogui.press(key)

def write_to_file(file_path, value):
    """Écrire une valeur dans un fichier texte."""
    with open(file_path, "w") as file:
        file.write(str(value))

def wait_for_pixel(x, y, color, timeout=60):
    """Attendre qu'un pixel ait une certaine couleur pendant un temps donné."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_color = pyautogui.pixel(x, y)
        if current_color == color:
            return True
        time.sleep(0.1)  
    return False  

def wait_for_pixel_without_block(x, y, color):
    """Attendre que le pixel ait une certaine couleur sans blocage de 60s."""
    while True:
        current_color = pyautogui.pixel(x, y)
        if current_color != color:
            break

        print("[INFO] Pixel détecté, relancement de la vente...")
        process_vente = execute_macro(os.path.join(base_dir, "macro_vente.exe"))
        wait_for_process_to_end(process_vente)

def execute_macro(file_path):
    """Exécuter un fichier macro .exe et retourner le processus."""
    return subprocess.Popen(file_path, shell=True)

def wait_for_process_to_end(process):
    """Attendre la fin d'un processus."""
    process.wait()

def on_exit(signal, frame):
    """Fonction appelée lors de l'arrêt du script."""
    global autoclick
    if autoclick == 1:
        simulate_click("f6")
    write_to_file(AUTOCICK_PATH, 0)
    write_to_file(CHEST_PATH, 0)
    sys.exit(0)

def main():
    global autoclick, used_keys
    autoclick = 0
    used_keys = []  # Réinitialisation de l'historique des touches
    write_to_file(AUTOCICK_PATH, autoclick)
    write_to_file(CHEST_PATH, 0)

    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)

    while True:
        write_to_file(CHEST_PATH, 0)
        end_time = datetime.now() + timedelta(hours=1, minutes=30)

        while datetime.now() < end_time:
            print("[INFO] Lancement de macro_debut.exe")
            process_debut = execute_macro(os.path.join(base_dir, "macro_debut.exe"))
            wait_for_process_to_end(process_debut)
            print("[INFO] Fin de macro_debut.exe")
            process_debut = execute_macro(os.path.join(base_dir, "échap.exe"))

            simulate_click("f6")  
            autoclick = 1
            write_to_file(AUTOCICK_PATH, autoclick)

            print("[INFO] Attente du pixel...")

            start_wait_time = time.time()
            while not wait_for_pixel(1722, 954, (60, 141, 38)):
                elapsed_time = time.time() - start_wait_time
                if elapsed_time >= 60:
                    print("[WARNING] Pixel toujours incorrect après 1 minute, tentative de déblocage...")
                    simulate_click("f6")
                    
                    press_key_random()  # Appuie sur 'o' + une touche selon l'ordre défini
                    time.sleep(2)
                    simulate_click("f6")
                    start_wait_time = time.time()

                print("[INFO] Pixel incorrect, en attente...")
                time.sleep(1)

            print("[SUCCESS] Pixel détecté, clic sur F6")
            simulate_click("f6")
            autoclick = 0
            write_to_file(AUTOCICK_PATH, autoclick)

            wait_for_pixel_without_block(1722, 954, (60, 141, 38))

            # Réinitialisation des touches après macro_vente
            used_keys = []

        # Une fois les 1h30 passées :
        if autoclick == 1:
            simulate_click("f6")
            autoclick = 0
            write_to_file(AUTOCICK_PATH, autoclick)

        print("[INFO] Fin des 1h30, lancement des macros supplémentaires...")

        print("[INFO] Lancement de macro_periodique1.exe")
        process_periodique = execute_macro(os.path.join(base_dir, "macro_periodique1.exe"))
        wait_for_process_to_end(process_periodique)
        print("[INFO] Fin de macro_periodique1.exe")

        write_to_file(CHEST_PATH, 1)

        print("[INFO] Lancement de macro_achat_multi.exe")
        process_achat_multi = execute_macro(os.path.join(base_dir, "macro_achat_muti.exe"))
        wait_for_process_to_end(process_achat_multi)
        print("[INFO] Fin de macro_achat_multi.exe")

        write_to_file(CHEST_PATH, 0)

if __name__ == "__main__":
    main()

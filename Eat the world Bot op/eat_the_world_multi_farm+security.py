import subprocess
import time
import keyboard
import os
import pyautogui
import psutil

pyautogui.FAILSAFE = False

# Chemins des fichiers utilisés
EAT_WORLD_SCRIPT = r"C:\Users\camil\Desktop\Eat the world Bot op\eat_the_world_multi_farm.py"
AUTOCLICK_STATUS_FILE = r"C:\Users\camil\Desktop\Eat the world Bot op\Autoclick_statue.txt"
CHEST_STATUS_FILE = r"C:\Users\camil\Desktop\Eat the world Bot op\Chest_statue.txt"
CHROME_URL_MACRO = r"C:\Users\camil\Desktop\Eat the world Bot op\chrome_url.exe"
RECONNECT_MACRO = r"C:\Users\camil\Desktop\Eat the world Bot op\reconnect.exe"
ROBLOX_CLOSE_FILE = r"C:\Users\camil\Desktop\Eat the world Bot op\close_roblox.exe"

# Liste des macros à vérifier et arrêter
MACROS_TO_STOP = [
    r"C:\Users\camil\Desktop\Eat the world Bot op\macro_debut.exe",
    r"C:\Users\camil\Desktop\Eat the world Bot op\échap.exe",
    r"C:\Users\camil\Desktop\Eat the world Bot op\macro_vente.exe",
    r"C:\Users\camil\Desktop\Eat the world Bot op\macro_periodique1.exe",
    r"C:\Users\camil\Desktop\Eat the world Bot op\macro_achat_muti.exe",
]

# Coordonnées et couleur des pixels à vérifier
PIXEL_X = 1082
PIXEL_Y = 568
PIXEL_COLOR = (57, 59, 61)  # La couleur cible du pixel

def stop_active_macros():
    """Vérifie et arrête les macros actives spécifiées dans MACROS_TO_STOP."""
    for process in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            # Vérifie si le processus correspond à l'un des chemins des macros
            process_path = process.info['exe']
            if process_path and process_path in MACROS_TO_STOP:
                print(f"Arrêt du processus : {process_path}")
                process.terminate()  # Envoie un signal pour terminer le processus
                process.wait()  # Attendre que le processus se termine
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

def is_roblox_open():
    """Vérifie si Roblox est ouvert, en excluant les processus Chrome."""
    for process in psutil.process_iter(['name', 'cmdline']):
        try:
            # Vérifier si le nom du processus contient 'Roblox'
            if process.info['name'] and 'roblox' in process.info['name'].lower():
                return True
            # Exclure les processus Chrome contenant 'Roblox' dans leurs arguments
            if process.info['name'] and 'chrome' in process.info['name'].lower():
                if process.info['cmdline'] and any('roblox' in arg.lower() for arg in process.info['cmdline']):
                    continue
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

def press_shortcut():
    """Simule le raccourci clavier Ctrl+Shift+Alt+P."""
    keyboard.send('ctrl+shift+alt+p')

def check_pixel_color(x, y, color):
    """Vérifie si un pixel a une couleur spécifique."""
    return pyautogui.pixel(x, y) == color

def read_status(file_path):
    """Lit le statut d'un fichier texte."""
    try:
        with open(file_path, "r") as file:
            return int(file.read().strip())
    except FileNotFoundError:
        print(f"Fichier introuvable : {file_path}")
        return 0
    except ValueError:
        print(f"Erreur de lecture du fichier {file_path}, valeur par défaut = 0.")
        return 0

def reset_chest_status():
    """Réinitialise la valeur du fichier Chest_statue.txt à 0."""
    with open(CHEST_STATUS_FILE, "w") as file:
        file.write("0")

def perform_actions():
    # Réinitialisation de Chest_statue.txt
    reset_chest_status()

    # Arrêter les macros actives avant de continuer
    print("Vérification et arrêt des macros actives...")
    stop_active_macros()

    for _ in range(5):
        press_shortcut()
        time.sleep(0.5)  # Pause de 0,5 seconde entre chaque exécution

    # Fermer Roblox
    roblox_close = subprocess.Popen(ROBLOX_CLOSE_FILE, shell=True)
    roblox_close.wait()  # Attendre que la macro soit terminée
    
    # Attendre 3 secondes
    time.sleep(3)
    
    # Ouvrir Chrome
    print("Ouverture de Chrome...")

    # Lancer la macro pour l'URL
    print("Lancement de la macro pour l'URL Roblox...")
    process_chrome_url = subprocess.Popen(CHROME_URL_MACRO, shell=True)
    process_chrome_url.wait()  # Attendre que la macro soit terminée

    time.sleep(1)  # Laisser le temps à Chrome de se stabiliser après la macro

    # Attendre 30 secondes
    print("Attente de 30 secondes pour le chargement de la page...")
    time.sleep(30)

    # Condition inversée
    if not is_roblox_open() or check_pixel_color(PIXEL_X, PIXEL_Y, PIXEL_COLOR):
        print("Condition remplie pour recommencer : Roblox fermé ou pixel principal détecté.")
        perform_actions()  # Réappel de la fonction
    else:
        print("Aucune condition remplie, lancement de la macro reconnect...")
        process_reconnect = subprocess.Popen(RECONNECT_MACRO, shell=True)
        process_reconnect.wait()  # Attendre que la macro reconnect soit terminée
        print("Reconnect terminé, fin des actions.")

def main():
    """Boucle principale."""
    process_script = None  # Variable pour stocker le processus du script secondaire

    while True:
        # Vérifier si le script est déjà en cours d'exécution
        if process_script is None or process_script.poll() is not None:
            print("Lancement du script eat_the_world_multi_farm.py...")
            # Lancer le script en parallèle
            process_script = subprocess.Popen(['python', EAT_WORLD_SCRIPT], shell=True)

        while True:
            # Vérifier la couleur du pixel et le statut dans Chest_statue.txt
            chest_status = read_status(CHEST_STATUS_FILE)
            if check_pixel_color(PIXEL_X, PIXEL_Y, PIXEL_COLOR) and chest_status == 0:
                print("Pixel détecté et valeur dans Chest_statue.txt = 0.")
                
                # Arrêter le script en cours, forcé si nécessaire
                if process_script.poll() is None:  # Si le processus est actif
                    print("Arrêt forcé du script eat_the_world_multi_farm.py...")
                    process_script.kill()  # Arrêt forcé du processus
                    process_script.wait()  # S'assurer qu'il est complètement terminé
                    print("Script arrêté avec succès.")

                # Lire le statut de l'autoclick
                autoclick_status = read_status(AUTOCLICK_STATUS_FILE)
                if autoclick_status == 1:
                    print("Statut de l'autoclick = 1, pression sur F6...")
                    keyboard.send("f6")  # Simuler une pression sur F6

                # Appeler la fonction d'actions
                try:
                    perform_actions()
                except Exception as e:
                    print(f"Erreur dans perform_actions : {e}")
                    break  # Sortir de la boucle en cas d'erreur pour éviter un appel infini

                break  # Revenir au début de la boucle principale

            time.sleep(1)  # Pause pour éviter une surcharge CPU

if __name__ == "__main__":
    main()

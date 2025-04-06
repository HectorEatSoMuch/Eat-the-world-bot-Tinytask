import os
import time
import keyboard
import threading
from subprocess import Popen

# Variables globales
auto_click_state = False  # État de l'autoclick (False: désactivé, True: activé)
spam_thread = None  # Référence au processus de spam de 'o'

# Définir le répertoire du script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Chemins vers les macros
macro_debut = os.path.join(script_dir, "macro_debut.exe")
macro_vente = os.path.join(script_dir, "macro_vente.exe")
macro_periodique = os.path.join(script_dir, "macro_periodique_event.exe")
macro_achat_maxsize = os.path.join(script_dir, "macro_achat_maxsize.exe")

# Démarrer une macro et attendre sa fin
def start_macro(file_name):
    print(f"Lancement de la macro : {file_name}")
    process = Popen([file_name], shell=True)
    process.wait()  # Attendre que la macro se termine avant de continuer
    print(f"Macro {file_name} terminée.")

# Activer/Désactiver l'autoclick
def toggle_autoclick():
    global auto_click_state, spam_thread
    if auto_click_state:
        # Désactiver l'autoclick
        keyboard.press_and_release("f6")
        auto_click_state = False
        print("Autoclick désactivé.")
        if spam_thread and spam_thread.is_alive():
            spam_thread = None  # Le thread s'arrête de lui-même
    else:
        # Activer l'autoclick
        keyboard.press_and_release("f6")
        auto_click_state = True
        print("Autoclick activé.")
        spam_thread = threading.Thread(target=spam_o)
        spam_thread.start()

# Spam de "o" uniquement quand l'autoclick est actif
def spam_o():
    while auto_click_state:
        keyboard.press("o")
        time.sleep(0.05)  # Petit délai pour éviter une surcharge

# Vérifier la couleur du pixel
def is_target_color():
    import pyautogui
    pixel_color = pyautogui.pixel(1722, 954)
    return pixel_color == (60, 141, 38)

# Cycle de farming
def farming_cycle():
    print("Démarrage du cycle de farming.")
    while True:
        print("Lancement de la macro de début.")
        start_macro(macro_debut)  # Attendre que la macro de début termine avant de continuer
        toggle_autoclick()  # Activer l'autoclick après la fin de la macro

        while True:
            if is_target_color():
                print("Pixel détecté, désactivation de l'autoclick et lancement de la macro de vente.")
                toggle_autoclick()  # Désactiver l'autoclick
                start_macro(macro_vente)
                time.sleep(5)  # Attente pour terminer la vente
                print("Reprise du farming.")
                break

# Timer de 1h30
def periodic_cycle():
    start_time = time.time()
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time >= 5400:  # 1h30 = 5400 secondes
            print("Temps écoulé, désactivation de l'autoclick et lancement des macros périodiques.")
            if auto_click_state:
                toggle_autoclick()  # Désactiver l'autoclick
            print("Exécution de la macro périodique.")
            start_macro(macro_periodique)
            time.sleep(5)  # Attente pour terminer la macro
            print("Exécution de la macro achat maxsize.")
            start_macro(macro_achat_maxsize)
            time.sleep(5)  # Attente pour terminer la macro
            print("Réinitialisation du timer.")
            start_time = time.time()
        time.sleep(1)  # Éviter une boucle trop rapide

# Fonction principale
def main():
    farming_thread = threading.Thread(target=farming_cycle, daemon=True)
    farming_thread.start()
    periodic_cycle()  # Timer principal

if __name__ == "__main__":
    main()

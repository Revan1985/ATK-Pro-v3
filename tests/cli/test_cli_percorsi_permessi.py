import os
import subprocess

def test_percorso_assente():
    print("=== Test percorso assente ===")
    try:
        # Simuliamo un file inesistente
        subprocess.run(["python", "test_main_cli.py", "input_inesistente.txt"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Errore gestito correttamente: {e}")

def test_permessi_limitati():
    print("=== Test permessi limitati ===")
    # Creiamo una cartella con permessi negati
    os.makedirs("cartella_protetta", exist_ok=True)
    try:
        # Su Linux/Mac: togliamo i permessi
        os.chmod("cartella_protetta", 0o000)
        subprocess.run(["python", "test_main_cli.py", "cartella_protetta/file.txt"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Errore gestito correttamente: {e}")
    finally:
        # Ripristiniamo i permessi per poter cancellare la cartella
        os.chmod("cartella_protetta", 0o755)
        os.rmdir("cartella_protetta")

if __name__ == "__main__":
    test_percorso_assente()
    test_permessi_limitati()

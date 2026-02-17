"""
Ensure Playwright browsers are available
Run this during ATK-Pro initialization
"""

import os
import sys


def ensure_playwright_browsers():
    """Scarica i browser Playwright se non presenti"""
    try:
        # Prova a importare e lanciare playwright per farlo scaricare
        from playwright.sync_api import sync_playwright
        
        print("[Playwright] Controllando disponibilità browser...")
        
        try:
            # Questo triggererà il download se mancante
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                browser.close()
                print("[Playwright] ✅ Browser disponibile")
                return True
        except Exception as download_error:
            print(f"[Playwright] ⚠ Browser non disponibile: {download_error}")
            print("[Playwright] Tentando download automatico...")
            
            # Esegui playwright install
            import subprocess
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("[Playwright] ✅ Browser scaricati con successo")
                return True
            else:
                print(f"[Playwright] ❌ Errore durante download: {result.stderr}")
                return False
                
    except ImportError:
        print("[Playwright] ❌ Playwright non installato")
        return False
    except Exception as e:
        print(f"[Playwright] ❌ Errore sconosciuto: {e}")
        return False


if __name__ == "__main__":
    ensure_playwright_browsers()

================================================================================
  ATK-Pro v2.0 per Linux - Istruzioni di utilizzo
================================================================================

REQUISITI SISTEMA:
- Linux x86_64 (Ubuntu 20.04+, Debian 11+, Fedora 34+, etc.)
- Librerie Qt6 (di solito già presenti)
- Connessione Internet per scaricare browser Playwright al primo avvio

INSTALLAZIONE:

1. Estrai l'archivio:
   tar -xzf ATK-Pro-Linux.tar.gz

2. Rendi eseguibile (se necessario):
   chmod +x ATK-Pro

3. Avvia l'applicazione:
   ./ATK-Pro

PRIMO AVVIO:
Al primo utilizzo, ATK-Pro scaricherà automaticamente Chromium (~150 MB).
Questo processo può richiedere alcuni minuti.

DIPENDENZE MANCANTI:
Se ricevi errori su librerie mancanti, installa:

Ubuntu/Debian:
  sudo apt-get install libxcb-xinerama0 libxcb-cursor0 libegl1 libdbus-1-3

Fedora/RHEL:
  sudo dnf install xcb-util-cursor libxkbcommon-x11 mesa-libEGL dbus-libs

Arch Linux:
  sudo pacman -S xcb-util-cursor libxkbcommon-x11 mesa dbus

DESKTOP INTEGRATION (opzionale):
Per aggiungere ATK-Pro al menu applicazioni, crea il file:
~/.local/share/applications/atkpro.desktop

Con questo contenuto:

[Desktop Entry]
Type=Application
Name=ATK-Pro
Comment=IIIF Archive Toolkit Professional
Exec=/percorso/completo/ATK-Pro
Icon=/percorso/completo/assets/common/grafici/ATK-Pro.ico
Terminal=false
Categories=Utility;

Sostituisci "/percorso/completo/" con il path reale dove hai copiato ATK-Pro.

SUPPORTO:
Repository GitHub: https://github.com/DanielePigoli/ATK-Pro-v2
Issues: https://github.com/DanielePigoli/ATK-Pro-v2/issues

================================================================================
© 2026 ATK-Pro - Distribuito sotto licenza open source
================================================================================

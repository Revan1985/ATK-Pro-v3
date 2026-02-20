================================================================================
  ATK-Pro v2.0 per macOS - Istruzioni di installazione
================================================================================

IMPORTANTE: Questa applicazione non è firmata con un certificato Apple Developer.
macOS potrebbe mostrarti un messaggio "L'app è danneggiata" o bloccarla.

SOLUZIONE (scegli una):

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
METODO 1: Rimuovi attributi di quarantena (CONSIGLIATO)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Apri il Terminale (Applicazioni > Utility > Terminale)

2. Trascina l'app ATK-Pro.app dentro la finestra del Terminale
   (oppure digita il percorso completo)

3. Premi Backspace per rimuovere lo spazio finale, poi digita:
   
   Esempio se l'app è in /Applications:
   xattr -cr /Applications/ATK-Pro.app

4. Premi Invio

5. Ora puoi aprire normalmente ATK-Pro dalle Applicazioni

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
METODO 2: Apri con Control+Click (alternativo)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Trova ATK-Pro.app in Finder

2. Tieni premuto Control e clicca sull'icona

3. Seleziona "Apri" dal menu

4. Clicca di nuovo "Apri" nella finestra di conferma

5. Da ora in poi potrai aprire l'app normalmente

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
METODO 3: Impostazioni di sistema (se i precedenti non funzionano)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Vai in Impostazioni di sistema > Privacy e sicurezza

2. Scorri fino a "Sicurezza"

3. Se vedi un messaggio su ATK-Pro bloccata, clicca "Apri comunque"

4. Conferma con la tua password

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REQUISITI SISTEMA:
- macOS 10.13 (High Sierra) o successivo
- Connessione Internet per scaricare i browser Playwright al primo avvio
- Python 3.12 già incluso nell'app bundle

PRIMO AVVIO:
Al primo utilizzo, ATK-Pro scaricherà automaticamente Chromium (~150 MB).
Questo processo può richiedere alcuni minuti.

SUPPORTO:
Repository GitHub: https://github.com/DanielePigoli/ATK-Pro-v2
Issues: https://github.com/DanielePigoli/ATK-Pro-v2/issues

================================================================================
© 2026 ATK-Pro - Distribuito sotto licenza open source
================================================================================

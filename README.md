# CrossLink

CrossLink è un'applicazione leggera per il trasferimento file tra PC e dispositivi mobili (Android) che utilizza una semplice interfaccia web locale, accessibile tramite scansione QR.

## Funzionalità
- **Server Web Locale**: Condivide istantaneamente la cartella corrente.
- **Accesso QR**: Scansiona il codice QR per aprire la pagina di upload/download sul telefono.
- **Upload Progress**: Barra di caricamento in tempo reale nel browser.
- **Storico**: Tieni traccia dei file ricevuti durante la sessione.

## Installazione (PC)
Assicurati di avere `python3` e `pip` installati.

1. Clona il repository:
   ```bash
   git clone https://github.com/Vagabondiamo/CrossLink.git
   cd CrossLink
   ```
2. Crea un ambiente virtuale e installa le dipendenze:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install fastapi uvicorn qrcode[pil] python-multipart segno
   ```

## Come usare
Per avviare il server di condivisione file nella cartella corrente:

```bash
# Se hai installato lo script globale:
crosslink

# Oppure, se sei nella cartella del progetto:
./venv/bin/python3 server.py
```

Il terminale mostrerà un codice QR. Scansionalo con il tuo dispositivo mobile per aprire la dashboard di trasferimento nel browser.

## Sviluppo
- Il server è basato su **FastAPI**.
- I file caricati verranno salvati nella cartella in cui avvii il server.
- Per il download, usa la lista presente nella pagina web.

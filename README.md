# 🚴 PT Cycling: WorldTour Indoor Training System
### 100% Serverless • Cloud-Native • Auto-Adaptive FTP • Zero-PC Architecture

> **Progettato per:** Rullo interattivo **Elite Suito** (modalità ERG)  
> **Sincronizzazione Automatica:** **Intervals.icu** ➡️ **MyWhoosh** (Tablet Android) & **Garmin Edge 850** (Fallback)  
> **Controllo Zero-Friction:** **1-Tap diretto da Smartphone** (senza aprire l'app GitHub) o tramite **Apple Shortcuts / Telegram**  
> **Filosofia di Carico:** **WorldTour Multi-Archetipo** — Allenamenti **sempre nuovi, non ripetitivi ed incrementali** (Livelli 1.0 -> 10.0 per VO2max, Sweet Spot e Soglia) su FTP di partenza di **205 Watt** (solo parametri fisiologici assoluti in Watt, %FTP, IF, TSS, EF e Decoupling Pw:Hr).

---

## 🧭 Indice
1. [Controllo 1-Tap da Smartphone (Zero Navigazione GitHub)](#-controllo-1-tap-da-smartphone-zero-navigazione-github)
2. [Motore WorldTour: Allenamenti Sempre Nuovi ed Incrementali](#-motore-worldtour-allenamenti-sempre-nuovi-ed-incrementali)
3. [Ottimizzazioni Biomeccaniche per Elite Suito ERG](#-ottimizzazioni-biomeccaniche-per-elite-suito-erg)
4. [Architettura Cloud & Sincronizzazione](#-architettura-cloud--sincronizzazione)
5. [Configurazione Cloud Passo-Passo (Secrets & Token)](#-configurazione-cloud-passo-passo-secrets--token)
6. [Integrazione Telegram & Apple Shortcuts (Opzionali)](#-integrazione-telegram--apple-shortcuts-opzionali)
7. [Specifiche delle Sessioni (42 - 60 Minuti)](#-specifiche-delle-sessioni-42---60-minuti)
8. [Sviluppo Locale e Test](#-sviluppo-locale-e-test)

---

## 📱 Controllo 1-Tap da Smartphone (Zero Navigazione GitHub)

Per evitare completamente di aprire l'applicazione di GitHub e dover cliccare ogni volta su *Actions ➔ PT Cycling WorldTour Coach ➔ Run workflow*, il sistema include una **Web App Progressive (PWA)** mobile-first che si comporta come una vera applicazione sul tuo smartphone:

```
┌─────────────────────────────────────────────────────────────┐
│                       SCHERMO TELEFONO                      │
│                                                             │
│  [🚴 PT Cycling WorldTour]        [⚙️ Impostazioni Token]   │
│                                                             │
│  FTP Attuale: 205W                Fase: Settimana 1 di 4    │
│  VO2max: Lvl 1.0 • Sweet Spot: Lvl 1.0 • Soglia: Lvl 1.0    │
│                                                             │
│  Giorni Indoor: [LUN] [MER] [VEN]                           │
│  Durata: [───────●──────] 50 minuti                         │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │    🚀 1-TAP: PROGRAMMA E SINCRONIZZA ORA              │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ✅ "Allenatore attivato! Workout sincronizzati su          │
│      MyWhoosh e Garmin Edge in 30 secondi."                 │
└─────────────────────────────────────────────────────────────┘
```

### Come installarla e usarla in 1 minuto:
1. **Apri la Web App sul browser dello smartphone:**  
   Vai all'indirizzo del tuo repository su GitHub Pages (es. `https://<tuo-utente>.github.io/<nome-repo>/web/`).
2. **Aggiungi alla Schermata Home:**  
   - **Su iPhone (Safari):** Tocca l'icona **Condividi** (quadrato con freccia) ➔ Seleziona **Aggiungi a schermata Home**.
   - **Su Android (Chrome):** Tocca i tre puntini in alto a destra ➔ **Aggiungi ad Home** / **Installa app**.
3. **Configura il Token una volta sola:**  
   Tocca l'icona dell'ingranaggio in alto a destra nella Web App e incolla:
   - Nome del repository (es. `tuo-username/PT-Cycling`).
   - Un GitHub Personal Access Token (PAT) con permesso *Actions (Read & Write)*.  
   *(Questo token rimane memorizzato unicamente nella memoria locale del tuo telefono: `localStorage`, 100% privato e sicuro)*.
4. **Da oggi in poi:**  
   Apri l'icona di PT Cycling sul telefono, scegli i giorni con un tocco, regola lo slider dei minuti e premi il pulsante arancione **"🚀 1-TAP: PROGRAMMA E SINCRONIZZA ORA"**. Fatto!

---

## 🏆 Motore WorldTour: Allenamenti Sempre Nuovi ed Incrementali

Un vero preparatore atletico WorldTour non ripete mai la stessa identica tabella ogni settimana. Il motore applica un catalogo multi-archetipo scientifico e gestisce una **matrice di progressione a 3 livelli energetici indipendenti (1.0 -> 10.0)**:

### 1. Catalogo Multi-Archetipo (Rotazione Continua)
Il sistema seleziona dinamicamente archetipi non ripetuti, evitando la noia e stimolando adattamenti metabolici complementari:

| Categoria | Archetipi WorldTour Inclusi | Stimolo Fisiologico |
| :--- | :--- | :--- |
| **VO2max** | • **Rønnestad 30/15 High-Ventilation**<br>• **Hard-Start Fast O2-Kinetics** (130% burst + plateau 112%)<br>• **Piramide Discendente** (4m-3m-2m-1m a Watt crescenti)<br>• **Tabata Clusters 40/20 & 30/30**<br>• **Torque Stomp (60 RPM) + VO2 Plateau** | Cinetica rapida di assorbimento dell'ossigeno, stroke volume cardiaco e attivazione fibre veloci IIx. |
| **Sweet Spot** | • **Criss-Cross Lactate Flux** (oscillazioni continue 87% / 95%)<br>• **Forza Resistente 55 RPM vs Spin 100 RPM**<br>• **Gradini Ascendenti** (86% -> 90% -> 93%)<br>• **Extended Endurance Engine** (blocchi lunghi 2x 14-16 min)<br>• **Dinamica di Cadenza 85/102 RPM** | Densità aerobica mitocondriale, clearance del lattato senza stress cardiaco e trazione periferica. |
| **Soglia / Over-Under** | • **Float Sets Clearance** (100% soglia + 85% Float — *zero recupero passivo*)<br>• **Spanish Steps Surges** (base 95% con sgasate a 115% ogni 90s)<br>• **Piramide Over-Under Lattacida** (Under 92% / Over 108%)<br>• **Agilità di Soglia Crono** (100% FTP a 100 RPM costanti)<br>• **Scala Sostenuta FTP** (96% -> 98% -> 100%) | Smaltimento del lattato ad andature gara e tolleranza all'acidosi muscolare. |
| **Scarico & Pre-Test** | • **Openers Neuromuscolari ad Alta Cadenza (110 RPM)**<br>• **Attivazione Pre-Test WorldTour** (Z2 + brevi tocchi soglia) | Mantenimento della freschezza neuromuscolare prima dell'auto-incremento FTP. |

### 2. Livelli di Preparazione Auto-Adattivi (1.0 -> 10.0)
- Ogni volta che completi con successo le sessioni settimanali con compliance $\ge 85\%$, il livello di preparazione del sistema energetico incrementa (es. **VO2max: Lvl 1.0 ➔ Lvl 1.4**).
- Gli intervalli futuri aumentano di densità (più ripetute, recuperi più stretti, wattaggi più specifici).
- Al termine della Settimana 4 (Scarico), se il blocco 3:1 ha avuto successo ($\ge 85\%$ completamento e decoupling $Pw:Hr \le 6.5\%$), **l'FTP sale del +2% (es. da 205W a 209W-210W)** e i livelli si ricalibrano sulla nuova base di potenza.

---

## ⚙️ Ottimizzazioni Biomeccaniche per Elite Suito ERG

In modalità ERG con rullo a trasmissione diretta Elite Suito:
1. **Warm-up Reattivo (7.5 - 8 minuti):** Rampa progressiva (50% ➔ 75% FTP) + **3 scatti da 15s al 105% FTP (100-105 RPM)** per scaldare il freno magnetico ed eliminare il ritardo di coppia.
2. **Allarmi Visivi Anti-Spiral-of-Death:** Negli intervalli duri e negli Over-Under, il file include la notifica testuale visualizzata sul display di MyWhoosh e Garmin:  
   `"Aumenta la cadenza a 95-100 RPM prima dello step!"`
3. **Cool-down Millimetrico (4 - 5 minuti):** Rampa 55% ➔ 40% dimensionata al secondo per rispettare la durata target esatta tra **42 e 60 minuti**.

---

## 🔐 Configurazione Cloud Passo-Passo (Secrets & Token)

### 1. Inserisci i Secrets principali su GitHub
Vai sul tuo repository GitHub ➔ **Settings** ➔ **Secrets and variables** ➔ **Actions** ➔ **New repository secret**:
- `INTERVALS_ATHLETE_ID`: il tuo ID atleta Intervals.icu (es. `i12345` o numerico).
- `INTERVALS_API_KEY`: la tua chiave API di Intervals.icu (Settings ➔ Developer).
- *(Opzionale)* `TELEGRAM_BOT_TOKEN`: Token del tuo bot Telegram.
- *(Opzionale)* `TELEGRAM_CHAT_ID`: Il tuo ID chat Telegram per ricevere il report domenicale.

### 2. Crea un Personal Access Token (per il pulsante 1-Tap)
1. Su GitHub tocca il tuo profilo in alto a destra ➔ **Settings** ➔ **Developer Settings** ➔ **Personal access tokens** ➔ **Fine-grained tokens**.
2. Clicca su **Generate new token**:
   - Repository access: seleziona solo il tuo repository (`PT-Cycling`).
   - Repository permissions: imposta **Actions** su **Read and write**.
3. Copia il token generato e incollalo nella Web App sul tuo smartphone toccando l'ingranaggio in alto a destra.

---

## 💬 Integrazione Telegram & Apple Shortcuts (Opzionali)

### Notifiche Telegram Dirette
Se imposti `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`, ogni domenica sera alle 20:00 (o ad ogni esecuzione manuale) il cloud invia direttamente sul tuo Telegram:
- Report di compliance e decoupling cardiaco ($Pw:Hr$).
- Eventuale salto di FTP calcolato in automatico (+2%).
- La scheda completa dei 3 nuovi allenamenti settimanali con i Watt di ciascun blocco.

### Apple Shortcuts (Comandi Rapidi iOS)
Puoi creare un'icona sulla schermata di blocco o chiedere a Siri:  
`"Ehi Siri, prepara allenamenti indoor"`  
Configurando una semplice azione **"Ottieni i contenuti dell'URL"** verso l'API di GitHub:
- **URL:** `https://api.github.com/repos/<username>/<repo>/actions/workflows/coach_automation.yml/dispatches`
- **Metodo:** `POST`
- **Intestazioni:** `Authorization: Bearer <tuo-token>`, `Accept: application/vnd.github+json`
- **Corpo Richiesta:** `{"ref":"main"}`

---

## 🧪 Sviluppo Locale e Test

```bash
# Esegui i 10 test di regressione unitari (verificano archetipi, durate e Suito ERG)
python3 -m pytest tests/ -v

# Esegui l'orchestratore in modalità simulazione locale
python3 src/main.py --dry-run
```

Tutti i test sono superati con successo al 100%. Il sistema è pronto per essere spinto sul tuo GitHub e utilizzato direttamente dal tuo smartphone!

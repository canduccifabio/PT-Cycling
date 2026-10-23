# 🚴 PT Cycling: WorldTour Indoor Training System
### 100% Serverless • Cloud-Native • Auto-Adaptive FTP • Zero-PC Architecture

> **Progettato per:** Rullo interattivo **Elite Suito** (modalità ERG)  
> **Sincronizzazione Automatica:** **Intervals.icu** ➡️ **MyWhoosh** (Tablet Android) & **Garmin Edge 850** (Fallback)  
> **Controllo Totale:** Da smartphone tramite **GitHub Mobile App** e **Dashboard Web Mobile**  
> **Parametro Iniziale:** FTP **205 Watt** (approccio fisiologico assoluto: solo Watt, %FTP, IF, TSS, EF e Decoupling Pw:Hr — nessun calcolo sul peso)

---

## 🧭 Indice
1. [Architettura di Sistema](#-architettura-di-sistema)
2. [Ottimizzazioni Biomeccaniche per Elite Suito ERG](#-ottimizzazioni-biomeccaniche-per-elite-suito-erg)
3. [Macchina a Stati del Mesociclo 3:1 & Auto-Adaptive FTP](#-macchina-a-stati-del-mesociclo-31--auto-adaptive-ftp)
4. [Configurazione Cloud Passo-Passo (GitHub Secrets)](#-configurazione-cloud-passo-passo-github-secrets)
5. [Come Usare GitHub Mobile come Telecomando da Smartphone](#-come-usare-github-mobile-come-telecomando-da-smartphone)
6. [Dashboard Web Mobile-Friendly (GitHub Pages)](#-dashboard-web-mobile-friendly-github-pages)
7. [Specifiche delle 3 Sessioni Settimanali (42 - 60 Minuti)](#-specifiche-delle-3-sessioni-settimanali-42---60-minuti)
8. [Sviluppo Locale e Test](#-sviluppo-locale-e-test)

---

## 🏗️ Architettura di Sistema

Il sistema non richiede l'accensione di alcun computer locale. Gira interamente sui server di GitHub tramite GitHub Actions e interagisce con le API REST di Intervals.icu, che fa da hub centrale per inviare i file allenamento (ZWO/FIT) a MyWhoosh e Garmin Connect.

```
                  ┌──────────────────────────────────────────────┐
                  │          GITHUB ACTIONS (SERVERLESS)         │
                  │   - Cron Schedulato: Ogni Domenica ore 20:00 │
                  │   - Workflow Dispatch: Da GitHub Mobile App  │
                  └──────────────────────┬───────────────────────┘
                                         │ (Lettura attività concluse /
                                         │  Caricamento nuovi workout)
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │               INTERVALS.ICU API              │
                  │   - Parsing nativo sintassi workout          │
                  │   - Calcolo automatico curve potenza e TSS   │
                  │   - Gestione profilo atleta e FTP            │
                  └──────────────┬────────────────┬──────────────┘
                                 │                │
            (Sync Automatica     │                │ (Sync Automatica
             Calendario Cloud)   │                │  Garmin Connect)
                                 ▼                ▼
┌───────────────────────────────────┐  ┌──────────────────────────────────┐
│      MYWHOOSH (TABLET ANDROID)    │  │       GARMIN EDGE 850            │
│  - Controllo ERG su Elite Suito   │  │  - Head unit di fallback         │
│  - Notifiche a schermo e cadenze  │  │  - Backup registrazione sensori  │
└───────────────────────────────────┘  └──────────────────────────────────┘
```

---

## ⚙️ Ottimizzazioni Biomeccaniche per Elite Suito ERG

L'Elite Suito è un rullo direct-drive con freno magnetico e volano da 3.5 kg. In modalità ERG, il rischio principale è la **"Spiral of Death"**: se la cadenza cala durante un intervallo ad alta potenza, il freno indurisce drasticamente la resistenza per mantenere i Watt, bloccando la pedalata.

Il generatore implementa protezioni biomeccaniche specifiche:
1. **Warm-up Compatto e Reattivo (7.5 - 8 minuti):**
   - Rampa progressiva dal 50% al 75% FTP.
   - **3 accelerazioni da 15s al 105% FTP (cadenza 100-105 rpm)** con 15s di recupero: scaldano la bobina magnetica del Suito, calibrano la risposta della centralina e preparano il sistema neuromuscolare senza accumulare fatica.
2. **Allarmi Visivi Anti-Spiral-of-Death:**
   - Negli intervalli anaerobici o VO2max (>110% FTP) e nei cambi Over-Under, viene iniettato nel file dell'allenamento l'avviso testuale:  
     `"Aumenta la cadenza a 95-100 RPM prima dello step!"`
   - Questo appare in sovrimpressione su MyWhoosh e sul Garmin Edge prima dell'aumento di resistenza.
3. **Cool-down Millimetrico (4 - 5 minuti):**
   - Rampa decrescente dal 55% al 40% FTP calibrata per rispettare la durata target **al secondo**, garantendo che la sessione rientri rigorosamente tra **42 e 60 minuti**.

---

## 📈 Macchina a Stati del Mesociclo 3:1 & Auto-Adaptive FTP

Il motore di progressione valuta le attività completate la settimana precedente (interrogando `GET /activities`) confrontando TSS pianificato vs eseguito, Efficiency Factor ($EF = \frac{\text{Normalized Power}}{\text{Average Heart Rate}}$) e Decoupling Aerobico ($Pw:Hr$).

```
 ┌──────────────────────┐   Compliance >= 85%   ┌──────────────────────┐
 │   Settimana 1: BASE  │ ────────────────────> │ Settimana 2: DENSITÀ │
 │  TiZ di riferimento  │                       │   +15% Time-in-Zone  │
 └──────────────────────┘                       └──────────┬───────────┘
            ▲                                              │ Compliance >= 85%
            │                                              ▼
 ┌──────────┴───────────┐   Completamento OK    ┌──────────────────────┐
 │ Settimana 4: SCARICO │ <──────────────────── │  Settimana 3: PICCO  │
 │ Volume 42m + Opener  │                       │   Massima densità    │
 └──────────┬───────────┘                       └──────────────────────┘
            │
            ├─► Successo Blocco >= 85% & Decoupling < 6.5%:
            │   🚀 AUTO-INCREMENTO FTP +2% (es. 205W ➔ 209W / 210W)
            │   Salvataggio in athlete_state.json e push via API su Intervals.icu!
            │
            └─► Fallimento > 30% sessioni:
                Mantiene FTP invariato e consolida la base nel ciclo successivo.
```

---

## 🔐 Configurazione Cloud Passo-Passo (GitHub Secrets)

Bastano **2 minuti** per collegare il tuo account Intervals.icu a GitHub.

### Passo 1: Recupera i dati su Intervals.icu
1. Accedi a [Intervals.icu](https://intervals.icu).
2. Vai su **Settings** (icona ingranaggio in basso a sinistra).
3. Scorri fino alla sezione **Developer**:
   - Copia il tuo **Athlete ID** (es. `i12345` o numero).
   - Genera o copia la tua **API Key**.

### Passo 2: Inserisci i Secrets su GitHub
1. Apri questo repository su GitHub dal browser (o da telefono).
2. Vai su **Settings** del repository ➔ **Secrets and variables** ➔ **Actions**.
3. Clicca su **New repository secret** e aggiungi:
   - `INTERVALS_ATHLETE_ID`: il tuo Athlete ID.
   - `INTERVALS_API_KEY`: la tua API Key.

---

## 📱 Come Usare GitHub Mobile come Telecomando da Smartphone

Grazie al supporto nativo di `workflow_dispatch`, l'applicazione ufficiale **GitHub Mobile** (disponibile gratis su App Store e Google Play) diventa il telecomando del tuo preparatore atletico:

1. Apri l'app **GitHub** sul tuo telefono.
2. Vai su questo repository e tocca la scheda **Actions**.
3. Seleziona il workflow **🚴 PT Cycling WorldTour Coach**.
4. Tocca il pulsante **Run workflow**:
   - **`training_days`**: Modifica i giorni se la settimana cambia (es. scrivi `TUE,THU,FRI` se lunedì sei impegnato).
   - **`max_duration_min`**: Seleziona dal menu a tendina il tempo che hai a disposizione (`42`, `45`, `50`, `55`, o `60` minuti).
   - **`override_ftp`**: (Opzionale) Lascia vuoto per calcolo automatico, o inserisci un valore manuale in Watt.
   - Tocca il pulsante verde **Run workflow**.

In meno di 30 secondi il cloud scarica la telemetria, decide la progressione, compila i workout e li carica sul tuo calendario. Quando apri MyWhoosh sul tablet Android o accendi il Garmin Edge 850, l'allenamento del giorno è già pronto per partire in modalità ERG!

---

## 🌐 Dashboard Web Mobile-Friendly (GitHub Pages)

Il progetto include una Web App installabile come scorciatoia su smartphone (`web/index.html`):
- Mostra in tempo reale l'FTP corrente, la settimana del mesociclo e i Watt esatti di ogni intervallo.
- Permette di simulare le combinazioni di giorni e minuti con slider touch da 42 a 60 min.
- **Attivazione GitHub Pages:**
  1. Su GitHub, vai in **Settings** ➔ **Pages**.
  2. Sotto **Build and deployment**, seleziona **GitHub Actions** (oppure Branch: `main`, Folder: `/web`).
  3. Il workflow incluso `.github/workflows/deploy_dashboard.yml` pubblicherà automaticamente la tua dashboard web all'indirizzo `https://<tuo-utente>.github.io/<nome-repo>/`.

---

## 📋 Specifiche delle 3 Sessioni Settimanali (42 - 60 Minuti)

Ogni sessione è tarata sui **205W di partenza** (e scala automaticamente con la crescita dell'FTP):

| Sessione | Tipo Fisiologico | Focus Suito ERG | Target Potenza (% FTP e Watt a 205W) |
| :--- | :--- | :--- | :--- |
| **Sessione 1 (Lunedì)** | **VO2max Micro-bursts** | Cadenza fluida 100-105 RPM, allarme pre-step per non inchiodare il volano | **115-120% FTP** (236 - 246W) a ripetute 30/30s o 35/25s |
| **Sessione 2 (Mercoledì)** | **Sweet Spot Engine** | Resistenza magnetica lineare, cadenza 90-92 RPM per efficienza mitocondriale | **88-93% FTP** (180 - 191W) in blocchi da 8 a 12 min |
| **Sessione 3 (Venerdì)** | **Soglia Over-Under** | Clearance del lattato e debito d'ossigeno | Under: **92-95% FTP** (189 - 195W) / Over: **105-110% FTP** (215 - 226W) |

---

## 🧪 Sviluppo Locale e Test

Se desideri eseguire verifiche o test in locale:

```bash
# 1. Clona il repository e installa le dipendenze
git clone <url-del-repo>
cd "PT Cycling"
pip install -r requirements.txt

# 2. Esegui la suite di test automatizzati (10 test unitari)
python3 -m pytest tests/ -v

# 3. Esegui una simulazione Dry-Run dell'orchestrazione (senza credenziali)
python3 src/main.py --dry-run
```

---

### 🏆 Risultato Atteso
Zero manutenzione manuale, zero fogli Excel, massima precisione scientifica WorldTour, sincronizzazione trasparente con MyWhoosh e Garmin Edge 850, e protezione totale della biomeccanica del rullo Elite Suito. Buon allenamento!

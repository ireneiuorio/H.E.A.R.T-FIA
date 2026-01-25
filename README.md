# H.E.A.R.T – Tecnica di Instradamento Adattivo in Ambiente Ospedaliero*

Questo repository contiene il progetto **H.E.A.R.T**, sviluppato per studiare il
problema della pianificazione dei percorsi in un ambiente ospedaliero indoor,
caratterizzato da costi di attraversamento dinamici e incerti.

L’obiettivo del progetto è analizzare **quando e in che condizioni l’uso del
machine learning può migliorare la pianificazione su grafo**, rispetto ad
approcci classici basati su costi statici.  
Il confronto viene effettuato utilizzando due algoritmi di ricerca standard:
**Uniform Cost Search (UCS)** e **A\***.

La domanda di ricerca che guida il lavoro è la seguente:

> 
> L’utilizzo di costi stimati tramite machine learning migliora la pianificazione di A*, oppure in alcuni casi può peggiorarne il comportamento rispetto all’uso di costi statici?

Il focus del lavoro non è sull’algoritmo di ricerca in sé, ma su **come la stima
dei costi influisce sulla qualità delle soluzioni e sull’efficienza della
ricerca**, soprattutto in presenza di variabilità e imprevedibilità
nell’ambiente.




## Ambiente simulato
L’ambiente ospedaliero è modellato come un **grafo non orientato**, in cui:
- i nodi rappresentano punti di interesse (ingresso, corridoi, reparti);
- gli archi rappresentano corridoi, ciascuno caratterizzato da:
  - lunghezza;
  - tipologia (centrale, secondario, isolato).




## Algoritmi di ricerca

Nel progetto vengono utilizzati due algoritmi di ricerca su grafo:

- **Uniform Cost Search (UCS)**  
  Espande i nodi in base al solo costo accumulato del percorso.  
  Rappresenta un baseline solido e privo di euristica.

- **A\***  
  Combina il costo accumulato con una funzione euristica.  
  Sono state testate:
  - euristica nulla (equivalente a UCS);
  -  euristica euclidea basata sulla distanza geometrica.



## Stima dei costi

I costi di attraversamento degli archi vengono stimati in tre modi:

- **Costi statici**, basati su valori medi;
- **Regressione lineare**, che modella il costo come funzione di:
  - lunghezza del corridoio;
  - orario;
  - livello di affollamento;
- **Random Forest**, che consente di catturare relazioni non lineari tra le
  variabili.

Il machine learning non sostituisce l’algoritmo di ricerca, ma viene utilizzato
per fornire **stime più adattive dei costi**.



## Scenari sperimentali

Sono stati definiti due scenari distinti:

- **Scenario normale**  
  Variabilità moderata dei costi, rumore limitato e bassa probabilità di eventi.

- **Scenario estremo**  
  Elevata variabilità, maggiore affollamento e alta probabilità di eventi
  improvvisi che aumentano i tempi di percorrenza.

Per ciascuno scenario sono stati eseguiti **50 test di pianificazione**.



## Metriche di valutazione

I risultati vengono valutati tramite:

- **Costo reale del percorso**;
- **Gap rispetto al percorso ottimo reale**;
- **Percentuale di soluzioni ottime**;
- **Numero di nodi espansi** (efficienza della ricerca);
- **Tempo di pianificazione**.

Per i modelli di machine learning vengono inoltre riportate metriche standard:
- **MAE** (errore medio assoluto);
- **RMSE** (errore quadratico medio);
- **R²** (capacità esplicativa del modello);
- **MAPE** (errore percentuale medio).



## Risultati principali
I risultati mostrano che:

- in ambienti **stabili**, l’approccio statico è semplice, veloce e già
  sufficientemente efficace;
- quando la variabilità dei tempi aumenta, le stime basate su costi medi
  diventano meno affidabili;
- la **Random Forest** riesce a migliorare la qualità delle soluzioni negli
  scenari più complessi, perché fornisce stime dei costi più accurate e più
  coerenti con le condizioni reali dell’ambiente;
- questo miglioramento comporta però un **costo computazionale più elevato**:
  a differenza dei costi statici, che sono immediatamente disponibili, le stime
  basate su machine learning richiedono la valutazione del modello per ogni arco
  durante la pianificazione, rendendo la ricerca più lenta.

Il machine learning risulta vantaggioso quando l’ambiente è
abbastanza complesso da giustificare questo aumento del tempo di calcolo.
Negli scenari più semplici e prevedibili, invece, gli approcci classici
rimangono preferibili perché offrono buone soluzioni con un costo computazionale
minimo.


Il contributo principale di questo progetto non è dimostrare che il machine learning
sia "migliore", ma chiarire in quale condizioni fornisce un reale valore aggiunto e quando,
incece, intorduce complessità inutile.


##  Utilizzo

### 1. Clonare il repository
```bash
git clone https://github.com/ireneiuorio/H.E.A.R.T-FIA.git
cd H.E.A.R.T-FIA
```

### 2. Installare le dipendenze
```bash
pip install -r requirements.txt
```

### 3. Eseguire gli esperimenti
```bash
python src/experiments/run_experiments.py
```
Questo script esegue 50 test per ciascuno dei due scenari (normale ed estremo), confrontando tutte e 4 le configurazioni.

### 4. Analizzare i risultati
```bash
python src/experiments/analizza_risultati.py
```
Genera le statistiche aggregate e le tabelle comparative presenti nella documentazione.

**Riproducibilità**: I test utilizzano seed fisso (42) per garantire risultati identici ad ogni esecuzione.
### 5. Avviare la visualizzazione interattiva *(opzionale)*
```bash
python src/visualization/visualizzatore_pygame.py
```

**Casualità della demo**: Ogni esecuzione genera scenari random (orario, affollamento, eventi imprevisti), quindi percorsi e metriche variano ad ogni avvio.

**Perché i percorsi sono spesso simili?**  
Il grafo è volutamente piccolo (26 nodi) per rendere immediato il confronto visivo. I percorsi coincidono frequentemente perché i modelli ML hanno appreso correttamente la struttura del grafo. Le **differenze emergono con forte congestione** sui corridoi centrali, dove l'informazione dinamica porta a scelte più adattive.



**Controlli sulla demo**: `1-4` per selezionare l'algoritmo | `ESC` per uscire


## Struttura del progetto
```
H.E.A.R.T-FIA/
│
├── docs/                              # H.E.A.R.T Doc (documentazione)
│
├── src/                               # Codice sorgente
│   │
│   ├── core/                          # Componenti principali
│   │   ├── astar.py                   # Implementazione A* e UCS
│   │   ├── grafo.py                   # Struttura del grafo ospedaliero (26 nodi)
│   │   └── simulator.py               # Simulatore dei tempi reali (ground truth)
│   │
│   ├── evaluation/                    # Valutazione delle prestazioni
│   │   └── metriche.py                # Calcolo metriche (costo, gap, nodi, errore)
│   │
│   ├── experiments/                   # Sperimentazione e risultati
│   │   ├── results/                   # Risultati degli esperimenti (JSON)
│   │   │   ├── scenario_estremo
│   │   │   └── scenario_normale
│   │   ├── analizza_risultati.py      # Analisi statistica e aggregazione dati
│   │   └── run_experiments.py         # Esecuzione automatica degli esperimenti
│   │
│   ├── ml/                            # Machine Learning
│   │   ├── dataset.py                 # Generazione dataset sintetico
│   │   └── modelli.py                 # Regressione Lineare e Random Forest
│   │
│   ├── visualization/                 # Interfaccia grafica
│   │   └── visualizzatore_pygame.py   # Demo interattiva con Pygame
│   │
│   └── main.py                        # Main per demo
│
├── .gitignore                         # File da escludere da Git
├── README.md                          
└── requirements.txt                   # Dipendenze Python
```


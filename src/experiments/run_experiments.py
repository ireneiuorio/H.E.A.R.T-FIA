# Esegue esperimenti e risponde alla domanda "Quando il ML diventa vantaggioso?"

import sys
import os

# Aggiungi la root del progetto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import json
from datetime import datetime

# Import moduli del progetto
from src.core.grafo import crea_grafo_complesso, ottieni_posizioni_grafo_complesso
from src.core.simulator import SimulatoreCosti, calcola_costi_statici
from src.core.astar import (
    RicercaAStar,
    euristica_nulla,
    euristica_distanza_euclidea,
    costo_statico_da_dizionario
)
from src.ml.dataset import GeneratoreDataset, split_train_test
from src.ml.modelli import (
    ModelloRegressioneLineare,
    ModelloRandomForest,
    confronta_modelli,
    crea_funzione_costo_ml_dinamica
)
from src.evaluation.metriche import CalcolatoreMetriche, MetrichePercorso


# Gestisce l'esecuzione di un esperimento completo
class EsperimentoCompleto:

    def __init__(
            self,
            nome_esperimento: str,
            grafo,
            simulatore: SimulatoreCosti,
            seed: int = 42
    ):
        self.nome = nome_esperimento
        self.grafo = grafo
        self.simulatore = simulatore
        self.seed = seed
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Risultati
        self.modelli = {}
        self.metriche_per_config = {}
        self.risultati_aggregati = {}
        self._condizioni_test = []

        # Storage per risultati completi
        self.risultati_ml_completi = {}
        self.analisi_complete = {}

        print(f"\n{'=' * 70}")
        print(f"ESPERIMENTO: {self.nome}")
        print(f"Timestamp: {self.timestamp}")
        print(f"{'=' * 70}\n")

    # Crea dati realistici, addestra modelli di Ml e prepara euristica e euclidea
    def fase_1_preparazione_dati(self, num_osservazioni: int = 2000):
        print("\n" + "=" * 70)
        print("FASE INIZIALE: PREPARAZIONE DATI E ADDESTRAMENTO ML")
        print("=" * 70)

        # Genera dataset
        gen = GeneratoreDataset(self.grafo, self.simulatore)
        # Per ogni combinazione di x e y viene testato ogni arco, non lascia il dataset sbilanciato
        X, y = gen.genera_stratificato(
            campioni_per_cella=20,
            seed=self.seed
        )

        # Quanto grande è il dataset
        print(f"Dataset generato: {len(X)} campioni")

        # Split train/test: 80% di addestramento e 20% di test
        X_train, X_test, y_train, y_test = split_train_test(
            X, y, test_size=0.2, seed=self.seed
        )

        # Addestra modelli
        modelli_lista = [
            ModelloRegressioneLineare(),
            ModelloRandomForest(numero_alberi=100, profondita_massima=10, seed=self.seed)
        ]

        risultati_ml = confronta_modelli(
            modelli_lista,
            X_train, y_train,
            X_test, y_test
        )

        # Salva modelli
        self.modelli = {
            "lineare": risultati_ml["Regressione Lineare"]["modello"],
            "rf": risultati_ml["Random Forest"]["modello"]
        }

        # Salva risultati ML completi per JSON
        try:
            self.risultati_ml_completi = {
                "dataset": {
                    "num_campioni_totali": len(X),
                    "num_train": len(X_train),
                    "num_test": len(X_test),
                    "test_size": 0.2
                },
                "regressione_lineare": {
                    "coefficienti": {
                        "lunghezza": float(risultati_ml["Regressione Lineare"]["modello"].modello.coef_[0]),
                        "orario": float(risultati_ml["Regressione Lineare"]["modello"].modello.coef_[1]),
                        "affollamento": float(risultati_ml["Regressione Lineare"]["modello"].modello.coef_[2]),
                        "intercetta": float(risultati_ml["Regressione Lineare"]["modello"].modello.intercept_)
                    },
                    "train": {
                        "mae": float(risultati_ml["Regressione Lineare"].get("metriche_train", {}).get("mae", 0)),
                        "rmse": float(risultati_ml["Regressione Lineare"].get("metriche_train", {}).get("rmse", 0)),
                        "r2": float(risultati_ml["Regressione Lineare"].get("metriche_train", {}).get("r2", 0)),
                        "mape": float(risultati_ml["Regressione Lineare"].get("metriche_train", {}).get("mape", 0))
                    },
                    "test": {
                        "mae": float(risultati_ml["Regressione Lineare"].get("metriche_test", {}).get("mae", 0)),
                        "rmse": float(risultati_ml["Regressione Lineare"].get("metriche_test", {}).get("rmse", 0)),
                        "r2": float(risultati_ml["Regressione Lineare"].get("metriche_test", {}).get("r2", 0)),
                        "mape": float(risultati_ml["Regressione Lineare"].get("metriche_test", {}).get("mape", 0))
                    }
                },
                "random_forest": {
                    "feature_importance": {
                        "lunghezza": float(
                            risultati_ml["Random Forest"].get("feature_importance", {}).get("Lunghezza", 0)),
                        "orario": float(risultati_ml["Random Forest"].get("feature_importance", {}).get("Orario", 0)),
                        "affollamento": float(
                            risultati_ml["Random Forest"].get("feature_importance", {}).get("Affollamento", 0))
                    },
                    "train": {
                        "mae": float(risultati_ml["Random Forest"].get("metriche_train", {}).get("mae", 0)),
                        "rmse": float(risultati_ml["Random Forest"].get("metriche_train", {}).get("rmse", 0)),
                        "r2": float(risultati_ml["Random Forest"].get("metriche_train", {}).get("r2", 0)),
                        "mape": float(risultati_ml["Random Forest"].get("metriche_train", {}).get("mape", 0))
                    },
                    "test": {
                        "mae": float(risultati_ml["Random Forest"].get("metriche_test", {}).get("mae", 0)),
                        "rmse": float(risultati_ml["Random Forest"].get("metriche_test", {}).get("rmse", 0)),
                        "r2": float(risultati_ml["Random Forest"].get("metriche_test", {}).get("r2", 0)),
                        "mape": float(risultati_ml["Random Forest"].get("metriche_test", {}).get("mape", 0))
                    },
                    "parametri": {
                        "numero_alberi": 100,
                        "profondita_massima": 10,
                        "seed": self.seed
                    }
                }
            }
        except Exception as e:
            print(f"Avviso: impossibile salvare metriche ML complete: {e}")
            self.risultati_ml_completi = {
                "dataset": {
                    "num_campioni_totali": len(X),
                    "num_train": len(X_train),
                    "num_test": len(X_test),
                    "test_size": 0.2
                },
                "nota": "Metriche ML non disponibili nella struttura attesa"
            }

        # Calcola costi statici (baseline)
        print("\nCalcolo costi statici (baseline)...")
        self.costi_statici = calcola_costi_statici(self.grafo, self.simulatore)
        print(f"Costi statici calcolati per {len(self.costi_statici)} archi")

        # Prepara euristica euclidea
        print("\nPreparazione euristica euclidea...")
        posizioni_metriche = ottieni_posizioni_grafo_complesso()
        self.euristica_euclidea = euristica_distanza_euclidea(
            posizioni_metriche,
            velocita_ottimistica=2.0
        )
        print(f"Euristica euclidea preparata per {len(posizioni_metriche)} nodi")

        return risultati_ml

    # Esegue test di pianificazione con configurazioni diverse
    def fase_2_esperimenti_pianificazione(self, num_test: int = 50, start: str = "Ingresso", goal: str = "Reparto"):

        print("\n" + "=" * 70)
        print(f"FASE 2: ESPERIMENTI DI PIANIFICAZIONE ({num_test} test)")
        print("=" * 70)
        print("Configurazioni: statico, statico+euristica, ML lineare, ML RF")

        # Calcola il costo reale dei percorsi, confronta con il costo stimato e calcola il GAP
        calcolatore = CalcolatoreMetriche(self.grafo, self.simulatore)

        # Configurazioni da testare
        configurazioni = ["statico", "statico_euclidea", "ml_lineare", "ml_rf"]

        # Crea una lista di risultati per ogni configurazione
        for config in configurazioni:
            self.metriche_per_config[config] = []

        # Reset condizioni test
        self._condizioni_test = []

        # Esegui test
        for i in range(num_test):
            # Stampa la scritta test
            if (i + 1) % 10 == 0:
                print(f"  Test {i + 1}/{num_test}...")

            # Genera condizioni casuali per questo test

            # Ogni test ha condizioni diverse ma ripetibili
            np.random.seed(self.seed + i)
            orario = np.random.randint(0, 24)
            affollamento = np.random.uniform(0, 1)

            # Memorizzo le condizioni
            self._condizioni_test.append({
                'orario': orario,
                'affollamento': affollamento
            })

            # Trova percorso ottimo reale (ground truth), uso A* con costo reale
            _, costo_ottimo = calcolatore.trova_percorso_ottimo_reale(
                start, goal, orario, affollamento
            )

            # 1. STATICO (h=0), usa il costo medio dell'arco
            astar_statico = RicercaAStar(
                self.grafo,
                costo_statico_da_dizionario(self.costi_statici),
                euristica_nulla
            )
            # A* esplora il grafo e trova un percorso
            ris_statico = astar_statico.pianifica(start, goal)

            # Ricalcolo il costo reale vero
            if ris_statico.successo:
                metriche = calcolatore.calcola_metriche_percorso(
                    ris_statico, "statico", costo_ottimo, orario, affollamento
                )
                # Confronto con quello stimato e calcolo errore gap dell'ottimo nodi espansi e tempo
                self.metriche_per_config["statico"].append(metriche)

            # 2. STATICO + EURISTICA: Stesso costo finale, meno nodi esplorati
            astar_euclidea = RicercaAStar(
                self.grafo,
                costo_statico_da_dizionario(self.costi_statici),
                self.euristica_euclidea
            )
            ris_euclidea = astar_euclidea.pianifica(start, goal)

            if ris_euclidea.successo:
                metriche = calcolatore.calcola_metriche_percorso(
                    ris_euclidea, "statico_euclidea", costo_ottimo, orario, affollamento
                )
                self.metriche_per_config["statico_euclidea"].append(metriche)

            # 3. ML LINEARE
            # Il modello diventa una funzione di costo adattandosi alle condizioni correnti
            funzione_ml_lin = crea_funzione_costo_ml_dinamica(
                self.modelli["lineare"]
            )(orario, affollamento)

            astar_ml_lin = RicercaAStar(
                self.grafo,
                funzione_ml_lin,
                euristica_nulla
            )
            ris_ml_lin = astar_ml_lin.pianifica(start, goal)

            if ris_ml_lin.successo:
                metriche = calcolatore.calcola_metriche_percorso(
                    ris_ml_lin, "ml_lineare", costo_ottimo, orario, affollamento
                )
                self.metriche_per_config["ml_lineare"].append(metriche)

            # 4. ML RANDOM FOREST
            funzione_ml_rf = crea_funzione_costo_ml_dinamica(
                self.modelli["rf"]
            )(orario, affollamento)

            astar_ml_rf = RicercaAStar(
                self.grafo,
                funzione_ml_rf,
                euristica_nulla
            )
            ris_ml_rf = astar_ml_rf.pianifica(start, goal)

            if ris_ml_rf.successo:
                metriche = calcolatore.calcola_metriche_percorso(
                    ris_ml_rf, "ml_rf", costo_ottimo, orario, affollamento
                )
                self.metriche_per_config["ml_rf"].append(metriche)

        print(f"\nTest completati!")
        for config, metriche_list in self.metriche_per_config.items():
            print(f"  {config}: {len(metriche_list)} successi")

    # Analizza e confronta i risultati
    def fase_3_analisi_risultati(self):

        print("\n" + "=" * 70)
        print("FASE 3: ANALISI RISULTATI")
        print("=" * 70)

        calcolatore = CalcolatoreMetriche(self.grafo, self.simulatore)

        # Aggrega metriche
        print("\n### STATISTICHE AGGREGATE ###\n")
        for config, metriche_list in self.metriche_per_config.items():

            if metriche_list:
                agg = calcolatore.aggrega_metriche(metriche_list)
                # Salva i risultati e dopo li scriviamo nel JSON
                self.risultati_aggregati[config] = agg
                print(agg)
                print()

        # Confronta statico con statico euclideo misura riduzione di nodi e differenza di costo
        analisi_euristica = self._analizza_euristica(calcolatore)

        # Confronta ml con statico
        analisi_ml_lineare, analisi_ml_rf = self._analizza_ml(calcolatore)

        # In quale condizioni vince e in quale perde (affollamento medio, orari tipici, risparmi o penalità)
        vittorie_sconfitte = self._analizza_vittorie_sconfitte()

        # Salva tutte le analisi
        self.analisi_complete = {
            "euristica": analisi_euristica,
            "ml_lineare_vs_statico": analisi_ml_lineare,
            "ml_rf_vs_statico": analisi_ml_rf,
            "vittorie_sconfitte": vittorie_sconfitte
        }

    # Analizza impatto euristica euclidea
    def _analizza_euristica(self, calcolatore):
        print("\n" + "=" * 70)
        print("ANALISI EURISTICA: Statico vs Statico+Euclidea")
        print("=" * 70)

        # Se una configurazione non ha prodotto risultati non confronto nulla
        if "statico" not in self.metriche_per_config or "statico_euclidea" not in self.metriche_per_config:
            return None

        # Sto usando solo per confrontare euristica con no-euristica
        analisi = calcolatore.analisi_quando_ml_aiuta(
            self.metriche_per_config["statico"],
            self.metriche_per_config["statico_euclidea"]
        )

        print("\n### IMPATTO EURISTICA EUCLIDEA ###")
        # Quante volte A* euclideo ha trovato un costo migliore
        print(f"  Migliore nel costo: {analisi['percentuale_ml_migliore_costo']:.1f}%")
        print(f"  Migliore nell'efficienza: {analisi['percentuale_ml_migliore_efficienza']:.1f}%")

        # Lo normalizzo sul numero medio di nodi statici
        print(f"  Riduzione nodi media: {-analisi['risparmio_nodi_medio']:.1f} nodi "
              f"({(-analisi['risparmio_nodi_medio'] / self.risultati_aggregati['statico'].nodi_espansi_medio) * 100:.1f}%)")

        # Se la differenza di costo<0.1
        diff_costo = abs(analisi['risparmio_costo_medio'])
        if diff_costo < 0.1:
            print(
                f"Ottimalità preservata (stesso costo finale), l'euristica riduce il costo computazionale senza degradare la soluzione")
        else:
            print(f"Differenza costo: {diff_costo:.2f}s")

        return analisi

    def _analizza_ml(self, calcolatore):
        print("\n" + "=" * 70)
        print("ANALISI ML: ML vs STATICO")
        print("=" * 70)

        analisi_lineare = None
        analisi_rf = None

        # ML Lineare
        if "ml_lineare" in self.metriche_per_config and "statico" in self.metriche_per_config:
            print("\n### ML LINEARE vs STATICO ###")
            analisi_lineare = calcolatore.analisi_quando_ml_aiuta(
                self.metriche_per_config["statico"],
                self.metriche_per_config["ml_lineare"]
            )
            self._stampa_analisi_comparativa(analisi_lineare)

        # Random Forest
        if "ml_rf" in self.metriche_per_config and "statico" in self.metriche_per_config:
            print("\n### RANDOM FOREST vs STATICO ###")
            analisi_rf = calcolatore.analisi_quando_ml_aiuta(
                self.metriche_per_config["statico"],
                self.metriche_per_config["ml_rf"]
            )
            self._stampa_analisi_comparativa(analisi_rf)

        return analisi_lineare, analisi_rf

    # Analizza quando ML vince vs quando ML perde
    def _analizza_vittorie_sconfitte(self):

        print("\n" + "=" * 70)
        print("ANALISI: Quando ML Vince vs Perde")
        print("=" * 70)

        # Controllo se esistono i dati, quindi se ho entrambe le configurazioni
        if "statico" not in self.metriche_per_config or "ml_rf" not in self.metriche_per_config:
            print("Dati insufficienti per analisi")
            return None

        # Esistono le condizioni? Quindi affollamento e orario
        if not hasattr(self, '_condizioni_test') or not self._condizioni_test:
            print("Condizioni test non salvate - analisi non disponibile")
            return None

        # Due liste di casi concreti
        ml_vince = []
        ml_perde = []

        # Prende gli stessi test con zip
        for i, (m_static, m_ml) in enumerate(zip(
                self.metriche_per_config["statico"],
                self.metriche_per_config["ml_rf"]
        )):
            # Controlla che non ci siano disallineamenti
            if i >= len(self._condizioni_test):
                break

            # Recupera le condizioni di test: orario e affollamento
            cond = self._condizioni_test[i]
            diff = m_static.costo_reale - m_ml.costo_reale

            if diff > 0:  # ML costa meno, vince
                ml_vince.append({
                    'crowd': cond['affollamento'],
                    'orario': cond['orario'],
                    'saving': diff  # quanto tempo ha risparmiato
                })
            else:  # Statico costa meno, ML perde
                ml_perde.append({
                    'crowd': cond['affollamento'],
                    'orario': cond['orario'],
                    'penalty': -diff  # tempo perso (è negativo ma con meno davanti diventa positivo)
                })

        total = len(ml_vince) + len(ml_perde)

        if total == 0:
            print("Nessun dato disponibile")
            return None

        # Ml vince in quale percentuale di casi?
        print(f"\n### ML RANDOM FOREST VINCE ({len(ml_vince)}/{total} = {len(ml_vince) / total * 100:.1f}%) ###")

        stats_vince = None
        # Dataset secondario dati vincenti
        if ml_vince:
            crowds = [v['crowd'] for v in ml_vince]  # Prende solo l'affollamento
            orari = [v['orario'] for v in ml_vince]  # Prende solo le fasce orarie
            savings = [v['saving'] for v in ml_vince]  # Prende solo il tempo risparmiato

            # mean: media std: deviazione standard
            print(f"  Affollamento: {np.mean(crowds):.2f} ± {np.std(crowds):.2f} "
                  f"[{np.min(crowds):.2f}-{np.max(crowds):.2f}]")
            print(f"  Orario medio: {np.mean(orari):.1f}h")
            print(f"  Risparmio: {np.mean(savings):.2f}s ± {np.std(savings):.2f}s "
                  f"(max: {np.max(savings):.2f}s)")

            stats_vince = {
                "num_casi": len(ml_vince),
                "percentuale": len(ml_vince) / total * 100,
                "affollamento": {
                    "medio": float(np.mean(crowds)),
                    "std": float(np.std(crowds)),
                    "min": float(np.min(crowds)),
                    "max": float(np.max(crowds))
                },
                "orario": {
                    "medio": float(np.mean(orari)),
                    "std": float(np.std(orari))
                },
                "risparmio": {
                    "medio": float(np.mean(savings)),
                    "std": float(np.std(savings)),
                    "min": float(np.min(savings)),
                    "max": float(np.max(savings))
                }
            }

        # Ml perde
        print(f"\n### ML RANDOM FOREST PERDE ({len(ml_perde)}/{total} = {len(ml_perde) / total * 100:.1f}%) ###")

        stats_perde = None
        if ml_perde:
            crowds = [p['crowd'] for p in ml_perde]
            orari = [p['orario'] for p in ml_perde]
            penalties = [p['penalty'] for p in ml_perde]

            print(f"  Affollamento: {np.mean(crowds):.2f} ± {np.std(crowds):.2f} "
                  f"[{np.min(crowds):.2f}-{np.max(crowds):.2f}]")
            print(f"  Orario medio: {np.mean(orari):.1f}h")
            print(f"  Penalità: {np.mean(penalties):.2f}s ± {np.std(penalties):.2f}s "
                  f"(max: {np.max(penalties):.2f}s)")

            stats_perde = {
                "num_casi": len(ml_perde),
                "percentuale": len(ml_perde) / total * 100,
                "affollamento": {
                    "medio": float(np.mean(crowds)),
                    "std": float(np.std(crowds)),
                    "min": float(np.min(crowds)),
                    "max": float(np.max(crowds))
                },
                "orario": {
                    "medio": float(np.mean(orari)),
                    "std": float(np.std(orari))
                },
                "penalita": {
                    "media": float(np.mean(penalties)),
                    "std": float(np.std(penalties)),
                    "min": float(np.min(penalties)),
                    "max": float(np.max(penalties))
                }
            }

        return {
            "total_casi": total,
            "ml_vince": stats_vince,
            "ml_perde": stats_perde
        }

    # Stampa analisi
    def _stampa_analisi_comparativa(self, analisi: dict):
        print(f"  ML migliore (costo): {analisi['percentuale_ml_migliore_costo']:.1f}%")
        print(f"  ML migliore (efficienza): {analisi['percentuale_ml_migliore_efficienza']:.1f}%")
        print(f"  Risparmio costo medio: {analisi['risparmio_costo_medio']:.2f}s "
              f"(±{analisi['risparmio_costo_std']:.2f}s)")
        print(f"  Risparmio nodi medio: {analisi['risparmio_nodi_medio']:.1f} "
              f"(±{analisi['risparmio_nodi_std']:.1f})")

    # Salva i risultati in JSON
    def salva_risultati(self, output_dir: str = "results"):

        # Crea la cartella se non esiste
        os.makedirs(output_dir, exist_ok=True)

        # Costruisce il file path
        filepath = os.path.join(
            output_dir,
            f"{self.nome}_{self.timestamp}.json"
        )

        # Costruisce il dizionario completo con tutti i dati
        dati = {
            "esperimento": self.nome,
            "timestamp": self.timestamp,

            # CONFIGURAZIONE
            "configurazione": {
                "seed": self.seed,
                "grafo": {
                    "tipo": "complesso",
                    "num_nodi": len(self.grafo.ottieni_nodi()),
                    "num_archi": len(self.costi_statici) if hasattr(self, 'costi_statici') else 0
                },
                "simulatore": {
                    "modello_congestione": self.simulatore.modello_congestione,
                    "probabilita_evento": self.simulatore.probabilita_evento,
                    "magnitudo_eventi": self.simulatore.magnitudo_eventi,
                    "rumore_std": self.simulatore.rumore_std
                },
                "num_test": len(self.metriche_per_config.get("statico", []))
            },

            # RISULTATI ML (R2, MAE, RMSE, coefficienti, feature importance)
            "risultati_ml": self.risultati_ml_completi,

            # RISULTATI AGGREGATI
            "risultati_aggregati": {},

            # ANALISI COMPLETE
            "analisi": self.analisi_complete
        }

        # Viene riempito per statico, statico euclideo ml lineare ed ml rf
        for config, agg in self.risultati_aggregati.items():
            dati["risultati_aggregati"][config] = {
                "configurazione": config,
                "costo_reale_medio": agg.costo_reale_medio,
                "costo_reale_std": agg.costo_reale_std,
                "costo_reale_min": agg.costo_reale_min,
                "costo_reale_max": agg.costo_reale_max,
                "gap_medio": agg.gap_medio,
                "gap_std": agg.gap_std,
                "gap_max": agg.gap_max,
                "percentuale_ottimi": agg.percentuale_ottimi,
                "nodi_espansi_medio": agg.nodi_espansi_medio,
                "nodi_espansi_std": agg.nodi_espansi_std,
                "tempo_medio": agg.tempo_medio,
                "tempo_std": agg.tempo_std,
                "errore_stima_medio": agg.errore_stima_medio,
                "errore_stima_std": agg.errore_stima_std
            }

        # Json leggibile e chiusura sicura del file
        with open(filepath, 'w') as f:
            json.dump(dati, f, indent=2)

        print(f"\nRisultati salvati in: {filepath}")

    # Esegue il tutto
    def esegui_completo(self, num_test: int = 50):

        self.fase_1_preparazione_dati()
        self.fase_2_esperimenti_pianificazione(num_test=num_test)
        self.fase_3_analisi_risultati()
        self.salva_risultati()

        print("\n" + "=" * 70)
        print("ESPERIMENTO COMPLETATO!")
        print("=" * 70)


def scenario_normale():
    print("\n" + "=" * 70)
    print("SCENARIO NORMALE: Variabilità Moderata")
    print("\n" + "=" * 70)

    grafo = crea_grafo_complesso()
    sim = SimulatoreCosti(
        modello_congestione="quadratico",
        probabilita_evento=0.03,
        magnitudo_eventi=(1.1, 1.4),
        rumore_std=0.06,
        seed=42
    )

    exp = EsperimentoCompleto("scenario_normale", grafo, sim, seed=42)
    # Lancia l'esperimento
    exp.esegui_completo(num_test=50)


def scenario_estremo():
    print("\n" + "=" * 70)
    print("SCENARIO ESTREMO: Alta Variabilità")
    print("\n" + "=" * 70)

    grafo = crea_grafo_complesso()
    sim = SimulatoreCosti(
        modello_congestione="quadratico",
        probabilita_evento=0.10,
        magnitudo_eventi=(1.3, 1.8),
        rumore_std=0.12,
        seed=42
    )

    exp = EsperimentoCompleto("scenario_estremo", grafo, sim, seed=42)
    exp.esegui_completo(num_test=50)


# Esegue gli scenari e li confronta
def confronta_scenari():
    print("\n" + "=" * 70)
    print("ESECUZIONE ESPERIMENTI COMPARATIVI")
    print("=" * 70)

    # Esegui entrambi
    scenario_normale()
    scenario_estremo()

    print("\n" + "=" * 70)
    print("TUTTI GLI ESPERIMENTI COMPLETATI")
    print("=" * 70)
    print("\nControlla la cartella 'results/' per i file JSON con i risultati dettagliati")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Esegui esperimenti H.E.A.R.T")
    parser.add_argument(
        "--scenario",
        type=str,
        default="entrambi",
        choices=["normale", "estremo", "entrambi"],
        help="Quale scenario eseguire"
    )
    parser.add_argument(
        "--num-test",
        type=int,
        default=50,
        help="Numero di test per scenario"
    )

    args = parser.parse_args()

    if args.scenario == "normale":
        scenario_normale()
    elif args.scenario == "estremo":
        scenario_estremo()
    elif args.scenario == "entrambi":
        confronta_scenari()
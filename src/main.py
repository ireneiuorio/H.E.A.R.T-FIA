
import time
import random
import numpy as np
from src.core.grafo import crea_grafo_complesso, ottieni_posizioni_grafo_complesso
from src.core.simulator import SimulatoreCosti, calcola_costi_statici
from src.core.astar import RicercaAStar, euristica_nulla, euristica_distanza_euclidea, costo_statico_da_dizionario
from src.ml.dataset import GeneratoreDataset, split_train_test
from src.ml.modelli import (
    ModelloRegressioneLineare,
    ModelloRandomForest,
    crea_funzione_costo_ml_dinamica
)
from src.evaluation.metriche import CalcolatoreMetriche
from src.visualization.visualizzatore_pygame import VisualizzatoreGrafo, crea_posizioni_grafo_complesso

#Demo
def main():

    #Seed casuale, ogni esecuzione è diversa
    #Ogni volta che lancio la demo cambiano orario affollamento ed eventi casuali
    seed = int(time.time() * 1000) % 10000
    random.seed(seed)
    np.random.seed(seed)

    print("\n" + "=" * 70)
    print("H.E.A.R.T - Hospital Environment Adaptive Routing Technique")
    print("=" * 70)
    print(f"Seed: {seed} (risultati diversi ad ogni esecuzione)")

    #Setup ambiente
    print("\n1. Creazione ambiente...")
    grafo = crea_grafo_complesso()
    #probabilità evento 10%
    sim = SimulatoreCosti(modello_congestione="quadratico", probabilita_evento=0.10, seed=seed)
    print(f"Grafo: {len(grafo.ottieni_nodi())} nodi")
    print(f"Simulatore: modello quadratico")

    #Addestra ML
    print("\n2. Addestramento ML")
    #Generazione Dataset che copre tutto
    gen = GeneratoreDataset(grafo, sim)
    X, y = gen.genera_stratificato(campioni_per_cella=30, seed=seed)
    X_train, X_test, y_train, y_test = split_train_test(X, y, seed=seed)

    #Addestramento dei modelli
    modello_lin = ModelloRegressioneLineare()
    modello_lin.addestra(X_train, y_train)

    modello_rf = ModelloRandomForest(seed=seed)
    modello_rf.addestra(X_train, y_train)

    metriche_ml = modello_rf.valuta(X_test, y_test)
    print(f"Modelli addestrati su {len(X)} campioni")
    print(f"RF - MAE: {metriche_ml['mae']:.2f}s, R²: {metriche_ml['r2']:.3f}")

    #Costi statici
    print("\n3. Calcolo costi statici")
    costi_statici = calcola_costi_statici(grafo, sim)
    print(f"Costi statici per {len(costi_statici)} archi")

    #Preparazione euristiche
    print("\n4. Preparazione euristiche")

    # Posizioni metriche dei nodi
    posizioni_metriche = ottieni_posizioni_grafo_complesso()
    print(f"Posizioni caricate per {len(posizioni_metriche)} nodi")

    # Euristica euclidea calibrata
    euristica_euclidea_func = euristica_distanza_euclidea(
        posizioni_metriche,
        velocita_ottimistica=3.5
    )

    print(f"Euristica euclidea")
    print(f" Velocità ottimistica: 2.0 m/s")
    print(f"Velocità reale simulatore: 1.4 m/s")
    print(f"Sottostima garantita: ~30%")

    # 5. Scenario di test
    print("\n5. Scenario di test:")
    start, goal = "Ingresso", "Reparto"

    orario = np.random.randint(8, 18)
    affollamento = np.random.uniform(0.70, 0.99)

    print(f"   Percorso: {start} → {goal}")
    print(f"   Orario: {orario:02d}:00")
    print(f"   Affollamento: {affollamento:.0%}")

    if affollamento > 0.85:
        print(f"ALTO affollamento - ML potrebbe scegliere percorsi alternativi")


    # 6. Pianificazione con A*
    print("\n6. Pianificazione con A*...")

    calcolatore = CalcolatoreMetriche(grafo, sim)
    _, costo_ottimo = calcolatore.trova_percorso_ottimo_reale(start, goal, orario, affollamento)

    # STATICO (h=0)
    astar_statico = RicercaAStar(grafo, costo_statico_da_dizionario(costi_statici), euristica_nulla)
    ris_statico = astar_statico.pianifica(start, goal)
    metr_statico = calcolatore.calcola_metriche_percorso(ris_statico, "statico", costo_ottimo, orario, affollamento)

    # STATICO CON EURISTICA EUCLIDEA (h≠0)
    astar_euclidea = RicercaAStar(
        grafo,
        costo_statico_da_dizionario(costi_statici),
        euristica_euclidea_func
    )
    ris_euclidea = astar_euclidea.pianifica(start, goal)
    metr_euclidea = calcolatore.calcola_metriche_percorso(
        ris_euclidea, "statico_euclidea", costo_ottimo, orario, affollamento
    )

    # ML LINEARE
    funzione_lin = crea_funzione_costo_ml_dinamica(modello_lin)(orario, affollamento)
    astar_lin = RicercaAStar(grafo, funzione_lin, euristica_nulla)
    ris_lin = astar_lin.pianifica(start, goal)
    metr_lin = calcolatore.calcola_metriche_percorso(ris_lin, "ml_lineare", costo_ottimo, orario, affollamento)

    # ML RANDOM FOREST
    funzione_rf_final = crea_funzione_costo_ml_dinamica(modello_rf)(orario, affollamento)
    astar_rf = RicercaAStar(grafo, funzione_rf_final, euristica_nulla)
    ris_rf = astar_rf.pianifica(start, goal)
    metr_rf = calcolatore.calcola_metriche_percorso(ris_rf, "ml_rf", costo_ottimo, orario, affollamento)

    # 7. Risultati
    print("\n" + "=" * 70)
    print("RISULTATI")
    print("=" * 70)
    print(f"\n{'Configurazione':<20} {'Costo (s)':<12} {'Gap':<10} {'Nodi':<8} {'Percorso'}")
    print("-" * 70)
    print(f"{'OTTIMO':<20} {costo_ottimo:<12.2f} {'0.0%':<10} {'-':<8} (informazione perfetta)")

    # Stampa percorsi
    def format_percorso(perc):
        if len(perc) <= 4:
            return ' → '.join(perc)
        else:
            return f"{perc[0]} → {perc[1]} → ... → {perc[-2]} → {perc[-1]}"

    print(
        f"{'Statico (h=0)':<20} {metr_statico.costo_reale:<12.2f} {metr_statico.gap_ottimalita * 100:<9.1f}% {metr_statico.nodi_espansi:<8} {format_percorso(ris_statico.percorso)}")
    print(
        f"{'A* Euclidea':<20} {metr_euclidea.costo_reale:<12.2f} {metr_euclidea.gap_ottimalita * 100:<9.1f}% {metr_euclidea.nodi_espansi:<8} {format_percorso(ris_euclidea.percorso)}")
    print(
        f"{'ML Lineare':<20} {metr_lin.costo_reale:<12.2f} {metr_lin.gap_ottimalita * 100:<9.1f}% {metr_lin.nodi_espansi:<8} {format_percorso(ris_lin.percorso)}")
    print(
        f"{'ML Random Forest':<20} {metr_rf.costo_reale:<12.2f} {metr_rf.gap_ottimalita * 100:<9.1f}% {metr_rf.nodi_espansi:<8} {format_percorso(ris_rf.percorso)}")

    # Analisi efficienza euristica
    riduzione_nodi = (1 - metr_euclidea.nodi_espansi / metr_statico.nodi_espansi) * 100

    print("\n" + "=" * 70)
    print("ANALISI EURISTICA")
    print("=" * 70)
    print(f"Statico (h=0):     {metr_statico.nodi_espansi} nodi esplorati")
    print(f"A* Euclidea (h≠0): {metr_euclidea.nodi_espansi} nodi esplorati")
    print(f"Riduzione:         {riduzione_nodi:.1f}%")


    # Vincitore
    migliore = min(
        [("Statico", metr_statico.costo_reale),
         ("A* Euclidea", metr_euclidea.costo_reale),
         ("ML Lineare", metr_lin.costo_reale),
         ("ML Random Forest", metr_rf.costo_reale)],
        key=lambda x: x[1]
    )
    print(f"\nMigliore: {migliore[0]} ({migliore[1]:.2f}s)")

    # Analisi percorsi
    percorsi_unici = set()
    percorsi_unici.add(tuple(ris_statico.percorso))
    percorsi_unici.add(tuple(ris_euclidea.percorso))
    percorsi_unici.add(tuple(ris_lin.percorso))
    percorsi_unici.add(tuple(ris_rf.percorso))

    print(f"\n Analisi: {len(percorsi_unici)} percorsi diversi trovati")
    if len(percorsi_unici) == 1:
        print("Tutte le configurazioni hanno scelto lo stesso percorso")
    elif len(percorsi_unici) == 2:
        print(" Alcune configurazioni hanno scelto percorsi diversi!")
    else:
        print("Diverse configurazioni hanno scelto percorsi diversi!")

    # 8. Visualizzazione
    print("\n7. Apertura visualizzatore...")
    print("   Usa i tasti 1, 2, 3, 4 per cambiare configurazione")
    print("   Premi ESC per uscire\n")

    pos = crea_posizioni_grafo_complesso()
    viz = VisualizzatoreGrafo(grafo, pos)


#Visualizzatore
    percorsi_viz = {
        "statico": (
            ris_statico.percorso,
            f"Statico (h=0) - {metr_statico.costo_reale:.1f}s - {metr_statico.nodi_espansi} nodi",
            {
                "Costo": f"{metr_statico.costo_reale:.1f}s",
                "Nodi": metr_statico.nodi_espansi,
                "Euristica": "h=0"
            }
        ),
        "ml_euclidea": (
            ris_euclidea.percorso,
            f"A* Euclidea - {metr_euclidea.costo_reale:.1f}s - {metr_euclidea.nodi_espansi} nodi",
            {
                "Costo": f"{metr_euclidea.costo_reale:.1f}s",
                "Nodi": metr_euclidea.nodi_espansi,
                "Euristica": "Euclidea",
                "Riduzione": f"{riduzione_nodi:.1f}%"
            }
        ),
        "ml_lineare": (
            ris_lin.percorso,
            f"ML Lineare - {metr_lin.costo_reale:.1f}s - {metr_lin.nodi_espansi} nodi",{
                "Costo": f"{metr_lin.costo_reale:.1f}s",
                "Nodi": metr_lin.nodi_espansi,
                "Tipo": "ML"
            }
        ),
        "ml_rf": (
            ris_rf.percorso,
            f"ML RF - {metr_rf.costo_reale:.1f}s - {metr_rf.nodi_espansi} nodi",
            {
                "Costo": f"{metr_rf.costo_reale:.1f}s",
                "Gap": f"{metr_rf.gap_ottimalita * 100:+.1f}%",
                "Nodi": metr_rf.nodi_espansi,
                "Tipo": "ML"
            }
        )
    }

    viz.loop(percorsi_viz)

    print("\n" + "=" * 70)
    print("Per esperimenti completi: python experiments/run_experiments.py")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterruzione. Arrivederci!")
    except Exception as e:
        print(f"\nErrore: {e}")
        import traceback

        traceback.print_exc()


import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass, field

#Calcolo metriche di valutazione, serve a giudicare quello che A* ha fatto (con costi statici o Ml)



#con data class viene generato automaticamente l'init
@dataclass

#Scheda di valutazione per un singolo percorso trovato da A* con una configurazione di costo
class MetrichePercorso:
    # Identificativo configurazione
    configurazione: str  # es: "statico", "ml_lineare", "ml_rf"

    # Percorso
    percorso: List[str] #Sequenza di nodi trovati da A*
    lunghezza_percorso: int  # Numero di nodi

    # Costi
    costo_stimato: float  # Quello usato da A* per pianificare
    costo_reale: float  # Ground truth dal simulatore
    errore_stima: float  # |stimato - reale|
    errore_relativo: float  # errore / reale

    # Ottimalità
    costo_ottimo: float  # Costo del percorso ottimo reale
    gap_ottimalita: float  # (reale - ottimo) / ottimo

    # Efficienza computazionale
    nodi_espansi: int #quanti nodi ha davvero espanso
    nodi_generati: int #quanti nodi ha crato in totale
    tempo_esecuzione: float  # secondi, tempo di calcolo

    # Dettagli archi (per analisi fine)
    #Salvo per ogni arco del percorso
    dettagli_archi: List[Dict] = field(default_factory=list)

    #Stampa il risultato in modo leggibile
    def __str__(self) -> str:
        return (
            f"=== {self.configurazione} ===\n"
            f"Percorso: {' -> '.join(self.percorso)}\n"
            f"Costo stimato: {self.costo_stimato:.2f}s\n"
            f"Costo reale: {self.costo_reale:.2f}s\n"
            f"Errore stima: {self.errore_stima:.2f}s ({self.errore_relativo * 100:.1f}%)\n"
            f"Gap ottimalità: {self.gap_ottimalita * 100:.1f}%\n"
            f"Nodi espansi: {self.nodi_espansi}\n"
            f"Tempo: {self.tempo_esecuzione * 1000:.2f}ms"
        )


#Riassume molti test con la stessa configurazione
@dataclass
class MetricheAggregate:
   #Configurazione scleta
    configurazione: str
    num_test: int #numero di esperimenti aggregati

    # Statistiche costo reale
    costo_reale_medio: float
    costo_reale_std: float #quanto è stabile o variabile
    costo_reale_min: float
    costo_reale_max: float

    # Statistiche gap ottimalità
    gap_medio: float
    gap_std: float
    gap_max: float
    percentuale_ottimi: float  # % di volte che trova l'ottimo

    # Statistiche efficienza
    nodi_espansi_medio: float
    nodi_espansi_std: float
    tempo_medio: float
    tempo_std: float

    # Statistiche errore stima
    errore_stima_medio: float
    errore_stima_std: float

    def __str__(self) -> str:
        return (
            f"=== {self.configurazione} - Statistiche su {self.num_test} test ===\n"
            f"Costo reale: {self.costo_reale_medio:.2f} ± {self.costo_reale_std:.2f}s\n"
            f"Gap ottimalità: {self.gap_medio * 100:.1f}% ± {self.gap_std * 100:.1f}%\n"
            f"Soluzioni ottime: {self.percentuale_ottimi * 100:.1f}%\n"
            f"Nodi espansi: {self.nodi_espansi_medio:.1f} ± {self.nodi_espansi_std:.1f}\n"
            f"Tempo: {self.tempo_medio * 1000:.2f} ± {self.tempo_std * 1000:.2f}ms\n"
            f"Errore stima: {self.errore_stima_medio:.2f} ± {self.errore_stima_std:.2f}s"
        )


#Valuta quello che A* ha fatto
class CalcolatoreMetriche:

    def __init__(self, grafo, simulatore):

           # simulatore: Istanza SimulatoreCosti (per ground truth)

        self.grafo = grafo
        self.simulatore = simulatore

    #Calcola metriche per un singolo percorso
    def calcola_metriche_percorso(self,risultato_astar, configurazione: str, costo_ottimo: float,orario: int,affollamento: float) -> MetrichePercorso:
           # risultato_astar: RisultatoRicerca da A*
            #configurazione: Nome config
           # costo_ottimo: Costo del percorso ottimo reale
            #orario: Ora del test
            #affollamento: Affollamento del test

        percorso = risultato_astar.percorso

        # Calcola costo REALE del percorso usando il simulatore
        costo_reale, dettagli = self._calcola_costo_reale_percorso(
            percorso, orario, affollamento
        )

        # Errore di stima
        errore_stima = abs(risultato_astar.costo_stimato - costo_reale) #Errore assoluto in secondi
        errore_relativo = errore_stima / costo_reale if costo_reale > 0 else 0

        # Gap dall'ottimo
        gap = (costo_reale - costo_ottimo) / costo_ottimo if costo_ottimo > 0 else 0

        #creo oggetto metriche percorso
        return MetrichePercorso(
            configurazione=configurazione,
            percorso=percorso,
            lunghezza_percorso=len(percorso),
            costo_stimato=risultato_astar.costo_stimato,
            costo_reale=costo_reale,
            errore_stima=errore_stima,
            errore_relativo=errore_relativo,
            costo_ottimo=costo_ottimo,
            gap_ottimalita=gap,
            nodi_espansi=risultato_astar.nodi_espansi,
            nodi_generati=risultato_astar.nodi_generati,
            tempo_esecuzione=risultato_astar.tempo_esecuzione,
            dettagli_archi=dettagli
        )

    #Prende il percorso trovato da A* e calcola quanto costerebbe davvero nel mondo reale
    def _calcola_costo_reale_percorso(self,percorso: List[str],orario: int,affollamento: float) -> Tuple[float, List[Dict]]:
        costo_totale = 0.0
        dettagli = []

        #Scorro gli archi uno alla volta
        for i in range(len(percorso) - 1):
            nodo1 = percorso[i]
            nodo2 = percorso[i + 1]

            # Recupera info arco dal grafo
            arco_info = self.grafo.ottieni_arco(nodo1, nodo2)
            if arco_info is None:
                # Arco non esiste (non dovrebbe mai succedere)
                continue

            lunghezza, tipo = arco_info

            # Calcola tempo reale usando simulatore
            tempo_reale = self.simulatore.tempo_percorrenza(
                lunghezza, orario, affollamento, tipo
            )

            #Costo reale totale
            costo_totale += tempo_reale

            #Lista dettagliata archi
            dettagli.append({
                "da": nodo1,
                "a": nodo2,
                "lunghezza": lunghezza,
                "tipo": tipo,
                "tempo_reale": tempo_reale
            })

        return costo_totale, dettagli #restituisce il costo totale e la lista dettagliata degli archi


    #Serve a trovare il meglio possibile, percorso con costo reale minore
    #Restituisce il percorso ottimo e il costo reale
    #Usa A* con i costi Reali del simulatore
    def trova_percorso_ottimo_reale(
            self,
            start: str,
            goal: str,
            orario: int,
            affollamento: float
    ) -> Tuple[List[str], float]:

        from src.core.astar import RicercaAStar, euristica_nulla

        # Funzione costo che usa direttamente il simulatore, il costo di ogni arco è quello reale
        def costo_reale_oracolo(n1, n2, lunghezza, tipo):
            return self.simulatore.tempo_percorrenza(
                lunghezza, orario, affollamento, tipo
            )

        #costruzione a* com informazione perfetta
        astar = RicercaAStar(self.grafo, costo_reale_oracolo, euristica_nulla)
        risultato = astar.pianifica(start, goal)

        #Se non esiste restituisce costo infinito
        if not risultato.successo:
            return None, float('inf')

        # Calcola costo reale (dovrebbe coincidere con costo_stimato)
        costo_reale, _ = self._calcola_costo_reale_percorso(
            risultato.percorso, orario, affollamento
        )

        return risultato.percorso, costo_reale


    #Aggrega metriche di multipli test per una configurazione
    def aggrega_metriche(self,lista_metriche: List[MetrichePercorso]) -> MetricheAggregate:
        #Restituisce un oggetto riassuntivo

        if not lista_metriche:
            raise ValueError("Lista metriche vuota")

        #Tutti i test nella lista hanno al stessa configurazione quindi mi prendo il nome della configurazione
        configurazione = lista_metriche[0].configurazione

        # Estrai array e trasformo in liste semplci
        costi_reali = [m.costo_reale for m in lista_metriche]
        gaps = [m.gap_ottimalita for m in lista_metriche]
        nodi_espansi = [m.nodi_espansi for m in lista_metriche]
        tempi = [m.tempo_esecuzione for m in lista_metriche]
        errori_stima = [m.errore_stima for m in lista_metriche]

        # Percentuale ottimi (gap < 1%)
        #Scorre tutti i gap e per ogni gap<0.01 produce 1 e poi li somma
        num_ottimi = sum(1 for g in gaps if g < 0.01)

        return MetricheAggregate(
            configurazione=configurazione,
            num_test=len(lista_metriche),
            costo_reale_medio=np.mean(costi_reali),
            costo_reale_std=np.std(costi_reali),
            costo_reale_min=np.min(costi_reali),
            costo_reale_max=np.max(costi_reali),
            gap_medio=np.mean(gaps),
            gap_std=np.std(gaps),
            gap_max=np.max(gaps),
            percentuale_ottimi=num_ottimi / len(lista_metriche),
            nodi_espansi_medio=np.mean(nodi_espansi),
            nodi_espansi_std=np.std(nodi_espansi),
            tempo_medio=np.mean(tempi),
            tempo_std=np.std(tempi),
            errore_stima_medio=np.mean(errori_stima),
            errore_stima_std=np.std(errori_stima)
        )


    #Analizza in quali casi il ML batte il baseline statico.
    #Stessi scenari cambia solo il modello di costo
    def analisi_quando_ml_aiuta( self, metriche_statico: List[MetrichePercorso],metriche_ml: List[MetrichePercorso]) -> Dict:


      #controlla stesso numero di test
        assert len(metriche_statico) == len(metriche_ml), \
            "Devono esserci lo stesso numero di test"


    #Serve per calcolare la percentuale
        n = len(metriche_statico)

        # Confronti
        ml_migliore_costo = 0 #quante volte il mL trova un percorso più veloce
        ml_migliore_efficienza = 0 #quante volte il Ml espande meno nodi

        differenze_costo = []
        differenze_nodi = []

        for ms, mml in zip(metriche_statico, metriche_ml): #crea le coppie (s1, con M1) ecc
            # Costo reale
            diff_costo = ms.costo_reale - mml.costo_reale #Se positivo ml è migliore
            differenze_costo.append(diff_costo)

            if diff_costo > 0:  # ML trova percorso più veloce
                ml_migliore_costo += 1

            # Efficienza (meno nodi = meglio)
            diff_nodi = ms.nodi_espansi - mml.nodi_espansi
            differenze_nodi.append(diff_nodi)

            if diff_nodi > 0:  # ML espande meno nodi
                ml_migliore_efficienza += 1

        return {
            "percentuale_ml_migliore_costo": ml_migliore_costo / n * 100,
            "percentuale_ml_migliore_efficienza": ml_migliore_efficienza / n * 100,
            "risparmio_costo_medio": np.mean(differenze_costo),
            "risparmio_costo_std": np.std(differenze_costo),
            "risparmio_nodi_medio": np.mean(differenze_nodi),
            "risparmio_nodi_std": np.std(differenze_nodi),
        }


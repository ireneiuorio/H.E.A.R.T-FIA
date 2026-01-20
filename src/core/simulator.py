

import random
import numpy as np #cacloli matematici
from typing import Literal #solo uno

#Simula i tempo reale, rappresenta come funziona davvero l'ospedale
#Serve per addestrare i modelli di ML e per valutare a posteriori i percorsi trovati da A*
class SimulatoreCosti:


    def __init__(
            self,
            velocita_media: float = 1.4,  # m/s (velocità camminata adulto)
            modello_congestione: Literal["lineare", "quadratico", "soglia"] = "lineare", #cona affollamento impatta il tempo
            probabilita_evento: float = 0.05,  #5% evento imprevisto
            seed: int = None #riproducibilità della casualità
    ):

        self.velocita_media = velocita_media
        self.modello_congestione = modello_congestione
        self.probabilita_evento = probabilita_evento

        if seed is not None:
            #usa questo numero pe generare i numeri casuali
            random.seed(seed) #orario, affollamento, eventi
            np.random.seed(seed) #rumore,Ml,dataset,RandomForest

    def tempo_percorrenza( self, lunghezza: float, orario: int, affollamento: float, tipo_corridoio: str = "centrale" ) -> float:

       #Lunghezza
        tempo_base = lunghezza / self.velocita_media #tempo ideale
       #Orario
        fattore_orario = self._calcola_fattore_orario(orario) #ora di punta più lento
       #Affollamento
        fattore_affollamento = self._calcola_fattore_affollamento(affollamento, tipo_corridoio) #quanto rallento davvero
       #Tipo corridoio
        fattore_tipo = self._calcola_fattore_tipo(tipo_corridoio) #rallentamento strutturale


        fattore_eventi = 1.0
        rumore = 1.0

        #Calcolo finale, ogni fattore moltiplica
        tempo_totale = (
                tempo_base
                * fattore_orario
                * fattore_affollamento
                * fattore_tipo
                * fattore_eventi
                * rumore
        )

        #Non posso andare più veloce del 90% del tempo ideale
        return max(tempo_totale, tempo_base * 0.9)



    #A questa ora, quanto è più lento/veloce muoversi?
    def _calcola_fattore_orario(self, orario: int) -> float:
        if 7 <= orario <= 9 or 17 <= orario <= 19:
            return 1.4  # Ore di punta principali +40%
        elif 12 <= orario <= 14:
            return 1.2 #Ora di pranzo +20%
        elif 22 <= orario or orario <= 6:
            return 0.9  # Notte -10%
        else:
            return 1.0  # Orario normale




    #Dato quanta gente c'è e che tipo di corridoio è, di quanto aumenta il tempo di percorrenza?
    def _calcola_fattore_affollamento(self,affollamento: float,tipo_corridoio: str) -> float: #input affollamento base varia tra 0 e 1

        # Aggiusta affollamento per tipo corridoio
        affollamento_effettivo = self._aggiusta_affollamento_per_tipo(affollamento, tipo_corridoio)

        if self.modello_congestione == "lineare": #Lineare: impatto proporzionale
            # Impatto proporzionale: +0% a +100%
            return 1.0 + affollamento_effettivo

        elif self.modello_congestione == "quadratico": #Quadratico: impatto esponenziale ad alta densità
            return 1.0 + (affollamento_effettivo ** 2) * 1.5

        elif self.modello_congestione == "soglia":#Soglia: impatto solo sopra una certa densità, fino a un certo livello funziona normalmente, superato quel livello le prestazioni peggiorao
            soglia = 0.6
            if affollamento_effettivo < soglia:
                return 1.0
            else:
                eccesso = (affollamento_effettivo - soglia) / (1 - soglia)  #normalizzo l'eccesso dalla soglia
                return 1.0 + eccesso * 2.0 #lo moltiplico per due

        else:
            return 1.0 + affollamento_effettivo  # Default lineare



    #Modifica l'affollamento tenendo conto del tipo di corridoio
    def _aggiusta_affollamento_per_tipo( self, affollamento_base: float,tipo: str) -> float:
        if tipo == "centrale":
            return min(1.0, affollamento_base + 0.3) #aggiungo 0,3 ma non supero mai 1
        elif tipo == "isolato":
            return max(0.0, affollamento_base - 0.3)  #tolgo 0,3 ma non scendo sotto 0
        else:  # secondario
            return affollamento_base #Nesuna modifica



    #Indipendentemente dalla gente alcuni corridoi sono strutturalmente più lenti
    def _calcola_fattore_tipo(self, tipo: str) -> float:
        fattori = {
            "centrale": 1.1,  #Leggeremente più veloce
            "secondario": 1.0, #Normale
            "isolato": 0.95, #Leggermente più lento
            "normale": 1.0 #Normale
        }
        #Se il tipo non è riconosciuto uso 1
        return fattori.get(tipo, 1.0)


    #In media quanto tempo ci vuole ad attraversare questo corridoio?
    def stima_media( self,lunghezza: float,tipo: str,num_campioni: int = 100 ) -> dict:

       #Restituisce media,deviaizone standard, minimo, massimo e mediana

       #tempi simulati
        tempi = []
        for _ in range(num_campioni):
            orario = random.randint(0, 23)
            affollamento = random.uniform(0, 1)

            #Calcolo tempo reale
            tempo = self.tempo_percorrenza(lunghezza, orario, affollamento, tipo)
            tempi.append(tempo)

        return {
            "media": np.mean(tempi),
            "std": np.std(tempi),#quanto è instabile/variabile
            "min": np.min(tempi),
            "max": np.max(tempi),
            "mediana": np.median(tempi)
        }



#Per ogni corridoio del grafo qual è il costo medio reale?
#Il risultato è un dizionario che A* userà come costi statici
#Simulatore-> unico che conosce mondo reale
def calcola_costi_statici(grafo, simulatore: SimulatoreCosti) -> dict:

    costi = {}

#Scorre tutti i nodi del grafo
    for nodo in grafo.ottieni_nodi():
        #Per ogni nodo
        for vicino, lunghezza, tipo in grafo.ottieni_vicini(nodo):
            # Evita duplicati (archi bidirezionali) a->b = b->a
            chiave = tuple(sorted([nodo, vicino]))

            #Se arco non è ancora nel dizionario calcolo il costo
            if chiave not in costi:
                stats = simulatore.stima_media(lunghezza, tipo, num_campioni=200)
                costi[chiave] = stats["media"]

    return costi




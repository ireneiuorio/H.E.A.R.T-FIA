
#Implementazione algoritmo A*
import heapq #libreria per gestire code a priorità
import time #misurare il tempo
from typing import Callable, List, Optional, Tuple
#Callable qualsiasi oggetto chiama bile come una funzione


#Tutti i risultati di una ricerca
class RisultatoRicerca:

    def __init__(self):
        self.percorso: Optional[List[str]] = None   #percorso, lista di nodi
        self.costo_stimato: float = float('inf')   #costo totale a seconda della funzione usata
        self.nodi_espansi: int = 0 #numero di nodi espansi
        self.nodi_generati: int = 0 #numero totale di nodi generati (anche non espansi)
        self.tempo_esecuzione: float = 0.0 #tempo in secondi
        self.successo: bool = False #vero, se viene trovato un percorso

#Effettua la stampa
    def __str__(self) -> str:
        if not self.successo:
            return "Ricerca fallita: nessun percorso trovato"

        return (
            f"Percorso: {' -> '.join(self.percorso)}\n"
            f"Costo stimato: {self.costo_stimato:.2f}\n"
            f"Nodi espansi: {self.nodi_espansi}\n"
            f"Nodi generati: {self.nodi_generati}\n"
            f"Tempo: {self.tempo_esecuzione * 1000:.2f}ms"
        )



class RicercaAStar:

    def __init__(self, grafo1, funzione_costo: Callable[[str, str, float, str], float], euristica: Callable[[str, str], float]):
        self.grafo = grafo1
        self.funzione_costo = funzione_costo #Funzione costo reale arco (nodo corrente, nodo vicino, lunghezza,tipo)
        self.euristica = euristica #h(n) stimare il costo rimanente (nodo corrente, nodo obiettivo)



    def pianifica( self, nodo_iniziale: str,nodo_obiettivo: str) -> RisultatoRicerca:

        risultato = RisultatoRicerca()
        tempo_inizio = time.time()

        # Validazione input
        if nodo_iniziale not in self.grafo.ottieni_nodi():
            return risultato  # Fallimento
        if nodo_obiettivo not in self.grafo.ottieni_nodi():
            return risultato  # Fallimento

        # Caso base: start == goal
        if nodo_iniziale == nodo_obiettivo:
            risultato.percorso = [nodo_iniziale]
            risultato.costo_stimato = 0.0
            risultato.successo = True
            risultato.tempo_esecuzione = time.time() - tempo_inizio
            return risultato

        # Inizializzazione strutture dati
        # Frontiera: heap con (f, contatore, nodo)
        # Il contatore serve per evitare confronti tra nodi quando f è uguale
        frontiera = []
        contatore = 0

        #min-heap espanso prima quello a priorità più bassa, restituisce il più piccolo
        heapq.heappush(frontiera, (0, contatore, nodo_iniziale)) #Inserisce elemento in frontiera (priorità, contatore, nodo iniziale)
        #Il contatore serve quando due nodi hanno la stessa priorità, numero che rappresenta l'ordine di inserimento nella frontiera
        contatore += 1


        predecessore = {}  # Per ricostruire il percorso
        costo_g = {nodo_iniziale: 0}  # g(n): costo dal nodo iniziale mantiene il migliore trovato
        in_frontiera = {nodo_iniziale}  #Sapere se un nodo è già in frontiera

       #Finchè ci sono nodi da esplorare
        while frontiera:

            #estraiamo il nodo minimo ignorando f e contatore _
            _, _, nodo_corrente = heapq.heappop(frontiera)
           #non è più in frontiera
            in_frontiera.discard(nodo_corrente)

            risultato.nodi_espansi += 1

            # Se il nodo estratto
            if nodo_corrente == nodo_obiettivo:
                risultato.percorso = self._ricostruisci_percorso(predecessore, nodo_iniziale, nodo_obiettivo)
                risultato.costo_stimato = costo_g[nodo_obiettivo]
                risultato.successo = True
                risultato.tempo_esecuzione = time.time() - tempo_inizio
                return risultato

            # Esploro tutti gli archi uscenti generando nuovi candidati
            for vicino, lunghezza, tipo in self.grafo.ottieni_vicini(nodo_corrente):
                risultato.nodi_generati += 1

                # Calcola costo arco usando la funzione fornita
                costo_arco = self.funzione_costo( nodo_corrente, vicino, lunghezza, tipo )

                #g(vicino)=g(nodo_corrente)+ costo (nodo corrente->vicino)
                nuovo_costo_g = costo_g[nodo_corrente] + costo_arco

                # Se troviamo un percorso migliore (o nuovo)
                if vicino not in costo_g or nuovo_costo_g < costo_g[vicino]:
                    costo_g[vicino] = nuovo_costo_g

                    # Calcola f(n) = g(n) + h(n)
                    f = nuovo_costo_g + self.euristica(vicino, nodo_obiettivo)

                    # Aggiungi (o aggiorna) in frontiera
                    if vicino not in in_frontiera:
                        #il nodo entra tra i candidati
                        heapq.heappush(frontiera, (f, contatore, vicino))
                        contatore += 1
                        in_frontiera.add(vicino)

                    # Aggiorna predecessore: il miglior modo per arrivare a vicino è il nodo corrente
                    predecessore[vicino] = nodo_corrente

        # Nessun percorso trovato
        risultato.tempo_esecuzione = time.time() - tempo_inizio
        return risultato


    #Ricostruisce il percorso seguendo i predecessori
    def _ricostruisci_percorso( self,predecessore: dict,start: str,goal: str ) -> List[str]:
        percorso = [goal] #partiamo dal goal
        nodo = goal #nodo parte dal goal e andrà all'indietro

        while nodo != start: #finchè non raggiungo lo start
            nodo = predecessore[nodo]
            percorso.append(nodo) #aggiungi il nodo al percorso

        percorso.reverse() #inversione percorso
        return percorso



#h(n)=0 per ogni n: si comporta come Dijkstra/ ricerca a costo uniforme
#f(n)=g(n)
def euristica_nulla(nodo_corrente: str, nodo_obiettivo: str) -> float:
    return 0.0


#Funzione esterna che permette di configurare l'euristica
def euristica_distanza_euclidea(posizioni: dict, velocita_ottimistica: float = 2.0):
    #posizioni: coordinate in metri reali
    #velocità ottimistica di default

    def euristica(nodo_corrente: str, nodo_obiettivo: str) -> float:

      #Senza coordinate non posso stimare la distanza
        if nodo_corrente not in posizioni or nodo_obiettivo not in posizioni:
            return 0.0

        x1, y1 = posizioni[nodo_corrente]
        x2, y2 = posizioni[nodo_obiettivo]

        # Distanza euclidea in metri (linea d'aria)
        distanza_metri = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        # Tempo minimo IDEALE (ignora tutto)però
        tempo_stimato = distanza_metri / velocita_ottimistica

        return tempo_stimato

    return euristica


#Factory
#Trasforma un dizionario di costi in una funzione di costo
def costo_statico_da_dizionario(costi_medi: dict):

#(nodo1,nodo2,lunghezza,tipo)-->float

    def costo(n1: str, n2: str, lunghezza: float, tipo: str) -> float:
        #ordina sempre nello stesso modo perchè grafo non orientato a-b = b-a
        chiave = tuple(sorted([n1, n2]))
        #recupera il costo dal dizionario, se per qualche motivo l'arco non è nel dizionario restituisce la lunghezza
        return costi_medi.get(chiave, lunghezza)

    return costo



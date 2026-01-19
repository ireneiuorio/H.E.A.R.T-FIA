
#Rappresentazione dell'ambiente ospedaliero come grafo non orientato.


from typing import List, Tuple, Dict, Optional
import json


class Grafo:

    #ogni arco ha la lunghezza in metri e il tipo (centrale, secondario, isolato)

    #Costruttore
    def __init__(self):

        #lista di adiacenza
        #Dizionario dove la chiave è il nome del nodo
        #il valore è una lista dei suoi vicini tuple: (nome del nodo vicino, lunghezza del corridoio, tipo corridoio)
        self.adiacenza: Dict[str, List[Tuple[str, float, str]]] = {}


    #Funzione che aggiunge un nodo se non è già presente nel dizionario
    def aggiungi_nodo(self, nodo: str) -> None:
        if nodo not in self.adiacenza:
            self.adiacenza[nodo] = [] #lo aggiunge come lista vuota di vicini


    #aggiunge un arco bidirezionale tra due nodi
    #tipo: valore di default se non specificato usa centrale
    def aggiungi_arco( self, nodo1: str, nodo2: str, lunghezza: float, tipo: str = "centrale") -> None:
        #se non esistono li creo
        self.aggiungi_nodo(nodo1)
        self.aggiungi_nodo(nodo2)

        #arco bidirezionale
        self.adiacenza[nodo1].append((nodo2, lunghezza, tipo))
        self.adiacenza[nodo2].append((nodo1, lunghezza, tipo))


   #restituisce i vicini di un nodo
    def ottieni_vicini(self, nodo: str) -> List[Tuple[str, float, str]]:
       #.get cerca la chiave nel dizionario
        return self.adiacenza.get(nodo, [])

    #restituisce tutti i nodi del grafo
    def ottieni_nodi(self) -> List[str]:
        #.keys restituisce tutte le chiavi del dizionario
        return list(self.adiacenza.keys())


    #cerca l'arco tra due nodi (lunghezza, tipo)
    def ottieni_arco(self, nodo1: str, nodo2: str) -> Optional[Tuple[float, str]]:
        for vicino, lunghezza, tipo in self.ottieni_vicini(nodo1):
            if vicino == nodo2:
                return (lunghezza, tipo)
        return None



#crea un grafo semplice
def crea_grafo_semplice() -> Grafo:

    grafo = Grafo()

    # Percorso diretto (centrale, affollato)
    grafo.aggiungi_arco("Ingresso", "A", 10, "centrale")
    grafo.aggiungi_arco("A", "Reparto", 10, "centrale")

    # Percorso alternativo (più lungo ma meno affollato)
    grafo.aggiungi_arco("Ingresso", "B", 8, "secondario")
    grafo.aggiungi_arco("B", "C", 8, "secondario")
    grafo.aggiungi_arco("C", "Reparto", 8, "secondario")

    return grafo


 #crea un grafo complesso con più alternative
def crea_grafo_complesso() -> Grafo:

    grafo = Grafo()

    # Corridoio centrale (molto affollato)
    grafo.aggiungi_arco("Ingresso", "A", 5, "centrale")
    grafo.aggiungi_arco("A", "B", 8, "centrale")
    grafo.aggiungi_arco("B", "C", 8, "centrale")
    grafo.aggiungi_arco("C", "D", 8, "centrale")
    grafo.aggiungi_arco("D", "E", 8, "centrale")
    grafo.aggiungi_arco("E", "Reparto", 5, "centrale")

    # Percorsi secondari (meno affollati)
    grafo.aggiungi_arco("A", "F", 12, "secondario")
    grafo.aggiungi_arco("F", "G", 12, "secondario")
    grafo.aggiungi_arco("G", "C", 12, "secondario")

    grafo.aggiungi_arco("C", "H", 12, "secondario")
    grafo.aggiungi_arco("H", "I", 12, "secondario")
    grafo.aggiungi_arco("I", "E", 12, "secondario")

    # Percorso isolato (lungo ma poco affollato)
    grafo.aggiungi_arco("C", "J", 15, "isolato")
    grafo.aggiungi_arco("J", "K", 10, "isolato")
    grafo.aggiungi_arco("K", "L", 10, "isolato")
    grafo.aggiungi_arco("L", "Reparto", 10, "isolato")

    return grafo



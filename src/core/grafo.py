
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


    grafo.aggiungi_arco("Ingresso", "A", 10, "centrale")
    grafo.aggiungi_arco("A", "Reparto", 10, "centrale")

    # Percorso alternativo (più lungo ma meno affollato)
    grafo.aggiungi_arco("Ingresso", "B", 8, "secondario")
    grafo.aggiungi_arco("B", "C", 8, "secondario")
    grafo.aggiungi_arco("C", "Reparto", 8, "secondario")

    return grafo

def crea_grafo_complesso() -> Grafo:
    grafo = Grafo()


    grafo.aggiungi_arco("Ingresso", "A", 10, "centrale")
    grafo.aggiungi_arco("A", "B", 10, "centrale")
    grafo.aggiungi_arco("B", "C", 10, "centrale")
    grafo.aggiungi_arco("C", "D", 10, "centrale")
    grafo.aggiungi_arco("D", "Reparto", 10, "centrale")

    # Scorciatoie centrali (rischiose)
    grafo.aggiungi_arco("A", "C", 18, "centrale")
    grafo.aggiungi_arco("B", "D", 18, "centrale")


    for prefisso, y in [("N", 30), ("S", 70)]:
        grafo.aggiungi_arco("Ingresso", f"{prefisso}1", 12, "secondario")
        grafo.aggiungi_arco(f"{prefisso}1", f"{prefisso}2", 12, "secondario")
        grafo.aggiungi_arco(f"{prefisso}2", f"{prefisso}3", 12, "secondario")
        grafo.aggiungi_arco(f"{prefisso}3", f"{prefisso}4", 12, "secondario")
        grafo.aggiungi_arco(f"{prefisso}4", "Reparto", 12, "secondario")

    # Bypass interni ai secondari
    grafo.aggiungi_arco("N2", "N4", 20, "secondario")
    grafo.aggiungi_arco("S2", "S4", 20, "secondario")

    # Collegamenti centrale ↔ secondari
    grafo.aggiungi_arco("A", "N1", 8, "secondario")
    grafo.aggiungi_arco("A", "S1", 8, "secondario")
    grafo.aggiungi_arco("B", "N2", 8, "secondario")
    grafo.aggiungi_arco("B", "S2", 8, "secondario")
    grafo.aggiungi_arco("C", "N3", 8, "secondario")
    grafo.aggiungi_arco("C", "S3", 8, "secondario")
    grafo.aggiungi_arco("D", "N4", 8, "secondario")
    grafo.aggiungi_arco("D", "S4", 8, "secondario")

    # RIENTRI verso il centrale (fondamentali!)
    grafo.aggiungi_arco("N2", "B", 7, "centrale")
    grafo.aggiungi_arco("S2", "B", 7, "centrale")
    grafo.aggiungi_arco("N3", "C", 7, "centrale")
    grafo.aggiungi_arco("S3", "C", 7, "centrale")


 #T nord est e p Sud est
    for prefisso in ["E", "T", "P"]:
        grafo.aggiungi_arco("Ingresso", f"{prefisso}1", 16 if prefisso == "E" else 18, "isolato")
        grafo.aggiungi_arco(f"{prefisso}1", f"{prefisso}2", 16 if prefisso == "E" else 18, "isolato")
        grafo.aggiungi_arco(f"{prefisso}2", f"{prefisso}3", 16 if prefisso == "E" else 18, "isolato")
        grafo.aggiungi_arco(f"{prefisso}3", f"{prefisso}4", 16 if prefisso == "E" else 18, "isolato")
        grafo.aggiungi_arco(f"{prefisso}4", "Reparto", 16 if prefisso == "E" else 18, "isolato")

    # Collegamenti isolati ↔ secondari
    grafo.aggiungi_arco("N1", "E1", 10, "isolato")
    grafo.aggiungi_arco("S1", "E1", 10, "isolato")
    grafo.aggiungi_arco("C", "E2", 12, "isolato")
    grafo.aggiungi_arco("N3", "E3", 18, "isolato")
    grafo.aggiungi_arco("S3", "E3", 18, "isolato")

    # Collegamenti isolati interni
    grafo.aggiungi_arco("E1", "T1", 10, "isolato")
    grafo.aggiungi_arco("E1", "P1", 10, "isolato")
    grafo.aggiungi_arco("N2", "T2", 12, "isolato")
    grafo.aggiungi_arco("S2", "P2", 12, "isolato")
    grafo.aggiungi_arco("T2", "P2", 20, "isolato")

    # Rientro isolato → centrale (decisione tardiva!)
    grafo.aggiungi_arco("E3", "D", 14, "secondario")

    return grafo



#Coordinate per euristica
#Distanza in linea d'aria
#Asse x distanza Ingresso (0m) a Reparto (100m)
#Asse y distanza dal corridoio centrale
def ottieni_posizioni_grafo_complesso() -> Dict[str, Tuple[float, float]]:
    return {
        "Ingresso": (0, 50),
        "Reparto": (100, 50),

        # Centrale
        "A": (20, 50),
        "B": (40, 50),
        "C": (60, 50),
        "D": (80, 50),

        # Secondari Nord
        "N1": (20, 30),
        "N2": (40, 30),
        "N3": (60, 30),
        "N4": (80, 30),

        # Secondari Sud
        "S1": (20, 70),
        "S2": (40, 70),
        "S3": (60, 70),
        "S4": (80, 70),

        # Isolati Est
        "E1": (20, 10),
        "E2": (40, 10),
        "E3": (60, 10),
        "E4": (80, 10),

        # Isolati Sud-Est
        "T1": (20, -10),
        "T2": (40, -10),
        "T3": (60, -10),
        "T4": (80, -10),

        # Isolati Nord-Est
        "P1": (20, 90),
        "P2": (40, 90),
        "P3": (60, 90),
        "P4": (80, 90),
    }

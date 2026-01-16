class Grafo:

    #Rappresenta il grafo dell'ambiente ospedaliero.
    #I nodi sono punti dell'edificio, gli archi sono corridoi con una lunghezza fisica.

    def __init__(self):
        # Dizionario: nodo -> lista di (nodo_vicino, lunghezza)
        self.adiacenza = {}  #Dizionario

    #Aggiunge un nodo al grafo.
    def aggiungi_nodo(self, nodo):
        if nodo not in self.adiacenza:
            self.adiacenza[nodo] = []

    #Aggiunge un arco non orientato tra nodo1 e nodo2 con la lunghezza specificata.
    def aggiungi_arco(self, nodo1, nodo2, lunghezza):
        self.aggiungi_nodo(nodo1)
        self.aggiungi_nodo(nodo2)
        self.adiacenza[nodo1].append((nodo2, lunghezza))
        self.adiacenza[nodo2].append((nodo1, lunghezza))

    #Restituisce la lista dei vicini di un nodo sotto forma di (nodo, lunghezza).
    def ottieni_vicini(self, nodo):
        return self.adiacenza.get(nodo, [])

    #Restituisce la lista di tutti i nodi del grafo
    def ottieni_nodi(self):
        return list(self.adiacenza.keys())

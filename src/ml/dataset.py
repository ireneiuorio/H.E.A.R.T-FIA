


#Serve a creare esempi per insegnare a un modello ML quanto tempi ci vuole per percorrere un corridoio
import random
import numpy as np
from typing import List, Tuple, Literal


#Genera dati sintetici per addestrare il modello
class GeneratoreDataset:
    def __init__(self, grafo, simulatore):

        #Struttura del grafo
        self.grafo = grafo
        #Tempo reale impiegato
        self.simulatore = simulatore


#Per evitare di addestrare il modello su dataset sbilanciati, genera dataset per coprire uniformemente lo spazio
    def genera_stratificato(self,campioni_per_cella: int = 10,seed: int = None) -> Tuple[np.ndarray, np.ndarray]: #return (x,y)

        #Rende l'esperimento riproducibile utilizzando lo stesso seed->stesso dataset
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        X = [] #feature->[lunghezza,orario,affollamento]
        y = [] #target-> tempo reale

        # Definizione strati
        fasce_orarie = {
            "notte": [0, 1, 2, 3, 4, 5, 6, 22, 23],
            "giorno": [10, 11, 12, 13, 14, 15, 16],
            "picco": [7, 8, 9, 17, 18, 19]
        }

        livelli_affollamento = {
            "basso": (0.0, 0.3),
            "medio": (0.3, 0.7),
            "alto": (0.7, 1.0)
        }

        # Estrai archi raggruppati per tipo
        archi_per_tipo = self._raggruppa_archi_per_tipo()

        #Ogni tipo di corridoio, in ogni fascia oraria a ogni livello di affollamento
        for tipo, archi in archi_per_tipo.items():
            for fascia_nome, ore in fasce_orarie.items():
                for livello_nome, (aff_min, aff_max) in livelli_affollamento.items():

                    for _ in range(campioni_per_cella):
                        # Campiona da questa cella
                        lunghezza, tipo_arco = random.choice(archi)
                        orario = random.choice(ore)
                        affollamento = random.uniform(aff_min, aff_max)

                        #Impara dal simulatore
                        tempo_reale = self.simulatore.tempo_percorrenza(
                            lunghezza, orario, affollamento, tipo_arco
                        )

                        X.append([lunghezza, orario, affollamento])
                        y.append(tempo_reale)

        # Shuffle: serve per rompere l'ordine artificiale
        #mantenendo la coppia feature+target
        indices = np.arange(len(X))
        np.random.shuffle(indices) #scelgo l'ordine
        X = np.array(X)[indices] #mescolo x in base all'ordine scelto
        y = np.array(y)[indices] #mescolo y in base all'ordine scelto

        return X, y


    #Estrae ogni corridoio una sola volta (lunghezza, tipo), evitando duplicazioni dovute alla bidirezionalità
    def _estrai_archi(self) -> List[Tuple[float, str]]:
        archi = []
        visti = set() #insieme delle coppie di nodi già processate

        for nodo in self.grafo.ottieni_nodi(): #ciclo sui nodi
            for vicino, lunghezza, tipo in self.grafo.ottieni_vicini(nodo):#ciclo sui vicini
                chiave = tuple(sorted([nodo, vicino])) #inverte a->b=b->a
                if chiave not in visti: #se non lo hai mai visto
                    archi.append((lunghezza, tipo))
                    visti.add(chiave)
        return archi



    #Divide i corridoi per tipo
    def _raggruppa_archi_per_tipo(self) -> dict:

       #Dizionario->per ogni arco lunghezza e tipo

        archi = self._estrai_archi()
        raggruppati = {}

        #Per ogni corridoio guardo che tipo è
        for lunghezza, tipo in archi:

            #Ogni corridoio va nella sua lista all'interno del dizionario
            if tipo not in raggruppati:
                #Se non esiste la lista per quel tipo di corridoio la crea
                raggruppati[tipo] = []
            #Aggiunge alla giusta lista
            raggruppati[tipo].append((lunghezza, tipo))

        return raggruppati



#Divide il dataset in due parti, il modello non vede i dati di test durante l'addestramento
 #il 20% dei dati va nel test
def split_train_test( X: np.ndarray,y: np.ndarray, test_size: float = 0.2, seed: int = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:

    from sklearn.model_selection import train_test_split #Mescola i dati li divide in due parti e mantiene allineati X e Y
    return train_test_split(X, y, test_size=test_size, random_state=seed)#ottenere sempre la stessa divisione

#Restituisce X_train,X_test, Y_train, y_test

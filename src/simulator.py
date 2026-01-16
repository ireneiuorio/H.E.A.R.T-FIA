
import random


class SimulatoreCosti:

    """
    Simula il tempo reale di percorrenza di un corridoio
    in base a lunghezza, orario e livello di affollamento.
    """

    def __init__(self, velocita_media=1.4):
        """
        velocita_media: velocità media di camminata (m/s)
        """
        self.velocita_media = velocita_media

    def tempo_percorrenza(self, lunghezza, orario, affollamento):
        """
        Calcola il tempo reale di percorrenza di un corridoio.

        lunghezza: lunghezza del corridoio (metri)
        orario: ora del giorno (0-23)
        affollamento: valore tra 0 e 1
        """

        # tempo base (secondi)
        tempo_base = lunghezza / self.velocita_media

        # fattore orario (ore di punta)
        if 8 <= orario <= 10 or 17 <= orario <= 19:
            fattore_orario = 1.3
        else:
            fattore_orario = 1.0

        # fattore affollamento
        fattore_affollamento = 1 + affollamento

        # rumore casuale (realismo)
        rumore = random.uniform(0.9, 1.1)

        tempo_totale = tempo_base * fattore_orario * fattore_affollamento * rumore

        return tempo_totale

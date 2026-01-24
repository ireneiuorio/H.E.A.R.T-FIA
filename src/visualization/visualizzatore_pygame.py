
import pygame
import sys
import math
from typing import Dict, List, Tuple


#Visualizzatore del grafo
class VisualizzatoreGrafo:

    def __init__(self, grafo, posizioni: Dict[str, Tuple[int, int]]):

        pygame.init()
        self.schermo = pygame.display.set_mode((1000, 750))  #Crea una finestra
        pygame.display.set_caption("H.E.A.R.T - Visualizzatore Percorsi") #Titolo della finestra

        self.grafo = grafo
        self.posizioni = posizioni

        #Fluidità controllata
        self.clock = pygame.time.Clock()

        # Colori base
        self.BIANCO = (255, 255, 255)
        self.NERO = (0, 0, 0)
        self.GRIGIO_CHIARO = (220, 220, 220)
        self.GRIGIO_SCURO = (100, 100, 100)

        # Colori corridoi (pastello)
        self.ROSSO_CHIARO = (255, 200, 200)  # Centrale
        self.BLU_CHIARO = (180, 220, 255)  # Secondario
        self.VERDE_CHIARO = (200, 255, 200)  # Isolato

        # Colori percorsi - 4 CONFIGURAZIONI
        self.ARANCIONE_FORTE = (255, 127, 0)  # Statico (h=0)
        self.VIOLA_FORTE = (138, 43, 226)  # A* Euclidea (h≠0)
        self.ROSA_FORTE = (255, 20, 147)  # ML Lineare
        self.TEAL_FORTE = (0, 150, 136)  # ML RF

        self.font = pygame.font.Font(None, 26)
        self.font_small = pygame.font.Font(None, 18)
        self.font_title = pygame.font.Font(None, 38)


#Colore per tipo di corridoio
    def _colore_tipo(self, tipo: str) -> Tuple[int, int, int]:

        colori = {
            'centrale': self.ROSSO_CHIARO,
            'secondario': self.BLU_CHIARO,
            'isolato': self.VERDE_CHIARO,
            'normale': self.GRIGIO_CHIARO
        }
        return colori.get(tipo, self.GRIGIO_CHIARO)

#Riceve il tipo dell'algoritmo e restituisce il colore associato all'algoritmo
    def _colore_config(self, config: str) -> Tuple[int, int, int]:
        """Colore per configurazione."""
        colori = {
            'statico': self.ARANCIONE_FORTE,
            'ml_euclidea': self.VIOLA_FORTE,
            'ml_lineare': self.ROSA_FORTE,
            'ml_rf': self.TEAL_FORTE
        }
        return colori.get(config, self.NERO)


#Disegna una linea e orienta la freccia
    def _disegna_freccia(self, surface, colore, start, end, larghezza=8):

        pygame.draw.line(surface, colore, start, end, larghezza)

        dx = end[0] - start[0]
        dy = end[1] - start[1]
        lunghezza = math.sqrt(dx ** 2 + dy ** 2)

        if lunghezza == 0:
            return

        dx /= lunghezza
        dy /= lunghezza

        d = 18
        px = end[0] - dx * d
        py = end[1] - dy * d

        angolo = math.atan2(dy, dx)
        larghezza_freccia = 9

        p1 = end
        p2 = (
            px - larghezza_freccia * math.sin(angolo),
            py + larghezza_freccia * math.cos(angolo)
        )
        p3 = (
            px + larghezza_freccia * math.sin(angolo),
            py - larghezza_freccia * math.cos(angolo)
        )

        pygame.draw.polygon(surface, colore, [p1, p2, p3])


    #Disegna tutto lo schermo
    def disegna(self, percorso=None, titolo="", config="statico", metriche=None):

        self.schermo.fill(self.BIANCO)

        # Titolo
        testo_titolo = self.font_title.render("H.E.A.R.T", True, self.NERO)
        self.schermo.blit(testo_titolo, (20, 15))

        # Configurazione corrente
        testo_config = self.font.render(titolo, True, self._colore_config(config))
        self.schermo.blit(testo_config, (20, 55))

        # Disegna ogni corridoio una sola volta
        archi_disegnati = set()
        for nodo in self.grafo.ottieni_nodi():
            if nodo not in self.posizioni:
                continue
            for vicino, lunghezza, tipo in self.grafo.ottieni_vicini(nodo):
                if vicino not in self.posizioni:
                    continue

                arco = tuple(sorted([nodo, vicino]))
                if arco in archi_disegnati:
                    continue
                archi_disegnati.add(arco)

                p1 = self.posizioni[nodo]
                p2 = self.posizioni[vicino]

                colore = self._colore_tipo(tipo)
                pygame.draw.line(self.schermo, colore, p1, p2, 3)

        # 2.Disegna il percorso sopra il grafo
        if percorso and len(percorso) > 1:
            colore_percorso = self._colore_config(config)
            for i in range(len(percorso) - 1):
                if percorso[i] in self.posizioni and percorso[i + 1] in self.posizioni:
                    p1 = self.posizioni[percorso[i]]
                    p2 = self.posizioni[percorso[i + 1]]
                    self._disegna_freccia(self.schermo, colore_percorso, p1, p2, larghezza=7)

        # 3. Disegna i nodi, cerchio nero interno bianco, e se fa oarte del percorso cerchio colorato
        for nodo, (x, y) in self.posizioni.items():
            pygame.draw.circle(self.schermo, self.NERO, (x, y), 13)
            pygame.draw.circle(self.schermo, self.BIANCO, (x, y), 11)

            if percorso and nodo in percorso:
                pygame.draw.circle(self.schermo, self._colore_config(config), (x, y), 9)
                pygame.draw.circle(self.schermo, self.BIANCO, (x, y), 7)

            # Label nodo
            label = self.font_small.render(nodo, True, self.NERO)
            label_rect = label.get_rect(center=(x, y - 20))

            bg_rect = label_rect.inflate(3, 3)
            pygame.draw.rect(self.schermo, self.BIANCO, bg_rect)
            pygame.draw.rect(self.schermo, self.NERO, bg_rect, 1)

            self.schermo.blit(label, label_rect)


        # PANNELLO DESTRO - Legenda e metriche
        x_panel = 770
        y_panel = 100

        # Box pannello
        pygame.draw.rect(self.schermo, (245, 245, 245), (x_panel - 10, y_panel - 10, 230, 620))
        pygame.draw.rect(self.schermo, self.NERO, (x_panel - 10, y_panel - 10, 230, 620), 2)

        # LEGENDA CORRIDOI
        testo_leg = self.font.render("CORRIDOI", True, self.NERO)
        self.schermo.blit(testo_leg, (x_panel, y_panel))

        y = y_panel + 35
        pygame.draw.line(self.schermo, self.GRIGIO_SCURO, (x_panel, y), (x_panel + 200, y), 1)
        y += 15

        # Tipi corridoio
        legenda_items = [
            ("Centrale", self.ROSSO_CHIARO),
            ("Secondario", self.BLU_CHIARO),
            ("Isolato", self.VERDE_CHIARO),
        ]

        for nome, colore in legenda_items:
            pygame.draw.rect(self.schermo, colore, (x_panel, y, 35, 18))
            pygame.draw.rect(self.schermo, self.NERO, (x_panel, y, 35, 18), 1)
            self.schermo.blit(self.font_small.render(nome, True, self.GRIGIO_SCURO), (x_panel + 42, y + 1))
            y += 26

        # ALGORITMI
        y += 20
        pygame.draw.line(self.schermo, self.GRIGIO_SCURO, (x_panel, y), (x_panel + 200, y), 1)
        y += 15

        testo_conf = self.font.render("ALGORITMI", True, self.NERO)
        self.schermo.blit(testo_conf, (x_panel, y))
        y += 25

        # Lista algoritmi - 4 CONFIGURAZIONI
        config_items = [
            ("1 - Statico", self.ARANCIONE_FORTE, "h = 0"),
            ("2 - A* Euclidea", self.VIOLA_FORTE, "h ≠ 0"),
            ("3 - ML Lineare", self.ROSA_FORTE, "ML"),
            ("4 - ML RF", self.TEAL_FORTE, "ML"),
        ]

        for nome, colore, desc in config_items:
            # Linea colorata
            pygame.draw.line(self.schermo, colore, (x_panel, y + 8), (x_panel + 35, y + 8), 5)

            # Nome
            self.schermo.blit(self.font_small.render(nome, True, self.GRIGIO_SCURO), (x_panel + 42, y))

            # Descrizione
            self.schermo.blit(self.font_small.render(desc, True, self.GRIGIO_SCURO), (x_panel + 42, y + 16))

            y += 36

        # METRICHE
        if metriche:
            y += 10
            pygame.draw.line(self.schermo, self.GRIGIO_SCURO, (x_panel, y), (x_panel + 200, y), 1)
            y += 15

            metr_testo = self.font.render("METRICHE", True, self.NERO)
            self.schermo.blit(metr_testo, (x_panel, y))
            y += 25

            for chiave, valore in metriche.items():
                # Formattazione
                if isinstance(valore, float):
                    testo = f"{chiave}: {valore:.2f}"
                elif isinstance(valore, int):
                    testo = f"{chiave}: {valore}"
                else:
                    testo = f"{chiave}: {valore}"

                # Evidenzia metriche speciali
                if chiave == "Riduzione" or chiave == "Euristica":
                    color = self.VIOLA_FORTE
                else:
                    color = self.GRIGIO_SCURO

                self.schermo.blit(self.font_small.render(testo, True, color), (x_panel, y))
                y += 19



        # ISTRUZIONI (in basso a sinistra)
        istruzioni = [
            "Premi 1, 2, 3, 4 per cambiare",
            "Premi ESC per uscire"
        ]

        y_istr = 690
        for istr in istruzioni:
            self.schermo.blit(self.font_small.render(istr, True, self.GRIGIO_SCURO), (20, y_istr))
            y_istr += 22

        pygame.display.flip()


#Loop principale con switch di configurazioni
    def loop(self, percorsi: Dict[str, Tuple[List[str], str, Dict]]):

        config_corrente = "statico"

        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                #Input da tastiera
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                    elif evento.key == pygame.K_1:
                        config_corrente = "statico"
                    elif evento.key == pygame.K_2:
                        config_corrente = "ml_euclidea"
                    elif evento.key == pygame.K_3:
                        config_corrente = "ml_lineare"
                    elif evento.key == pygame.K_4:
                        config_corrente = "ml_rf"

            if config_corrente in percorsi:
                percorso, titolo, metriche = percorsi[config_corrente]
                self.disegna(percorso, titolo, config_corrente, metriche)

            self.clock.tick(30) #30 fps


#Descrive le posizioni nel grafo

# Descrive le posizioni nel grafo per il visualizzatore Pygame
def crea_posizioni_grafo_complesso() -> Dict[str, Tuple[int, int]]:

    return {

        "Ingresso": (50, 375),
        "Reparto": (720, 375),


        "A": (180, 375),
        "B": (320, 375),
        "C": (460, 375),
        "D": (600, 375),


        "N1": (180, 285),
        "N2": (320, 285),
        "N3": (460, 285),
        "N4": (600, 285),


        "S1": (180, 465),
        "S2": (320, 465),
        "S3": (460, 465),
        "S4": (600, 465),


        "E1": (180, 195),
        "E2": (320, 195),
        "E3": (460, 195),
        "E4": (600, 195),


        "T1": (180, 110),
        "T2": (320, 110),
        "T3": (460, 110),
        "T4": (600, 110),


        "P1": (180, 555),
        "P2": (320, 555),
        "P3": (460, 555),
        "P4": (600, 555),
    }


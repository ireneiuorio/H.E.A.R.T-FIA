import json
import glob
import pandas as pd
from pathlib import Path


#Genera una tabella riassuntiva dei risultati JSON
class AnalizzatoreRisultati:

    def __init__(self, results_dir: str):
        self.results_dir = results_dir
        self.esperimenti = self._carica_esperimenti()

    def _carica_esperimenti(self):
        esperimenti = {}

        pattern = f"{self.results_dir}/*.json"
        files = glob.glob(pattern)

        if not files:
            print(f" Nessun file JSON trovato in: {self.results_dir}")

        for filepath in files:
            with open(filepath, "r") as f:
                dati = json.load(f)
                nome = dati.get("esperimento", Path(filepath).stem)
                esperimenti[nome] = dati

        return esperimenti

    def tabella_riepilogativa(self) -> pd.DataFrame:
        righe = []

        for nome_exp, dati in self.esperimenti.items():
            risultati = dati.get("risultati_aggregati", {})

            for config, m in risultati.items():
                righe.append({
                    "Esperimento": nome_exp,
                    "Configurazione": config.replace("_", " ").title(),
                    "Costo medio (s)": round(m["costo_reale_medio"], 2),
                    "Gap ottimo (%)": round(m["gap_medio"] * 100, 1),
                    "Soluzioni ottime (%)": round(m["percentuale_ottimi"] * 100, 1),
                    "Nodi espansi": round(m["nodi_espansi_medio"], 1),
                    "Tempo (ms)": round(m["tempo_medio"] * 1000, 2),
                })

        return pd.DataFrame(righe)

    def stampa_riepilogo(self):
        if not self.esperimenti:
            print("Nessun esperimento caricato.")
            return

        df = self.tabella_riepilogativa()

        print("\n" + "=" *114)
        print("RIEPILOGO RISULTATI")
        print("=" * 114 + "\n")
        print(df.to_string(index=False))
        print("\n" + "=" * 114)




 #Genera una tabella LaTeX riassuntiva dei risultati sperimentali.

def genera_tabella_latex(self, output_path: str):

    df = self.tabella_riepilogativa()

    latex = df.to_latex(
        index=False,
        escape=False,
        column_format="llrrrr",
        caption="Risultati aggregati degli esperimenti",
        label="tab:risultati_esperimenti"
    )

    with open(output_path, "w") as f:
        f.write(latex)

    print(f"Tabella LaTeX generata in: {output_path}")


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    RESULTS_DIR = BASE_DIR / "results"

    analizzatore = AnalizzatoreRisultati(results_dir=str(RESULTS_DIR))
    analizzatore.stampa_riepilogo()



#Modelli di ML per stimare il tempo di percorrenza di un corridoio
import numpy as np
from sklearn.linear_model import LinearRegression #implementazioni pronte di Ml
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score #valutare quando sbaglia il modello


#Impongo il contratto ai modelli concreti
class ModelloCosto:


#x->feature (lunghezza,orario,affollamento)
#y->target

    #Ogni modello deve implementare addestra
    def addestra(self, X: np.ndarray, y: np.ndarray):
        raise NotImplementedError

    #Ogni modello stima il tempo di percorrenza
    def stima(self, lunghezza: float, orario: int, affollamento: float) -> float:
        raise NotImplementedError

    #Capire quanto bene il modello predice sui dati che non ha visto durante l'addestramento
    def valuta(self, X: np.ndarray, y: np.ndarray) -> dict:
        y_pred = self.predici_batch(X)

        mae = mean_absolute_error(y, y_pred) #Errore medio in secondi
        rmse = np.sqrt(mean_squared_error(y, y_pred)) #Penalizza errori grandi
        r2 = r2_score(y, y_pred) #Qianto il modello spiega i dati

        # Errore percentuale medio
        errori_relativi = np.abs(y - y_pred) / y
        mape = np.mean(errori_relativi) * 100

        return {
            "mae": mae,
            "rmse": rmse,
            "r2": r2,
            "mape": mape,
        }


#x->lunghezza orario e affollamento
    def predici_batch(self, X: np.ndarray) -> np.ndarray:
        return np.array([
            self.stima(x[0], x[1], x[2]) for x in X
        ])
        #per ogni riga del dataset prende lunghezzza orario e affollamento e chiama stimache restituisce il tempo stimato

#Modello regressione lineare, eredita da modello costo
class ModelloRegressioneLineare(ModelloCosto):


    def __init__(self):
        self.modello = LinearRegression() #modello
        self.addestrato = False #Finchè non chiamo addestra non può stimare


    #Addestra il modello
    #Input x->(lunghezza,orario,affollamento), y->(tempo reale simulato)
    def addestra(self, X: np.ndarray, y: np.ndarray):

        self.modello.fit(X, y) #impara i coefficienti
        self.addestrato = True

        # Stampa coefficienti
        print("\nCoefficienti Regressione Lineare:")
        print(f"  Lunghezza: {self.modello.coef_[0]:.4f}")
        print(f"  Orario: {self.modello.coef_[1]:.4f}")
        print(f"  Affollamento: {self.modello.coef_[2]:.4f}")
        print(f"  Intercetta: {self.modello.intercept_:.4f}")

  # Prende un solo corridoio e definisce un tempo stimato, usa il modello
    def stima(self, lunghezza: float, orario: int, affollamento: float) -> float:
        if not self.addestrato:
            raise RuntimeError("Modello non addestrato")

        X = np.array([[lunghezza, orario, affollamento]])
        return max(0.0, self.modello.predict(X)[0]) #restituisvce un array tempo

    def __str__(self):
        return "Regressione Lineare"


#Modello Random Forest
class ModelloRandomForest(ModelloCosto):

    def __init__(
            self,
            numero_alberi: int = 100, # più alberi più accuratezza ma più costo
            profondita_massima: int = None,
            seed: int = 42
    ):
        self.modello = RandomForestRegressor(
            n_estimators=numero_alberi,
            max_depth=profondita_massima,
            random_state=seed,
            n_jobs=-1  # Usa tutti i core della CPU
        )
        self.addestrato = False


    #Addestra il modello
    # Input x->(lunghezza,orario,affollamento), y->(tempo reale simualto)
    def addestra(self, X: np.ndarray, y: np.ndarray):

        self.modello.fit(X, y)
        self.addestrato = True

        # Feature importance: dice su cosa si basa davvero il modello per decidere
        print("\nFeature Importance (Random Forest):")
        importances = self.modello.feature_importances_
        features = ["Lunghezza", "Orario", "Affollamento"]
        for feat, imp in zip(features, importances):
            print(f"  {feat:<13}: {imp * 100:5.1f}%")

    #Questa è la funzione che A* chiama
    def stima(self, lunghezza: float, orario: int, affollamento: float) -> float:
        if not self.addestrato:
            raise RuntimeError("Modello non addestrato")

        X = np.array([[lunghezza, orario, affollamento]])
        return max(0.0, self.modello.predict(X)[0]) #stima del costo, predict restituisce un array

    def __str__(self):
        return "Random Forest"



#inpuy lista modelli usati, dati su cui il modello impara, dati di test
def confronta_modelli(modelli: list,X_train: np.ndarray,y_train: np.ndarray, X_test: np.ndarray,y_test: np.ndarray
):
#Dizionario->nome modello, metriche

    print("=" * 70)
    print("CONFRONTO MODELLI ML")
    print("=" * 70)

    risultati = {}

    for modello in modelli:
        nome = str(modello)
        print(f"\n{nome}:")
        print("-" * 70)

        # Addestra
        print("Addestramento...")
        modello.addestra(X_train, y_train)

        # Valuta su train
        metriche_train = modello.valuta(X_train, y_train)
        print(f"\nPrestazioni su TRAIN set:")
        print(f"  MAE:  {metriche_train['mae']:.3f}s")
        print(f"  RMSE: {metriche_train['rmse']:.3f}s")
        print(f"  R²:   {metriche_train['r2']:.3f}")
        print(f"  MAPE: {metriche_train['mape']:.1f}%")

        # Valuta su test
        metriche_test = modello.valuta(X_test, y_test)
        print(f"\nPrestazioni su TEST set:")
        print(f"  MAE:  {metriche_test['mae']:.3f}s")
        print(f"  RMSE: {metriche_test['rmse']:.3f}s")
        print(f"  R²:   {metriche_test['r2']:.3f}")
        print(f"  MAPE: {metriche_test['mape']:.1f}%")

        risultati[nome] = {
            "train": metriche_train,
            "test": metriche_test,
            "modello": modello
        }

    print("\n" + "=" * 70)
    print("RIEPILOGO COMPARATIVO (Test Set)")
    print("=" * 70)
    print(f"{'Modello':<30} {'MAE':<10} {'RMSE':<10} {'R²':<10} {'MAPE':<10}")
    print("-" * 70)

    for nome, res in risultati.items():
        m = res['test']
        print(f"{nome:<30} {m['mae']:<10.3f} {m['rmse']:<10.3f} {m['r2']:<10.3f} {m['mape']:<10.1f}%")

    return risultati



#Funge da ponte tra A* e il modello
#Riceve un modello Ml già addestrato
def crea_funzione_costo_ml_dinamica(modello: ModelloCosto):


#Factory per funzione costo che accetta parametri dinamici.
    def factory(orario: int, affollamento: float):
        #quello che a* si aspetta
        def funzione_costo(n1: str, n2: str, lunghezza: float, tipo: str) -> float:
            # Aggiusta affollamento per tipo
            if tipo == "centrale":
                aff_eff = min(1.0, affollamento + 0.3)
            elif tipo == "isolato":
                aff_eff = max(0.0, affollamento - 0.3)
            else:
                aff_eff = affollamento
            #usa il modello addestrato
            return modello.stima(lunghezza, orario, aff_eff)

        return funzione_costo

    return factory


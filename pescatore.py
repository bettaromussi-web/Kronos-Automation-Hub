import yfinance as yf
import pandas as pd
import os
import argparse

# Aggiunge la cartella corrente al percorso di ricerca di Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from model import Kronos, KronosTokenizer, KronosPredictor
except ImportError:
    print("❌ Errore: Cartella 'model' non trovata nella directory corrente!")
    print(f"Directory attuale: {os.getcwd()}")
    print(f"Contenuto: {os.listdir('.')}")
    sys.exit(1)
    
parser = argparse.ArgumentParser()
parser.add_argument('--sector', type=str, help='Il settore da analizzare')
args = parser.parse_args()

settore = args.sector # Ora il settore viene preso dal comando --sector
file_lista = f"{settore}.csv"
cartella_destinazione = f"database_{settore}"

if not os.path.exists(file_lista):
    print(f"❌ Errore: Il file {file_lista} non esiste!")
else:
    if not os.path.exists(cartella_destinazione):
        os.makedirs(cartella_destinazione)

    df_lista = pd.read_csv(file_lista)
    titoli = df_lista['Ticker'].tolist()

    print(f"📥 Scaricamento settore {settore.upper()} ({len(titoli)} titoli)...")

    for ticker in titoli:
        try:
            data = yf.download(ticker, period="1mo", interval="5m", progress=False)
            data.columns = data.columns.get_level_values(0)
            data = data.reset_index()
            
            percorso_file = os.path.join(cartella_destinazione, f"{ticker}.csv")
            data.to_csv(percorso_file, index=False)
            print(f"✅ {ticker} salvato.")
        except Exception as e:
            print(f"❌ Errore su {ticker}: {e}")

    print(f"\n🏁 Database '{cartella_destinazione}' aggiornato!")

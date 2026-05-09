import sys
import os
import pandas as pd
import numpy as np
import torch
import plotly.graph_objects as go
from docx import Document
from docx.shared import Inches
from datetime import datetime

# --- CONFIGURAZIONE ---
settore = input("Quale settore vuoi analizzare? (es: tech o energy): ").strip().lower()
CARTELLA_DATI = f"database_{settore}"
REPORT_DIR = "reports"
LOOKBACK = 512
PRED_LEN = 120
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

if not os.path.exists(CARTELLA_DATI):
    print(f"❌ Errore: La cartella {CARTELLA_DATI} non esiste!")
    sys.exit()

if not os.path.exists(REPORT_DIR): os.makedirs(REPORT_DIR)

# Caricamento Kronos
sys.path.append(os.getcwd())
from model import Kronos, KronosTokenizer, KronosPredictor
print(f"🧠 Caricamento modello su {DEVICE.upper()}...")
tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
model = Kronos.from_pretrained("NeoQuasar/Kronos-small").to(DEVICE)
predictor = KronosPredictor(model, tokenizer, device=DEVICE, max_context=LOOKBACK)

# Creazione Documento Word
doc = Document()
doc.add_heading(f'Report Kronos: Settore {settore.upper()}', 0)
doc.add_paragraph(f"Data Analisi: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# Identifica automaticamente i titoli nella cartella
titoli = [f.replace('.csv', '') for f in os.listdir(CARTELLA_DATI) if f.endswith('.csv')]

for ticker in titoli:
    print(f"🔍 Analisi {ticker}...")
    df = pd.read_csv(os.path.join(CARTELLA_DATI, f"{ticker}.csv"))
    
    # Preparazione e Predizione
    x_df = df.iloc[-LOOKBACK:].copy()
    x_df.columns = [c.lower() for c in x_df.columns]
    x_ts = pd.to_datetime(df['Datetime'].iloc[-LOOKBACK:])
    y_ts = pd.Series(pd.date_range(start=x_ts.iloc[-1], periods=PRED_LEN + 1, freq='5min')[1:])

    try:
        pred = predictor.predict(x_df[['open','high','low','close','volume']], x_ts, y_ts, PRED_LEN, T=0.8, sample_count=10)
        
        # Logica Sentimento
        var_perc = ((pred['close'].iloc[-1] - x_df['close'].iloc[-1]) / x_df['close'].iloc[-1]) * 100
        sentimento = "RIALZISTA" if var_perc > 0.5 else "RIBASSISTA" if var_perc < -0.5 else "STABILE"

        # Grafico
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=x_df['close'].tail(50), name='Storico'))
        fig.add_trace(go.Scatter(x=list(range(50, 50+PRED_LEN)), y=pred['close'], name='Predizione', line=dict(dash='dash', color='red')))
        
        img_path = f"temp_{ticker}.png"
        fig.write_image(img_path)

        # Scrittura Word
        doc.add_heading(f'Titolo: {ticker}', level=1)
        doc.add_picture(img_path, width=Inches(5))
        doc.add_paragraph(f"Sentimento: {sentimento} | Variazione prevista: {var_perc:.2f}%")
        os.remove(img_path)
    except Exception as e:
        print(f"⚠️ Errore su {ticker}: {e}")

# Salva Report
nome_file = os.path.join(REPORT_DIR, f"Report_{settore.upper()}_{datetime.now().strftime('%Y%m%d_%H%M')}.docx")
doc.save(nome_file)
print(f"\n✅ Analisi completata! Report salvato in: {nome_file}")

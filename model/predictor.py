import torch
import pandas as pd
import numpy as np

class KronosPredictor:
    def __init__(self, model, tokenizer, device="cpu", max_context=512):
        """
        Inizializza il predittore Kronos.
        """
        self.model = model.to(device)
        self.tokenizer = tokenizer
        self.device = device
        self.max_context = max_context

    def predict(self, df, x_timestamp, y_timestamp, pred_len, T=1.0, top_p=0.9, sample_count=1):
        """
        Esegue la predizione probabilistica utilizzando il metodo forecast del modello.
        """
        self.model.eval()
        
        # Assicuriamoci che i dati siano nel formato corretto per il modello
        # Kronos si aspetta le colonne in minuscolo: open, high, low, close, volume
        df.columns = [c.lower() for c in df.columns]
        
        with torch.no_grad():
            # Il modello Kronos (in kronos.py) ha un metodo chiamato 'forecast'
            # che gestisce internamente la tokenizzazione e la generazione
            forecast_df = self.model.forecast(
                df=df,
                x_timestamp=x_timestamp,
                y_timestamp=y_timestamp,
                pred_len=pred_len,
                T=T,
                top_p=top_p,
                sample_count=sample_count
            )
            
        return forecast_df

# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 11:41:34 2026

@author: Diego
"""

import os
import pandas as pd

class CreditDataCollector:
    
    def __init__(self) -> None: 
        
        self.cred_path = r"A:\2026BlpAdHocData\Combined\FixedIncomeIndex"
        self.src_path  = os.getcwd()
        self.repo_path = os.path.abspath(os.path.join(self.src_path, ".."))
        self.data_path = os.path.join(self.repo_path, "data")
        
    def get_index_data(self, verbose: bool = True) -> None: 
        
        if verbose: print("Getting Credit Index Data")
        
        out_path = os.path.join(self.data_path, "CreditData.parquet")
        if os.path.exists(out_path):
            if verbose: print("Already have credit data\n")
            return None
        
        ticker_path = os.path.join(self.data_path, "CreditTickers.xlsx")
        df_tickers  = pd.read_excel(io = ticker_path)
        
        tickers = df_tickers.ticker.drop_duplicates().sort_values().to_list()
        
        files = {
            "INDEX_BLENDED_SPREAD_DUR": "sprd_dur", 
            "INDEX_OAS_TSY_BP"        : "oas", 
            "TRUU"                    : "truu"}
        
        df_lists = []
        
        for file in files.keys(): 
            
            path   = os.path.join(self.cred_path, file + ".parquet")
            df_add = (pd
                      .read_parquet(path = path, engine = "pyarrow")
                      .loc[lambda x: x.security.isin(tickers)]
                      .rename(columns = {file: "value"})
                      .rename(columns = {"PX_LAST": "value"})
                      .assign(calc = files[file]))
            
            df_lists.append(df_add)
            
        df_out = (pd
                .concat(df_lists)
                .pivot(index = ["date", "security"], columns = "calc", values = "value")
                .dropna()
                .reset_index())
        
        if verbose: print("Saving data\n")
        df_out.to_parquet(path = out_path, engine = "pyarrow")
        
CreditDataCollector().get_index_data()
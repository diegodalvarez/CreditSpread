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
        
    def get_raw_index_data(self, verbose: bool = True) -> None: 
        
        if verbose: print("Getting Credit Index Data")
        
        out_path = os.path.join(self.data_path, "RawCreditData.parquet")
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

    def _get_days(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.sort_values("date").assign(days_diff = lambda x: x.date.diff())
        
    def slice_index_data(self, verbose: bool = True) -> pd.DataFrame: 
        
        if verbose: print("Slicing Credit Indices")
        
        out_path = os.path.join(self.data_path, "SlicedCreditData.parquet")
        if os.path.exists(out_path):
            if verbose: print("Already have data\n")
            return None
        
        raw_path = os.path.join(self.data_path, "RawCreditData.parquet")
        df_raw   = pd.read_parquet(path = raw_path, engine = "pyarrow")
        
        df_slicer = (df_raw
            [["date", "security"]]
            .groupby("security")
            .apply(self._get_days)
            .reset_index()
            .drop(columns = ["level_1"])
            .assign(days_diff = lambda x: x.days_diff.dt.days)
            .loc[lambda x: x.days_diff < 5]
            [["security", "date"]]
            .groupby("security")
            .agg("min")
            .rename(columns = {"date": "slice_date"}))
        
        df_out = (df_raw
                .merge(right = df_slicer, how = "inner", on = ["security"])
                .loc[lambda x: x.date >= x.slice_date]
                .drop(columns = ["slice_date"]))
        
        if verbose: print("Saving data\n")
        df_out.to_parquet(path = out_path, engine = "pyarrow")
        
def main() -> None: 
        
    credit_collect = CreditDataCollector()
    credit_collect.get_raw_index_data()
    credit_collect.slice_index_data()
    
if __name__ == "__main__": main()
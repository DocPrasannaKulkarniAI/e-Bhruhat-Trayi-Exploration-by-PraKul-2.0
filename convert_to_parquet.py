"""
One-time script to convert Excel to Parquet format
Run this once before deploying the app

Usage:
    python convert_to_parquet.py

This will create 'all3_cleaned.parquet' from 'all3_cleaned.xlsx'
"""

import pandas as pd
import os

def convert_excel_to_parquet():
    input_file = "all3_cleaned.xlsx"
    output_file = "all3_cleaned.parquet"
    
    print(f"🔄 Loading {input_file}...")
    
    # Load Excel
    df = pd.read_excel(input_file, engine='openpyxl')
    
    print(f"✅ Loaded {len(df):,} rows")
    print(f"📊 Columns: {list(df.columns)}")
    
    # Save as Parquet
    df.to_parquet(output_file, engine='pyarrow', index=False)
    
    # Compare file sizes
    xlsx_size = os.path.getsize(input_file) / (1024 * 1024)  # MB
    parquet_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
    
    print(f"\n📁 File Size Comparison:")
    print(f"   Excel:   {xlsx_size:.2f} MB")
    print(f"   Parquet: {parquet_size:.2f} MB")
    print(f"   Reduction: {((xlsx_size - parquet_size) / xlsx_size * 100):.1f}%")
    
    print(f"\n✅ Successfully created {output_file}")
    print(f"📌 Use this file with the optimized app for 10x faster loading!")

if __name__ == "__main__":
    convert_excel_to_parquet()

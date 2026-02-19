
import pandas as pd
import numpy as np

def check_content(filename):
    print(f"\nChecking content for {filename}...")
    try:
        df = pd.read_csv(filename, encoding='latin1', header=None, on_bad_lines='skip')
        
        # Assume header is around row 10 (0-indexed)
        # Data starts row 11
        
        data_block = df.iloc[11:, 5:]
        
        print("Data Block Shape:", data_block.shape)
        
        # Count non-nulls
        non_null_count = data_block.count().sum()
        print(f"Non-null values in measurement area (Row 11+, Col 5+): {non_null_count}")
        
        if non_null_count > 0:
            print("Sample non-null values:")
            print(data_block.stack().sample(min(5, non_null_count)))
        else:
            print("The measurement area appears to be empty.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    files = ["KMX-PA-PE-F-001.csv", "KMX-PA-PT-F-001.csv"]
    for f in files:
        check_content(f)

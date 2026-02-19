
import pandas as pd
import sys

# Set pandas options to display all columns/rows we ask for
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)

def analyze_file(filename):
    print(f"\n{'='*50}\nAnalyzing {filename}\n{'='*50}")
    
    try:
        # Read with header=None to see raw structure effectively
        df = pd.read_csv(filename, encoding='latin1', header=None, on_bad_lines='skip')
        
        print("--- First 20 rows, first 20 columns ---")
        print(df.iloc[:20, :20])
        
        # identifying the start of the data table
        # looking for likely header row
        print("\n--- Identifying potential header rows ---")
        for i in range(20):
            row_values = df.iloc[i, :20].dropna().tolist()
            if row_values:
                print(f"Row {i}: {row_values}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    files = ["KMX-PA-PE-F-001.csv", "KMX-PA-PT-F-001.csv"]
    for f in files:
        analyze_file(f)

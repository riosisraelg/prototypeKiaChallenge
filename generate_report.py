
import pandas as pd
import numpy as np
import io

def clean_and_parse(filename):
    print(f"Processing {filename}...")
    try:
        # Load the file, skipping initial metadata rows to get to the header area
        # Based on previous inspection, the main headers seem to be around row 8 (0-indexed)
        # and sub-headers (times) at row 10.
        
        # specific to the structure observed:
        # Row 8: Num, ETAPA, VARIABLE, RANGO, VOLUMEN DE TANQUE...
        # Row 10: ... Times ...
        
        # Let's read the whole thing without header first to slice it carefully
        df_raw = pd.read_csv(filename, encoding='latin1', header=None, on_bad_lines='skip')
        
        # Extract Metadata
        doc_num = df_raw.iloc[0, 12] if len(df_raw.columns) > 12 else "Unknown"
        date_rev = df_raw.iloc[2, 12] if len(df_raw.columns) > 12 else "Unknown"
        dept = df_raw.iloc[4, 12] if len(df_raw.columns) > 12 else "Unknown"
        
        metadata = {
            "Document Number": doc_num,
            "Revision Date": date_rev,
            "Department": dept
        }

        # Find the start of the data
        # Look for "Num" or "VARIABLE" in a column
        header_row_idx = None
        for i in range(20):
            row_vals = df_raw.iloc[i].astype(str).tolist()
            if "VARIABLE" in row_vals or "Variable" in row_vals:
                header_row_idx = i
                break
        
        if header_row_idx is None:
            return metadata, None, "Could not find data header."

        # The time headers are likely 2 rows below the main header
        time_row_idx = header_row_idx + 2
        
        # Get Variable info
        # Assuming structure: Col 1=Etapa, Col 2=Variable, Col 3=Rango (indices might vary)
        # Based on previous `head` output: 
        # Row 8 (likely header_row_idx): Col 0=Num, 1=ETAPA, 2=VARIABLE, 3=RANGO, 4=VOL/TANK
        
        # Slice the dataframe from the first data row (time_row_idx + 1)
        data_start_idx = time_row_idx + 1
        df_data = df_raw.iloc[data_start_idx:].copy()
        
        # Reconstruct columns
        # We want: ETAPA, VARIABLE, RANGO, and the Time Columns
        
        # Time columns seem to start from column 5 onwards (based on previous view)
        # Let's verify column 5 in time_row_idx
        time_headers = df_raw.iloc[time_row_idx, 5:].dropna().tolist()
        
        # Let's build a simplified dataframe
        structured_data = []
        
        for idx, row in df_data.iterrows():
            # Stop if row is largely empty
            if pd.isna(row[2]) and pd.isna(row[3]):
                continue
                
            etapa = str(row[1]).replace('\n', ' ').strip() if not pd.isna(row[1]) else ""
            variable = str(row[2]).replace('\n', ' ').strip()
            rango = str(row[3]).strip() if not pd.isna(row[3]) else ""
            
            # Extract measurements
            # Assuming columns 5 to 5+len(time_headers) are the times
            measurements = row[5:5+len(time_headers)].tolist()
            
            entry = {
                "Etapa": etapa,
                "Variable": variable,
                "Rango": rango,
                "Measurements": measurements
            }
            structured_data.append(entry)
            
        return metadata, structured_data, time_headers

    except Exception as e:
        return {}, None, f"Error parsing: {str(e)}"

def generate_markdown_report(files):
    report = "# Análisis de Reportes de Laboratorio KIA\n\n"
    
    for f in files:
        report += f"## Archivo: {f}\n\n"
        meta, data, times = clean_and_parse(f)
        
        if isinstance(times, str): # Error message
            report += f"**Error parsing file:** {times}\n\n"
            continue
            
        report += "### Metadatos Identificados\n"
        for k, v in meta.items():
            report += f"- **{k}**: {v}\n"
        
        report += "\n### Estructura de Datos\n"
        report += f"Se identificaron {len(data)} variables monitoreadas."
        if isinstance(times, list):
            report += f" Los horarios de medición detectados son: {', '.join([str(t) for t in times if str(t).lower() != 'nan'])}\n"
        
        report += "\n### Análisis de Variables\n"
        report += "| Etapa | Variable | Rango Esperado | Promedio de Lecturas | Mín | Máx |\n"
        report += "|---|---|---|---|---|---|\n"
        
        for item in data:
            measurements = item['Measurements']
            # Clean measurements (remove NaNs, convert to float)
            clean_meas = []
            for m in measurements:
                try:
                    val = float(m)
                    clean_meas.append(val)
                except:
                    continue
            
            if clean_meas:
                avg = f"{sum(clean_meas)/len(clean_meas):.2f}"
                min_val = f"{min(clean_meas):.2f}"
                max_val = f"{max(clean_meas):.2f}"
            else:
                avg = "-"
                min_val = "-"
                max_val = "-"
            
            report += f"| {item['Etapa']} | {item['Variable']} | {item['Rango']} | {avg} | {min_val} | {max_val} |\n"
        
        report += "\n---\n\n"

    with open("analysis_report.md", "w") as f:
        f.write(report)
    
    print("Report generated: analysis_report.md")

if __name__ == "__main__":
    files = ["KMX-PA-PE-F-001.csv", "KMX-PA-PT-F-001.csv"]
    generate_markdown_report(files)

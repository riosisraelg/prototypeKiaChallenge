
import pandas as pd
import numpy as np

def find_value_in_row(row, key_substring):
    """Search for a substring in a row and return the next non-nan cell value."""
    row = row.astype(str).tolist()
    for i, val in enumerate(row):
        if key_substring.lower() in val.lower():
            # Found key, look for value in next few cells
            for j in range(i, len(row)):
                clean_val = row[j].replace(key_substring, '').strip()
                # If the cell contained both key and value (e.g. "Doc: 123")
                if len(clean_val) > 1 and clean_val != ":" and clean_val != "nan":
                    return clean_val
                # If value is in next cells
                if j+1 < len(row):
                    next_val = row[j+1]
                    if next_val.lower() != 'nan' and next_val.strip() != '':
                        return next_val
    return "Not Found"

def parse_file_structure(filename):
    try:
        df = pd.read_csv(filename, encoding='latin1', header=None, on_bad_lines='skip')
        
        # Metadata Extraction
        doc_ref = "Unknown"
        revision = "Unknown"
        dept = "Unknown"
        
        # Scan first 10 rows for metadata
        for i in range(10):
            row = df.iloc[i]
            if doc_ref == "Unknown":
                doc_ref = find_value_in_row(row, "Documento")
            if revision == "Unknown":
                revision = find_value_in_row(row, "Revision")
            if dept == "Unknown":
                dept = find_value_in_row(row, "Departamento")

        # Identify Process (PT vs ED based on filename or content)
        process_name = "Electrodeposition (ED)" if "PE" in filename else "Pre-Treatment (PT)"
        if "PT" in filename: process_name = "Pre-Treatment (PT)"
        
        # Extract Variables
        variables = []
        
        # Locate header row
        start_row = 0
        for i in range(20):
            if "VARIABLE" in df.iloc[i].astype(str).str.upper().values:
                start_row = i
                break
                
        # Iterate through data rows
        current_stage = ""
        for i in range(start_row + 1, len(df)):
            row = df.iloc[i]
            
            # Col 1 is usually Stage/Etapa
            stage_val = str(row[1]).replace("nan", "").strip()
            if stage_val:
                current_stage = stage_val
                
            # Col 2 is Variable
            var_name = str(row[2]).replace("nan", "").strip()
            
            # Col 3 is Range
            range_val = str(row[3]).replace("nan", "").strip()
            
            # Skip empty or header-repetition rows
            if not var_name or "VARIABLE" in var_name.upper():
                continue
                
            # Clean text
            current_stage = current_stage.replace('\n', ' ')
            var_name = var_name.replace('\n', ' ').replace('¡', '°').replace('_', 'µ')
            range_val = range_val.replace('¡', '°')
            
            variables.append({
                "Stage": current_stage,
                "Variable": var_name,
                "Range": range_val
            })
            
        return {
            "Filename": filename,
            "Process": process_name,
            "Document": doc_ref,
            "Revision": revision,
            "Department": dept,
            "Variables": variables
        }

    except Exception as e:
        return {"Error": str(e)}

def write_markdown_report_v2(parsed_data_list):
    md = "# Análisis de Reportes de Control de Calidad - KIA Motors Mexico\n\n"
    md += "Este reporte analiza la estructura y parámetros de control definidos en los archivos CSV proporcionados. "
    md += "Los archivos parecen ser plantillas de hoja de control diario ('Daily Laboratory Report') para las áreas de Pintura.\n\n"
    
    for data in parsed_data_list:
        md += f"## {data['Process']} - Análisis de Estructura\n\n"
        
        md += "| Metadato | Valor |\n"
        md += "|---|---|\n"
        md += f"| Archivo Origen | `{data['Filename']}` |\n"
        md += f"| Documento | {data.get('Document', 'N/A')} |\n"
        md += f"| Revisión | {data.get('Revision', 'N/A')} |\n"
        md += f"| Departamento | {data.get('Department', 'N/A')} |\n\n"
        
        md += "### Parámetros de Control Monitoreados\n\n"
        md += "A continuación se listan las variables críticas y sus rangos operativos estándar:\n\n"
        
        md += "| Etapa del Proceso | Variable de Control | Rango Estándar |\n"
        md += "|---|---|---|\n"
        
        last_stage = ""
        for v in data['Variables']:
            stage = v['Stage']
            # Make table cleaner by not repeating stage name
            display_stage = stage if stage != last_stage else ""
            last_stage = stage
            
            md += f"| {display_stage} | {v['Variable']} | {v['Range']} |\n"
            
        md += "\n---\n\n"
        
    md += "### Observaciones Generales\n"
    md += "1. **Naturaleza de los Archivos**: Los archivos analizados actúan como definidores de estándares operativos. No contienen datos de medición históricos (los campos de registro están vacíos o contienen marcadores de posición), por lo que se asume que son **plantillas maestras**.\n"
    md += "2. **Frecuencia de Muestreo**: La estructura de columnas (08:00 - 06:00) indica un monitoreo continuo de 24 horas con intervalos de muestreo de 2 horas.\n"
    md += "3. **Cobertura de Control**: \n"
    md += "   - **Electrodeposición (ED)**: Se enfoca en voltaje, amperaje, sólidos y condiciones del baño principal.\n"
    md += "   - **Pre-Tratamiento (PT)**: Se enfoca en la limpieza y preparación de la superficie mediante múltiples etapas de enjuague y control de pH/Conductividad.\n"

    with open("analysis_report.md", "w") as f:
        f.write(md)
    print("Final report written to analysis_report.md")

if __name__ == "__main__":
    files = ["KMX-PA-PE-F-001.csv", "KMX-PA-PT-F-001.csv"]
    results = [parse_file_structure(f) for f in files]
    write_markdown_report_v2(results)

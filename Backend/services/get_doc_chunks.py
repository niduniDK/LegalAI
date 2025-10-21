import pandas as pd
import os

# Support both local and Railway/production paths
if os.path.exists("/app/data"):
    DATA_DIR = "/app/data"
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "..", "data")

INDICES_DIR = os.path.join(DATA_DIR, "indices")

def get_doc_chunks(filename, type):
    base_path = os.path.join(INDICES_DIR, "constitution.tsv")
    if type == "acts":
        base_path = os.path.join(INDICES_DIR, "acts.tsv")
    elif type == "bills":
        base_path = os.path.join(INDICES_DIR, "bills.tsv")
    elif type == "gazettes":
        base_path = os.path.join(INDICES_DIR, "gazettes.tsv")
    
    try:
        # Check if file exists
        if not os.path.exists(base_path):
            print(f"File not found: {base_path}")
            return []
        
        # Try to read with different encodings
        df = None
        for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
            try:
                df = pd.read_csv(base_path, sep="\t", encoding=encoding)
                print(f"Successfully read {base_path} with encoding: {encoding}")
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"Error with encoding {encoding}: {e}")
                continue
        
        # If all encodings fail, try with errors='ignore'
        if df is None:
            try:
                df = pd.read_csv(base_path, sep="\t", encoding='utf-8', errors='ignore')
                print(f"Read {base_path} with UTF-8 and ignored errors")
            except Exception as e:
                print(f"Failed to read file even with error handling: {e}")
                return []

        # Filter rows where 'name' matches the given filename
        if 'name' not in df.columns:
            print(f"Column 'name' not found in {base_path}. Available columns: {df.columns.tolist()}")
            return []
            
        filtered_df = df[df['name'] == filename]
        if filtered_df.empty:
            print(f"No document found with filename: {filename} in {base_path}")
            return []
        
        if 'content' not in df.columns:
            print(f"Column 'content' not found in {base_path}. Available columns: {df.columns.tolist()}")
            return []
        
        content = filtered_df['content'].to_list()
        
        # Clean content and remove any problematic characters
        clean_content = []
        for item in content:
            if pd.notna(item) and isinstance(item, str):
                # Remove any non-printable characters except common whitespace
                clean_item = ''.join(char for char in str(item) if char.isprintable() or char in ['\n', '\t', ' '])
                if clean_item.strip():  # Only add non-empty content
                    clean_content.append(clean_item.strip())
            elif pd.notna(item):
                clean_str = str(item).strip()
                if clean_str:
                    clean_content.append(clean_str)
        
        print(f"Found {len(clean_content)} content chunks for {filename}")
        return clean_content
        
    except Exception as e:
        print(f"Error reading document chunks for {filename}: {e}")
        return []
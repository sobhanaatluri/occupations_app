import pandas as pd

def load_embeddings(embed_path):
    """
    Load embeddings from CSV, fix header issues with decimal points,
    and add the headers as the first row of data.
    
    Parameters:
    -----------
    embed_path : str
        Path to the CSV file containing embeddings
    
    Returns:
    --------
    numpy.ndarray
        NumPy array with the fixed header included as first row
    """
    
    print("load_embeddings()")
    
    # Load the embeddings
    embeddings = pd.read_csv(embed_path)
    
    # Clean and convert the column headers
    header_values = []
    for col in embeddings.columns:
        # Handle potential formatting issues with extra decimal points
        col_str = str(col)  # Ensure it's a string
        if col_str.count('.') > 1:
            # If there are multiple decimal points, keep only the first one
            parts = col_str.split('.')
            cleaned_value = parts[0] + '.' + parts[1]  # Take only first decimal part
            header_values.append(float(cleaned_value))
        else:
            # Normal case - just one or zero decimal points
            header_values.append(float(col_str))
    
    # Create a new DataFrame with the header values as the first row
    header_df = pd.DataFrame([header_values], columns=embeddings.columns)
    
    # Concatenate the header row with the original data
    embeddings = pd.concat([header_df, embeddings], ignore_index=True)
    
    # Convert to numpy array
    embeddings = embeddings.to_numpy()
    
    return embeddings
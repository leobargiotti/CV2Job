import pandas as pd
import os


def process_excel(path_file):
    try:
        df = pd.read_excel(path_file)
    except Exception as e:
        print(f"Error loading the file: {e}")
        return

    if 'Job Title' not in df.columns or 'Job Description' not in df.columns or 'Required Skills' not in df.columns:
        print("The Excel file must contain the columns 'Job Title', 'Job Description', and 'Required Skills'.")
        return

    df_no_duplicates = df.drop_duplicates(subset=['Job Title', 'Job Description', 'Required Skills'], keep='first')

    cleaned_file_path = 'JobOpportunities_Cleaned.xlsx'
    df_no_duplicates.to_excel(cleaned_file_path, index=False)
    print(f"Data without duplicates saved to: {cleaned_file_path}")


os.chdir(os.path.dirname(os.path.abspath(__file__)))
process_excel('JobOpportunities.xlsx')

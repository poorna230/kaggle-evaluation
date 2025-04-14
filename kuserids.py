import os
import pandas as pd
import streamlit as st
from kaggle.api.kaggle_api_extended import KaggleApi

# Function to authenticate Kaggle API using the API key
def authenticate_kaggle():
    if not os.path.exists('kaggle.json'):
        st.error("Please upload your Kaggle API key (kaggle.json).")
    else:
        os.environ['KAGGLE_CONFIG_DIR'] = os.getcwd()

# Function to fetch submitted notebooks by a Kaggle user
def get_notebooks_submitted(kaggle_id):
    api = KaggleApi()
    api.authenticate()

    submissions = api.kernels_list(user=kaggle_id)
    notebook_details = []

    for submission in submissions:
        notebook_details.append({
            'Notebook Title': submission.title,
            'Notebook URL': f"https://www.kaggle.com/{submission.ref}",
            'Date Submitted': submission.last_run_time
        })

    return notebook_details

# Function to save the results to a spreadsheet
def save_to_spreadsheet(notebook_details, kaggle_id):
    df = pd.DataFrame(notebook_details)
    file_name = f'{kaggle_id}_notebooks.xlsx'
    df.to_excel(file_name, index=False, engine='openpyxl')
    return file_name

# Streamlit UI
def main():
    st.title("📊 Kaggle Notebooks Submission Tracker")
    st.write("upload your kaggle.json file in following path==>c:/users/.kaggle/kaggle.json")
    st.sidebar.header("🔑 Upload Kaggle API Key")
    uploaded_file = st.sidebar.file_uploader("Upload your `kaggle.json`", type="json")

    if uploaded_file:
        with open('kaggle.json', 'wb') as f:
            f.write(uploaded_file.getbuffer())
        authenticate_kaggle()

    kaggle_id = st.text_input("Enter Kaggle Username:")

    if st.button("Fetch Notebooks"):
        if kaggle_id:
            st.info("Fetching data...")
            try:
                notebooks = get_notebooks_submitted(kaggle_id)
                if notebooks:
                    df = pd.DataFrame(notebooks)
                    st.success(f"Found {len(notebooks)} notebooks submitted by **{kaggle_id}**.")
                    st.dataframe(df)

                    file_name = save_to_spreadsheet(notebooks, kaggle_id)
                    with open(file_name, "rb") as f:
                        st.download_button(
                            label="📥 Download Excel",
                            data=f,
                            file_name=file_name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.warning("No notebooks found for the specified user.")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter a valid Kaggle username.")

if __name__ == '__main__':
    main()

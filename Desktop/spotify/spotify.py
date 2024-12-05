import spotipy  # type: ignore
from spotipy.oauth2 import SpotifyClientCredentials  # type: ignore
import streamlit as st  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import csv
import base64
import subprocess
from airflow import DAG  # type: ignore
from airflow.operators.python import PythonOperator  # type: ignore
from datetime import datetime, timedelta

# Spotify API Setup
client_id = 'af6606ad86f747378e94fe689730f7b3'  # Replace with your actual client ID
client_secret = '5fdd2d24a374441d873b82c1f8465054'  # Replace with your actual client secret

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Streamlit App
st.title("Spotify Artist Top Tracks")

# Unique keys for each input field
artist = st.text_input("Enter Artist Name", "Tale Of Us", key="artist_input_unique")

# When user clicks the "Search" button
if st.button("Search"):
    with st.spinner('Fetching data...'):
        try:
            # Fetch top tracks of the artist
            results = sp.search(q=artist, limit=15, type='track')
            tracks = results['tracks']['items']

            # If no tracks are found
            if not tracks:
                st.warning(f"No tracks found for artist: {artist}")
            else:
                # Data Processing
                track_names = [track['name'] for track in tracks]
                track_popularity = [track['popularity'] for track in tracks]

                # Display Results
                for track in tracks:
                    st.write(f"Track: {track['name']} | Artist: {track['artists'][0]['name']}")

                # Display Bar Chart
                st.subheader("Track Popularity")
                fig, ax = plt.subplots()
                ax.barh(track_names, track_popularity)
                ax.set_xlabel("Popularity")
                st.pyplot(fig)

                # Save data to CSV
                csv_data = "Track,Artist,Album,Popularity\n"
                for track in tracks:
                    csv_data += f"{track['name']},{track['artists'][0]['name']},{track['album']['name']},{track['popularity']}\n"

                # Provide a download link for CSV
                st.success("Data has been saved.")
                st.markdown(f'<a href="data:file/csv;base64,{base64.b64encode(csv_data.encode()).decode()}" download="tracks.csv">Download CSV</a>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred: {e}")

# Function to run the Spotify data collection script for Airflow
def run_spotify_script():
    subprocess.run(["python", "/Users/viprajkunchakuri/Desktop/spotify/spotify.py"])  # Path to your script

# Airflow DAG Setup
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'spotify_data_collection',
    default_args=default_args,
    description='Automated Spotify Data Collection',
    schedule=timedelta(days=1),  # Runs once a day
    start_date=datetime(2024, 12, 5),  # Adjust the start date
    catchup=False,
)

# Airflow task to run the Spotify script
task = PythonOperator(
    task_id='run_spotify_script',
    python_callable=run_spotify_script,
    dag=dag,
)

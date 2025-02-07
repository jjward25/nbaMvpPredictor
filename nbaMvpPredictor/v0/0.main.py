import os
import subprocess

# Checking if the base player list has been created.
absolute_path = os.path.dirname(__file__)
filename = 'players_since_2009'
csv_file_path = os.path.join(absolute_path, f'{filename}.csv')
script_to_run = 'a.playersL15Y.py'  # The script to create the CSV if it does not exist

# Check if the CSV file exists
if not os.path.exists(csv_file_path):
    print(f"{csv_file_path} does not exist. Running {script_to_run} to create it.")
    try:
        # Execute the script to create the CSV file
        subprocess.run(['python', script_to_run], check=True)
        print(f"{csv_file_path} has been created.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running {script_to_run}: {e}")
else:
    print(f"{csv_file_path} already exists. Proceeding to the next script.")
    # Run the next script here
    next_script = 'next_script.py'  # Update with the actual script you want to run
    subprocess.run(['python', next_script], check=True)

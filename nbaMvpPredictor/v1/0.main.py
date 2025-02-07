import os
import subprocess

# Base directory for your project
project_directory = os.path.dirname(os.path.abspath(__file__))

# Define CSV filenames and full paths
first_csv = 'players.csv'
second_csv = 'players_with_mvp.csv'
first_csv_path = os.path.join(project_directory, first_csv)
second_csv_path = os.path.join(project_directory, second_csv)

# Define scripts and their absolute paths as raw strings
first_script = os.path.join(project_directory, 'a.pastPlayers.py')
second_script = os.path.join(project_directory, 'b.ft.MVPs.py')
final_script = os.path.join(project_directory, 'c.final_script.py')

# Check and create the first CSV file if it doesn't exist
if not os.path.exists(first_csv_path):
    print(f"{first_csv_path} does not exist. Running {first_script} to create it.")
    try:
        subprocess.run(['python', first_script], check=True)
        print(f"{first_csv_path} has been created.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running {first_script}: {e}")
else:
    print(f"{first_csv_path} already exists.")

# Check and create the second CSV file if it doesn't exist
if not os.path.exists(second_csv_path):
    print(f"{second_csv_path} does not exist. Running {second_script} to create it.")
    try:
        subprocess.run(['python', second_script], check=True)
        print(f"{second_csv_path} has been created.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running {second_script}: {e}")
else:
    print(f"{second_csv_path} already exists.")

# Run the final script only if both CSV files exist
if os.path.exists(first_csv_path) and os.path.exists(second_csv_path):
    print("Both CSV files exist. Proceeding to the final script.")
    try:
        subprocess.run(['python', final_script], check=True)
        print(f"{final_script} has completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running {final_script}: {e}")
else:
    print("One or more CSV files are missing. Skipping the final script.")

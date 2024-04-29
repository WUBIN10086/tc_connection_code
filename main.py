#================================================================
# Enter of the project main file
# Last modify date: 2024 04/30
# Author: WU BIN
#================================================================
import configparser
import subprocess
import os

# read configuration file
def read_configuration(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    settings = {
        'path': config.get('Settings', 'Path').strip('"'),
        'gra_location': config.getboolean('Settings', 'Gra_Location'),
        'eng2_location': config.getboolean('Settings', 'Eng#2_Location'),
        'output_file': config.get('Settings', 'output_file').strip('"')
    }
    return settings


def main():
    config_file = r'model/etc/configuration.txt'
    settings = read_configuration(config_file)

    # Construct the full path to the Walls.csv file
    walls_csv_path = os.path.join(settings['path'], 'Walls.csv')
    print("==============================")
    # Check if the Walls.csv file exists at the specified path
    if not os.path.exists(walls_csv_path):
        print(f"Error: 'Walls.csv' not found at path: {walls_csv_path}")
        return  # Exit the program or raise an exception

    # If the file exists, continue with the rest of the program
    print("Walls.csv exists, proceeding with the rest of the program.")
    print("==============================")

    # Check if both locations are set to 1, which is not allowed
    if settings['gra_location'] and settings['eng2_location']:
        print("Error: Both Gra_Location and Eng#2_Location cannot be set to 1 simultaneously.")
        print("==============================")
        return

    # Set the CSV file path based on configuration
    if settings['gra_location']:
        csv_file = settings['path'] + 'Gra_Location.csv'
        print("You are using the map of Graduated Building !")
        print("==============================")
    elif settings['eng2_location']:
        csv_file = settings['path'] + 'Eng_Location.csv'
        print("You are using the map of Engneering Building#2 !")
        print("==============================")
    else:
        print("No valid location configuration found.")
        print("==============================")
        return
    
    # Prepare the arguments for Calc_Plan.py
    csv_path = f"{csv_file}"
    output_file = f"{settings['output_file']}"

    # Call Calc_Plan.py with the necessary arguments
    subprocess.run(['python', 'model/src/Calc_Plan.py', csv_path, output_file, walls_csv_path], check=True)

if __name__ == '__main__':
    main()
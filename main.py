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
        'mode': config.get('Settings', 'Mode'),
        'seed': config.get('Settings', 'RandomSeed'),
        'gra_location': config.getboolean('Settings', 'Gra_Location'),
        'eng2_location': config.getboolean('Settings', 'Eng2_Location'),
        'output_file': config.get('Settings', 'output_file').strip('"')
    }
    settings['mode'] = int(settings['mode'])
    settings['seed'] = int(settings['seed'])
    return settings


def main():
    config_file = r'model/etc/configuration.conf'
    settings = read_configuration(config_file)

    # Choose the programm mode:
    # If the mode=1 will not use active AP algorithm
    if(settings['mode']==0):
        print("==============================")
        print("The system mode(0) is not using active AP choose algorithm")
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
    
    # If the mode=0 will use active AP algorithm
    elif(settings['mode']==1):
        print("==============================")
        print("The system mode(1) is using active AP algorithm")

        # csv path read
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
        csv_path = f"{csv_file}"

        # Random seed read
        # check input random seed:
        if settings['seed'] > 100 or settings['seed'] < 0:
            print("Error! Please check the seed range value!")
        elif settings['seed'] is None:
            print("Error! Please input and save your random seed!") 
        else:
            print("The random seed is:",settings['seed'])
        RandomSeed = settings['seed']
        
        

        subprocess.run(['python', 'model/src/ActiveAP.py', csv_path, RandomSeed], check=True)

    else:
        print("Error! The mode is:", settings['mode'],". Please check the mode setting in configuration.conf")
        return


if __name__ == '__main__':
    main()
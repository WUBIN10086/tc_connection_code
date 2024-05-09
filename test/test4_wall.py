# Load the data
import pandas as pd

Walls_csv_path = 'model\Location\Exp2\Walls.csv'
walls_data = pd.read_csv(Walls_csv_path)

def get_wall_info(ap_name, host_name):
    wall_info = walls_data[(walls_data['AP_Name'] == ap_name) & (walls_data['Host_Name'] == host_name)]
    if not wall_info.empty:
        nk = wall_info.iloc[0, 2:].tolist()  # Accessing columns directly
        return nk
    else:
        print(f"No wall data found for AP {ap_name} and Host {host_name}")
        return [0] * (walls_data.shape[1] - 2)  # Default no impact

# Example usage:
nk = get_wall_info('AP1', 'H1')
print(nk)
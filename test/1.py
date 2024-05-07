import math

c = 299792458 
d =1

RSS1 = -28
RSS2 = -40

f = 2_452_000_000

Pr1 = 10 ** (RSS1 / 10)
Pr2 = 10 ** (RSS2 / 10)
Prd = Pr1 - Pr2

Ptd = Prd + 20 * math.log10(4 * math.pi / c) + 20 * math.log10(f) + 20 * math.log10(d)

RSSd = 10*math.log10(Ptd)

print(Ptd,RSSd)

import matplotlib.pyplot as plt
import numpy as np

# Set temperature range
temperatures = np.linspace(10, 40, 300)
membership_no_water = []
membership_water = []

# Calculate membership functions
for temp in temperatures:
    if temp <= 20:
        membership_no_water.append(1)
    elif 20 < temp < 30:
        membership_no_water.append((30 - temp) / 10)  # Linear decrease
    else:
        membership_no_water.append(0)
    
    if temp >= 30:
        membership_water.append(1)
    elif 20 < temp < 30:
        membership_water.append((temp - 20) / 10)  # Linear increase
    else:
        membership_water.append(0)

# Plotting
plt.figure(figsize=(8, 5))
plt.plot(temperatures, membership_no_water, label='No Water Needed (Low Temperature)', color='blue')
plt.plot(temperatures, membership_water, label='Water Needed (High Temperature)', color='red')
plt.title('Fuzzy Logic Membership Functions for Watering Decision')
plt.xlabel('Temperature (°C)')
plt.ylabel('Membership Degree')
plt.legend()
plt.grid(True)
plt.show()

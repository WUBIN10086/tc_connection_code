# Dual interfaces connection decision code

This code is for Dual interfaces.

Throughput control code is written by Shell, here this code is for calc. best connection assign

## Code List

+ throughput estimation model 
+ throughput reduce model -> concurrent_calc.py

+ Host and AP position -> coordinates.csv
+ Throughput estimation model parameters -> parameters.txt
+ connection decision code -> main.py
+ To be update

## Descriptions

Here will give some descriptions for codes files.

+ concurrent_calc.py is made by Mr.Lu, see it in paper: https://doi.org/10.3390/signals4020015
+ Throughput estimation model also refer to https://doi.org/10.3390/signals4020015
+ the parameters in "parameters.txt" are already optimized by POT

## How to use

Step:

1. Measure the RSS and throughput for new experiment space or new device.
2. use POT to get the optimized parameters.
3. input the parameters in "parameters.txt"
4. decide the position for APs and Hosts.
5. input the coordinates in "coordinates.csv"
6. run main.py
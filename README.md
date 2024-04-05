# Dual interfaces connection decision code

This code is for Dual interfaces.

Throughput control code is written by Shell, here this code is for calc. best connection assign

## To Do

改进位置图，设计网页前端完成AP和Host的坐标

加入墙面的影响

## Code List

+ throughput estimation model
+ throughput reduce model -> concurrent_calc.py
+ Host and AP position -> coordinates.csv
+ Throughput estimation model parameters -> parameters.txt
+ connection decision code -> main.py
+ To be update

## Descriptions

### Reference

Here will give some descriptions for codes files.

+ concurrent_calc.py is made by Mr.Lu, see it in paper: https://doi.org/10.3390/signals4020015
+ Throughput estimation model also refer to https://doi.org/10.3390/signals4020015
+ the parameters in "parameters.txt" are already optimized by POT

---

### Strategy for finding the optimal plan

+ Consider both fairness index and total throughput size
+ The difference  between the total throughput size and the fairness index is large, and normalization is applied to the total throughput size

Normalization for total throughput:

Normalization works by converting data to a common scale so that data of different magnitudes or units can be fairly compared and combined. This is particularly useful when dealing with data that has different ranges, such as in your scenario where the fairness index ranges from 0 to 1 and the total throughput may have a value much greater than 1.

Specifically, this normalization method uses min-max scaling, which converts the range of the data to [0, 1] using the following formula:

Here：

- `value` is a value in the original data.
- `min_value` is the minimum value in the data set.
- `max_value` is the maximum value in the data set.
- `normalized_value` is the normalized value.

$$
normalized_{value}= \frac{（max_{value}−min_{value}）}{ （value−min_{value}）}
$$

In this way, each value in the dataset is converted to a number between 0 and 1, where the minimum value becomes 0, the maximum value becomes 1, and the remaining values are scaled according to their proportions relative to the maximum and minimum values. This allows data that would otherwise be on different scales (e.g., fairness index and total throughput) to be compared and weighted in a uniform manner.

---

### Normalized data

The normalized data is the `total throughput`, such that the size of the total throughput is transformed into a number between 0 and 1, and the `fairness index` is also a number between 0 and 1.

If the difference in total throughput is not too large: (due to fluctuations in throughput during actual experimental testing, the size of the throughput for each Host may fluctuate between 5Mbps up and down)

+ we set $W_1$ as 0.3, $W_2$ as 0.7
+ conversely, set $W_1$ as 0.7, $W_2$ as 0.3

The equation to calculate the scores of each plan is :

$$
scores = ( W_1 * fair~index + W_2 * normalized~total~throughput) * 100
$$

## How to use

Step:

1. Measure the RSS and throughputs for new experiment space or new devices.
2. use POT to get the optimized parameters.
3. input the parameters in "parameters.txt", and here, different parameters date file is for different frequency ( 2.4Ghz or 5Ghz )
4. decide the position for APs and Hosts.
5. input the coordinates in "coordinates.csv"
   coordinates decided by the xlsx file `Floor_Plan_for_estimation`, the row of this file represent the X axis, and column represent the Y axis.
6. input the walls info in "Wall.csv"
7. run main.py
8. see the results in "Output.txt"

## Measurement Setup

+ static ip name rule:

| Host number | 2.4GHz        | 5GHz          |
| ----------- | ------------- | ------------- |
| Host 1      | 192.168.11.12 | 192.168.11.15 |
| Host 2      | 192.168.11.22 | 192.168.11.25 |
| ...         |               |               |

+ channel assignments and devices:

|            2.4Ghz            |           5Ghz           |
| :---------------------------: | :-----------------------: |
|         channel 9+13         |       channel 44+48       |
|        40Mhz bandwidth        |      40Mhz bandwidth      |
| Raspberry pi 4B+ embedded NIC | TP-LINK T4UH external NIC |

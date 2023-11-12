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

### Strategy for finding the optimal plan

+ Consider both fairness index and total throughput size
+ The difference  between the total throughput size and the fairness index is large, and normalization is applied to the total throughput size

Normalization for total throughput:

Normalization works by converting data to a common scale so that data of different magnitudes or units can be fairly compared and combined. This is particularly useful when dealing with data that has different ranges, such as in your scenario where the fairness index ranges from 0 to 1 and the total throughput may have a value much greater than 1.

Specifically, this normalization method uses min-max scaling, which converts the range of the data to [0, 1] using the following formula:

normalized_value=value−min_valuemax_value−min_valuenormalized_value=max_value−min_valuevalue−min_value

Here：

- `value` is a value in the original data.
- `min_value` is the minimum value in the data set.
- `max_value` is the maximum value in the data set.
- `normalized_value` is the normalized value.

$$
normalized_value= \frac{（max_{value}−min_{value}）}{ （value−min_{value}）}
$$

In this way, each value in the dataset is converted to a number between 0 and 1, where the minimum value becomes 0, the maximum value becomes 1, and the remaining values are scaled according to their proportions relative to the maximum and minimum values. This allows data that would otherwise be on different scales (e.g., fairness index and total throughput) to be compared and weighted in a uniform manner.

## How to use

Step:

1. Measure the RSS and throughput for new experiment space or new device.
2. use POT to get the optimized parameters.
3. input the parameters in "parameters.txt"
4. decide the position for APs and Hosts.
5. input the coordinates in "coordinates.csv"
6. run main.py

## Measurement Setup

+ static Ip name rule:

| Host number | 2.4GHz        | 5GHz          |
| ----------- | ------------- | ------------- |
| Host 1      | 192.168.11.12 | 192.168.11.15 |
| Host 2      | 192.168.11.22 | 192.168.11.25 |
| ...         |               |               |


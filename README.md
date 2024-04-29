# Dual interfaces connection decision code

This code is for Dual interfaces.

Throughput control code is written by Shell, here this code is for calc. best connection assign

## Target of this code

This code aim to find the best assignments while using Dual interfaces, it means that the output of this code is the best connection plan, which have better fairness and higher total throughput.

## To Do

+ nothing....

## Code List

The throughput estimation model basic code is in Path://main/src/

+ throughput drop model -> concurrent_calc.py
+ connection decision code -> Calc_Plan.py
+ target fairness throughput calculation -> fairness_calc.py
+ fairness index calculation -> fairness_index.py
+ throughput estimation mode -> throughput_estimation.py

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

1. Please open download the code using `git` or the link.
1. Open this project with VScode (Recommand).
1. Please install the extension of VScode -> Live server
1. Open the file: /html/main/index.html with `Live server` or any other way
1.  Choose your location map: Engineering building #2 or Graduated building
1. Input name of `AP` and `Host` as this way: ==AP1 or H1==
1. Click the AP or Host icon to move and delete, and if need, click the button `Dual interfaces` set this AP as dual band.
1. Click the button `Export CSV` and download the csv file.
1. Copy this file into the path: /model/Location/Your Experiment name, and pls also add a wall.csv file in it.
1. Set the `configuration` and `parameters` in the path: /model/etc.
1. run the main.py
1. see the result in /model/output.

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

## Files structure

```c
Project Tree
├─ .gitignore
├─ FloorPlanExcel  // Useless Floder
│  ├─ Floor_PLan_for_Estimation.xlsx
│  └─ Measurement.csv
├─ html // Use this web Loction Plan
│  ├─ main
│  │  ├─ Eng#2_Location.html
│  │  ├─ Gra_Location.html
│  │  └─ index.html // Please open the index.html when you use it
│  └─ test
├─ model
│  ├─ etc // put the config and setting here!
│  │  ├─ configuration.txt
│  │  ├─ parameters.txt
│  │  └─ parameters2.txt
│  ├─ Location // import the location here!
│  │  ├─ Exp1
│  │  │  ├─ Eng_Location.csv
│  │  │  └─ Walls.csv
│  │  └─ Exp2
│  │     └─ Eng_Location.csv
│  ├─ output // see the result here!
│  │  └─ 1AP_3H_Eng.txt
│  └─ src // simulation functions
│     ├─ Calc_Plan.py
│     ├─ concurrent_calc.py
│     ├─ fairness_calc.py
│     ├─ fairness_index.py
│     ├─ throughput_estimation.py
│     └─ write_to_output.py
├─ main.py // the enter of the project, Please run this
├─ README.md
└─ test // Please ignore
   ├─ coordinates.csv
   ├─ d_estimate.py
   ├─ fairness_test.py
   ├─ index.py
   ├─ template.py
   ├─ test1.py
   ├─ test2.py
   ├─ test3.py
   └─ throughput_estimation.py

```


import matplotlib.pyplot as plt

# Data for plotting
categories = ['Max Power', 'Optimized Power']
values = [128.23, 106.43]

# Creating the bar plot with a softer color palette and larger figure
plt.figure(figsize=(10, 8))  # Increased figure size for better visibility
plt.bar(categories, values, color=['#3498db', '#2ecc71'])  # Using softer shades of blue and green
plt.title('Throughput Comparison', fontsize=25)
plt.ylabel('Throughput (mBps)', fontsize=18)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.ylim(0, max(values) + 10)  # Adjusting y-axis limit to add some space above the tallest bar

# Adding value labels on top of the bars
for index, value in enumerate(values):
    plt.text(index, value + 1, f'{value:.2f}', ha='center', va='bottom', fontsize=20)

# Display the improved plot
plt.show()

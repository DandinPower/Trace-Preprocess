import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Create DataFrame
data = {
    'Sequential Rate': [0.12921, 0.07365, 0.03502, 0.16109, 0.769, 0.06074, 0.05773, 0.05662, 0.05197, 0.07722, 0.0383, 0.0804],
    'Total Data Write': [18.091, 6.172, 10.35, 15.379, 2.05, 7.49, 6.051, 7.588, 7.145, 8.347, 7.014, 7.445],
    'Total Footprint': [9.294, 1.136, 5.402, 2.909, 0.237, 0.496, 0.745, 0.562, 0.37, 0.795, 0.64, 0.936],
    'LBA Range': [103.597, 13.939, 363.285, 16.24, 20.714, 16.891, 15.627, 10.788, 21.973, 15.893, 16.955, 33.909]
}

df = pd.DataFrame(data)

print(df.describe())

# Initialize an outlier counter array with zeros
outlier_count = np.zeros(df.shape[0])

# Calculate outlier rate
for column in df:
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    # defining the upper and lower whiskers
    lower_whisker = Q1 - 1.5*IQR
    upper_whisker = Q3 + 1.5*IQR

    # Add 1 to the counter for each trace that is an outlier in this column
    outlier_count += ((df[column] < lower_whisker) | (df[column] > upper_whisker)).to_numpy()
print(outlier_count)

# Get index of trace with maximum number of outliers
max_outlier_index = np.argmax(outlier_count)
print(f"Trace with the highest number of outliers: {max_outlier_index}")

# Box Plots
df.boxplot()
plt.yscale('log')
plt.savefig('box.png', dpi=300)

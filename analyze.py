from collections import namedtuple
import csv

LENGTH = 1000000

sequential_count = 0
random_count = 0
total_footprint = 0
min_lba = 0
max_lba = 0

Request = namedtuple('Request', ['lba', 'bytes'])

with open('trace/temp/temp_stg_0.csv', 'r') as file:
    reader = csv.reader(file)
    # next(reader)  # Skip the header row, if present
    traces = []
    for index, row in enumerate(reader):
        lba = int(row[2])
        bytes = int(row[3])
        traces.append(Request(lba, bytes))
        if index == LENGTH - 1:
            break
        
    if traces[0].lba + traces[0].bytes == traces[1].lba:
        sequential_count += 1
    else:
        random_count += 1
    min_lba = traces[0].lba
    max_lba = traces[0].lba

    if traces[-2].lba + traces[-2].bytes == traces[-1].lba:
        sequential_count += 1
    else:
        random_count += 1
    total_footprint += traces[0].bytes
    total_footprint += traces[-1].bytes


    for i in range(1, len(traces) - 1):
        min_lba = min(min_lba, traces[i].lba)
        max_lba = max(max_lba, traces[i].lba)
        if (traces[i - 1].lba + traces[i - 1].bytes == traces[i].lba) or (traces[i].lba + traces[i].bytes == traces[i + 1].lba):
            sequential_count += 1
        else:
            random_count += 1
        total_footprint += traces[i].bytes

    total_entries = sequential_count + random_count
    sequential_percentage = (sequential_count / total_entries) * 100
    random_percentage = (random_count / total_entries) * 100

print(f"Sequential Percentage: {sequential_percentage}%")
print(f"Random Percentage: {random_percentage}%")
print(f"Total Footprint: {total_footprint / (1024 * 1024 * 1024):.2f} GB")
print(f"LBA Range: {max_lba / (1024 * 1024 * 1024)} - {min_lba / (1024 * 1024 * 1024)} GB")
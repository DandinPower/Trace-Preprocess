import multiprocessing
from collections import namedtuple
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm
import os

LENGTH = 900000
BYTES_HIST_MIN = 0
BYTES_HIST_MAX = 100000
BYTES_HIST_BINS = 50
Request = namedtuple('Request', ['lba', 'bytes'])

def Analyze(traceName):
    traces = []

    # 用來計算Sequential & Random Ratio
    sequential_count = 0
    random_count = 0

    # 用來計算總寫入量
    total_data_write = 0

    # 用來計算Lba的Total Range
    min_lba = 0
    max_lba = 0

    # 用來計算總共接觸到的資料
    subRanges = []
    total_footprint = 0

    df = pd.read_csv(f'trace/temp/{traceName}.csv')
    total_length = min(LENGTH, len(df))
    for index, row in tqdm(df.iterrows(), total=total_length, desc=f'Load Trace: {traceName} into memory...'):
        if index >= total_length:
            break
        
        lba = int(row[2])
        bytes = int(row[3])
        traces.append(Request(lba, bytes))

        currentSubRange = [lba, lba + bytes - 1]       
        merged = False
        for i, subRange in enumerate(subRanges):
            if currentSubRange[1] < subRange[0] - 1:
                subRanges.insert(i, currentSubRange)
                merged = True
                break
            elif currentSubRange[0] <= subRange[1] + 1:
                subRange[0] = min(subRange[0], currentSubRange[0])
                subRange[1] = max(subRange[1], currentSubRange[1])
                merged = True
                break
        if not merged:
            subRanges.append(currentSubRange)

    if traces[0].lba + traces[0].bytes == traces[1].lba:
            sequential_count += 1
    else:
        random_count += 1

    if traces[-2].lba + traces[-2].bytes == traces[-1].lba:
        sequential_count += 1
    else:
        random_count += 1

    total_data_write += traces[0].bytes
    total_data_write += traces[-1].bytes

    min_lba = traces[0].lba
    max_lba = traces[0].lba

    for i in range(1, len(traces) - 1):
        min_lba = min(min_lba, traces[i].lba)
        max_lba = max(max_lba, traces[i].lba)
        if (traces[i - 1].lba + traces[i - 1].bytes == traces[i].lba) or (traces[i].lba + traces[i].bytes == traces[i + 1].lba):
            sequential_count += 1
        else:
            random_count += 1
        total_data_write += traces[i].bytes

    total_entries = sequential_count + random_count
    sequential_percentage = (sequential_count / total_entries) * 100
    random_percentage = (random_count / total_entries) * 100
    total_footprint = sum(end - start + 1 for start, end in subRanges)

    with open(f'analyze/report/{traceName}.txt', 'w') as file:
        file.write(f"Trace Length: {total_length}\n")
        file.write(f"Sequential Percentage: {sequential_percentage:.3f}%\n")
        file.write(f"Random Percentage: {random_percentage:.3f}%\n")
        file.write(f"Total Data Write: {total_data_write / (1024 * 1024 * 1024):.3f} GB\n")
        file.write(f"Total Footprint: {total_footprint / (1024 * 1024 * 1024):.3f} GB\n")
        file.write(f"LBA Range: {max_lba / (1024 * 1024 * 1024):.3f} - {min_lba / (1024 * 1024 * 1024):.3f} GB\n")

    # Get the list of byte sizes
    byte_sizes = [req.bytes for req in traces]

    # Plot the histogram
    plt.hist(byte_sizes, bins=BYTES_HIST_BINS, range=(BYTES_HIST_MIN, BYTES_HIST_MAX), edgecolor='black')

    # Add labels and title
    plt.xlabel('Bytes')
    # plt.ylabel('Count (log scale)')
    plt.ylabel('Count')
    # plt.yscale('log')
    plt.title('Bytes Distribution')

    # Display the plot
    plt.savefig(f'analyze/image/{traceName}.png', dpi=300)
    plt.close()
    # print(f"Trace {traceName} Done!")

def main():
    trace_directory = 'trace/temp'
    trace_files = [f for f in os.listdir(trace_directory) if f.endswith('.csv')]

    processes = []
    for trace_file in trace_files:
        trace_name = os.path.splitext(trace_file)[0]
        p = multiprocessing.Process(target=Analyze, args=(trace_name,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

if __name__ == "__main__":
    main()
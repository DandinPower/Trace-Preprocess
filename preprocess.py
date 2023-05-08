from statistic import Entries
from host_request_queue import HostRequestQueue
import csv
from tqdm import tqdm
from dotenv import load_dotenv
import os
load_dotenv()

TRACE_PATH = os.getenv('TRACE_PATH')
FIRST_STEP_PATH = os.getenv('FIRST_STEP_PATH')
TRACE_OUTPUT_PATH = os.getenv('TRACE_OUTPUT_PATH')
LBA_FREQ_PATH = os.getenv('LBA_FREQ_PATH')

def GetLbaFreq():
    lba_frequency = {}
    with open(TRACE_OUTPUT_PATH, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            lba = row[2]
            if lba in lba_frequency:
                lba_frequency[lba] += 1
            else:
                lba_frequency[lba] = 1
    sorted_lba_frequency = sorted(lba_frequency.items(), key=lambda x: x[1], reverse=True)
    with open(LBA_FREQ_PATH, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['LBA', 'Frequency'])
        for lba, frequency in sorted_lba_frequency:
            writer.writerow([lba, frequency])

def GetTraceLength():
    with open(FIRST_STEP_PATH, 'r') as file_in:
        reader = csv.reader(file_in)
        return len(list(reader)) - 1

def GetTargetAnswer():
    TRACE_LENGTH = GetTraceLength()
    print(f'TRACE_LENGH: {TRACE_LENGTH}')
    queue = HostRequestQueue()
    queue.LoadTrace(FIRST_STEP_PATH)
    entries = Entries()
    for i in tqdm(range(TRACE_LENGTH), desc='Processing requests'):
        req = queue.GetWriteRequest()
        entries.Add(req.fid, req.lba, req.bytes)
    entries.Write(TRACE_OUTPUT_PATH)

def Preprocess():
    # Open input and output files
    with open(TRACE_PATH, 'r') as file_in, open(FIRST_STEP_PATH, 'w', newline='') as file_out:
        reader = csv.reader(file_in)
        writer = csv.writer(file_out)
        # Process each row in the input file
        for row in reader:
            # Extract relevant fields from the current row
            fid = row[0]
            hostname = row[1]
            core_number = row[2]
            operation_type = row[3]
            lba = row[4]
            offset = row[5]
            # Convert operation type to '2' if it's 'Write', otherwise skip the row
            if operation_type == 'Write':
                # Write the desired fields to the output file
                writer.writerow(['2', fid, lba, offset])
    print("Preprocessing complete.")

def main():
    # Preprocess()
    # GetTargetAnswer()
    GetLbaFreq()

if __name__ == "__main__":
    main()
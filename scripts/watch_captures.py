import subprocess
import os
import glob
import time

from ingest_zeek_logs import parse_conn_log

CAPTURES_DIR="captures"
PROCESSED_DIR="captures/processed"
ERROR_DIR="captures/error"
INGESTED_DIR="captures/ingested"
BASE_BACKOFF = 10 # seconds
MAX_RETRIES = 3

def process_pcap(filepath):
    print(f"Processing {filepath}...")
    subprocess.run([
        'docker', 'run', '--rm',
        '-v', f'{os.path.abspath(filepath)}:/capture.pcap',
        '-v', f'{os.path.abspath("zeek_logs")}:/zeek_logs',
        '--workdir', '/zeek_logs',
        'zeek/zeek', 'zeek', '-r', '/capture.pcap'
    ], check=True, capture_output=True, text=True)
   
    
def move_to_processed(filepath):
    os.rename(filepath, os.path.join(PROCESSED_DIR, os.path.basename(filepath)))

def move_to_error(filepath):
    os.rename(filepath, os.path.join(ERROR_DIR, os.path.basename(filepath)))

def next_retry_time(attempt):
    return time.time() + BASE_BACKOFF * (2 ** (attempt - 1))

def is_still_writing(filepath):
    initial_size = os.path.getsize(filepath)
    time.sleep(1)
    return os.path.getsize(filepath) != initial_size

def is_ready(filepath, min_age_seconds=5):
    file_age = time.time() - os.path.getmtime(filepath)
    return file_age > min_age_seconds

def watch():
    seen = set()
    failures = {} # filepath -> retry count
    retry_after = {} # filepath -> timestamp when eligible for retry

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(ERROR_DIR, exist_ok=True)

    while True:
        files = glob.glob(f'{CAPTURES_DIR}/*.pcap')
        for f in files:
            if f in seen:
                continue

            if time.time() < retry_after.get(f, 0):
                continue

            if is_still_writing(f) or not is_ready(f):
                print(f"Skipping {f}, still being written...")
                continue

            if failures.get(f, 0) >= MAX_RETRIES:
                print(f"PERMANENT FAILURE: {f}. Moving to error/")
                try:
                    move_to_error(f)
                except OSError:
                    print(f"Warning: Failed to move {f} to errors/ after exceeding retry limit.")
                finally:
                    seen.add(f)
                continue
            try:
                process_pcap(f)
                move_to_processed(f)
                seen.add(f)
            except subprocess.CalledProcessError as e:
                failures[f] = failures.get(f, 0) + 1
                retry_after[f] = next_retry_time(failures[f])
                print(f"Zeek failed to process {f} (attempt {failures[f]}/{MAX_RETRIES}): {e}")
                print(f"stderr: {e.stderr}")
                print(f"stdout: {e.stdout}")
            except OSError as e:
                print(f"Warning: Zeek succeeded in processing {f} but move failed: {e}")
                seen.add(f)
        time.sleep(10)

if __name__ == "__main__":
    try:
        watch()
    except KeyboardInterrupt:
        print("\stopping watcher.")
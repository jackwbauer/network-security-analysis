import os
import sys
import django
from datetime import datetime, timezone

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from log_entries.models import ZeekConnLog

UNSET = '-'
EMPTY = '(empty)'

def parse_value(value):
    """Return NONE for empty and unset values"""
    if value in (UNSET, EMPTY):
        return None
    return value

def parse_bool(value):
    if value in (UNSET, EMPTY):
        return None
    return value == "T"


def parse_conn_log(filepath):
    fields = []
    entries = []

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("#fields"):
                fields = line.split("\t")[1:]
                continue

            if line.startswith("#"):
                continue

            if not line:
                continue

            values = line.split('\t')
            row = dict(zip(fields, values))

            try:
                entry = ZeekConnLog(
                    timestamp       = datetime.fromtimestamp(float(row['ts']), tz=timezone.utc),
                    uid             = row.get('uid'),
                    source_ip       = parse_value(row.get('id.orig_h')),
                    source_port     = parse_value(row.get('id.orig_p')),
                    dest_ip         = parse_value(row.get('id.resp_h')),
                    dest_port       = parse_value(row.get('id.resp_p')),
                    protocol        = parse_value(row.get('proto')),
                    service         = parse_value(row.get('service')),
                    duration        = parse_value(row.get('duration')),
                    bytes_orig      = parse_value(row.get('orig_bytes')),
                    bytes_resp      = parse_value(row.get('resp_bytes')),
                    missed_bytes    = parse_value(row.get('missed_bytes')),
                    orig_pkts       = parse_value(row.get('orig_pkts')),
                    orig_ip_bytes   = parse_value(row.get('orig_ip_bytes')),
                    resp_pkts       = parse_value(row.get('resp_pkts')),
                    resp_ip_bytes   = parse_value(row.get('resp_ip_bytes')),
                    conn_state      = parse_value(row.get('conn_state')),
                    history         = parse_value(row.get('history')),
                    local_orig      = parse_bool(row.get('local_orig')),
                    local_resp      = parse_bool(row.get('local_resp')),
                    tunnel_parents  = parse_value(row.get('tunnel_parents')),
                    ip_proto        = parse_value(row.get('ip_proto')),
                )
                entries.append(entry)
            except Exception as e:
                print(f"Skipping row due to error: {e} - {row}")

    ZeekConnLog.objects.bulk_create(entries, batch_size=500)
    print(f"Inserted {len(entries)} records into ZeekConfigLog")
            
if __name__ == "__main__":
    log_path = sys.argv[1] if len(sys.argv) > 1 else "zeek_logs/conn.log"
    parse_conn_log(log_path)
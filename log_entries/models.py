from django.db import models

class LogEntry(models.Model):
    timestamp = models.DateTimeField(db_index =True)
    host_name = models.CharField()
    process_name = models.CharField()
    process_id = models.PositiveIntegerField()
    raw_message = models.CharField(max_length =255)
    source = models.CharField()
    source_ip = models.CharField()
    source_port = models.PositiveIntegerField()
    destination_ip = models.CharField()
    event_type = models.CharField()
    ssh_key_fingerprint = models.CharField()
    username = models.CharField()
    tty = models.CharField()
    working_directory = models.CharField()
    target_user = models.CharField()
    command = models.CharField()
    session_action = models.CharField()
    pam_service = models.CharField()
    session_id = models.CharField()

class ZeekConnLog(models.Model):
    timestamp       = models.DateTimeField(db_index=True)
    uid             = models.CharField(max_length=20, unique=True, db_index=True)
    source_ip       = models.GenericIPAddressField(db_index=True)
    source_port     = models.PositiveIntegerField()
    dest_ip         = models.GenericIPAddressField(db_index=True)
    dest_port       = models.PositiveIntegerField()
    protocol        = models.CharField(max_length=20)
    service         = models.CharField(max_length=50, null=True, blank=True)

    # Traffic stats
    duration        = models.FloatField(null=True, blank=True)
    bytes_orig      = models.BigIntegerField(null=True, blank=True)
    bytes_resp      = models.BigIntegerField(null=True, blank=True)
    missed_bytes    = models.BigIntegerField(null=True, blank=True)
    orig_pkts       = models.BigIntegerField(null=True, blank=True)
    orig_ip_bytes   = models.BigIntegerField(null=True, blank=True)
    resp_pkts       = models.BigIntegerField(null=True, blank=True)
    resp_ip_bytes   = models.BigIntegerField(null=True, blank=True)

    # Connection details
    conn_state      = models.CharField(max_length=20, null=True, blank=True)
    history         = models.CharField(max_length=50, null=True, blank=True)
    local_orig      = models.BooleanField(null=True, blank=True)
    local_resp      = models.BooleanField(null=True, blank=True)
    tunnel_parents  = models.CharField(max_length=255, null=True, blank=True)
    ip_proto        = models.PositiveIntegerField(null=True, blank=True)

    ingested_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'conn_state']),
            models.Index(fields=['source_ip', 'dest_ip']),
        ]

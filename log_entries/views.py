from django.shortcuts import render

from .models import ZeekConnLog
from django.db.models import Count


def conn_log_list(request):
    queryset = ZeekConnLog.objects.all().order_by('-timestamp')

    source_ip = request.GET.get('source_id')
    dest_port = request.GET.get('dest_port')
    service = request.GET.get('service')
    conn_state = request.GET.get('conn_state')

    if source_ip:
        queryset.filter(source_ip = source_ip)
    if dest_port:
        queryset.filter(dest_port = dest_port)
    if service:
        queryset.filter(service = service)
    if conn_state:
        queryset.filter(conn_state = conn_state)

    services = ZeekConnLog.objects.values_list('service', flat=True).distinct()
    conn_states = ZeekConnLog.objects.values_list('conn_state', flat=True).distinct()

    total = ZeekConnLog.objects.count()

    top_source_ips = ZeekConnLog.objects.values("source_ip").annotate(count=Count("id")).order_by("-count")[:5]
    top_dest_ports = ZeekConnLog.objects.values("dest_port").annotate(count=Count("id")).order_by("-count")[:5]
    count_by_service = ZeekConnLog.objects.values("service").annotate(count=Count("id")).order_by("-count")
    count_by_conn_state = ZeekConnLog.objects.values("conn_state").annotate(count=Count("id")).order_by("-count")

    context = {
        'zeek_conn_logs': queryset[:500],
        'services': services,
        'conn_states': conn_states,
        'total': total,
        'top_source_ips': top_source_ips,
        "top_dest_ports": top_dest_ports,
        "count_by_service": count_by_service,
        "count_by_conn_state": count_by_conn_state,
        'filters': request.GET
    }

    return render(request, 'log_entries/conn_log_list.html', context)
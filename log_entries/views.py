from django.shortcuts import render

from .models import ZeekConnLog
from django.db.models import Count
from django.core.paginator import Paginator
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse


def conn_log_list(request):
    queryset = ZeekConnLog.objects.all().order_by('-timestamp')

    source_ip = request.GET.get('source_ip')
    dest_port = request.GET.get('dest_port')
    service = request.GET.get('service')
    conn_state = request.GET.get('conn_state')

    if source_ip:
        queryset = queryset.filter(source_ip__icontains = source_ip)
    if dest_port:
        queryset = queryset.filter(dest_port = dest_port)
    print('before:', queryset.query)
    if service:
        print("setting service filter")
        queryset = queryset.filter(service = service)
    print('after:', queryset.query)
    if conn_state:
        queryset = queryset.filter(conn_state = conn_state)

    paginator = Paginator(queryset, 50)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    services = set(ZeekConnLog.objects.values_list('service', flat=True).distinct())
    conn_states = set(ZeekConnLog.objects.values_list('conn_state', flat=True).distinct())

    total = ZeekConnLog.objects.count()

    top_source_ips = ZeekConnLog.objects.values("source_ip").annotate(count=Count("id")).order_by("-count")[:5]
    top_dest_ports = ZeekConnLog.objects.values("dest_port").annotate(count=Count("id")).order_by("-count")[:5]
    count_by_service = ZeekConnLog.objects.values("service").annotate(count=Count("id")).order_by("-count")
    count_by_conn_state = ZeekConnLog.objects.values("conn_state").annotate(count=Count("id")).order_by("-count")

    context = {
        'zeek_conn_logs': page,
        'services': services,
        'conn_states': conn_states,
        'total': total,
        'top_source_ips': top_source_ips,
        "top_dest_ports": top_dest_ports,
        "count_by_service": count_by_service,
        "count_by_conn_state": count_by_conn_state,
        'filters': request.GET,
    }

    return render(request, 'log_entries/conn_log_list.html', context)

def conn_log_list_live(request):
    queryset = ZeekConnLog.objects.all()

    source_ip = request.GET.get('source_ip')
    dest_port = request.GET.get('dest_port')
    service = request.GET.get('service')
    conn_state = request.GET.get('conn_state')

    if source_ip:
        queryset = queryset.filter(source_ip__icontains = source_ip)
    if dest_port:
        queryset = queryset.filter(dest_port = dest_port)
    if service:
        queryset = queryset.filter(service = service)
    if conn_state:
        queryset = queryset.filter(conn_state = conn_state)

    paginator = Paginator(queryset, 50)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    services = set(ZeekConnLog.objects.values_list('service', flat=True).distinct())
    print(services)
    conn_states = set(ZeekConnLog.objects.values_list('conn_state', flat=True).distinct())
    context = {
        'services': services,
        'conn_states': conn_states,
        'filters': request.GET
    }
    return render(request, 'log_entries/conn_log_list_live.html', context)

def conn_log_feed(request):
    queryset = ZeekConnLog.objects.all().order_by('-timestamp')

    source_ip = request.GET.get('source_ip')
    dest_port = request.GET.get('dest_port')
    service = request.GET.get('service')
    conn_state = request.GET.get('conn_state')

    if source_ip:
        queryset = queryset.filter(source_ip__icontains = source_ip)
    if dest_port:
        queryset = queryset.filter(dest_port = dest_port)
    if service:
        queryset = queryset.filter(service = service)
    if conn_state:
        queryset = queryset.filter(conn_state = conn_state)

    since = timezone.now() - timedelta(seconds=60)
    logs = (
        # queryset.filter(ingested_at__gte=since)[:50]
        ZeekConnLog.objects
        .filter(ingested_at__gte=since)
        # .order_by('-timestamp')[:50]
        .values(
            'timestamp', 'uid', 'source_ip', 'source_port',
            'dest_ip', 'dest_port', 'protocol', 'service',
            'conn_state', 'duration', 'bytes_orig', 'bytes_resp'
        )

    )
    return JsonResponse({'zeek_conn_logs': list(logs)}, json_dumps_params={'default': str})
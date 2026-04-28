capture:
	sudo tcpdump -i en0 -w captures/capture-%s.pcap -G 60

watch:
	python scripts/watch_captures.py
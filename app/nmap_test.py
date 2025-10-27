import nmap

nm = nmap.PortScanner()

target_host = '127.0.0.1'  # Replace with the IP or hostname you want to scan
ports_to_scan = '21-80,443'  # Scan ports 21-80 and 443

#arguments='-sV' # is added for service and version detection
nm.scan(target_host, ports_to_scan, arguments='-sV')

for host in nm.all_hosts():
    print(f'Host: {host} ({nm[host].hostname()})')
    print(f'State: {nm[host].state()}')

    # Iterate through all protocols (tcp, udp, etc.)
    for proto in nm[host].all_protocols():
        print(f'Protocol: {proto}')

        # Iterate through all scanned ports for the current protocol
        lport = nm[host][proto].keys()
        for port in lport:
            print(f'Port: {port}\tState: {nm[host][proto][port]["state"]}')
            print(f'Service: {nm[host][proto][port]["name"]}')
            print(f'Product: {nm[host][proto][port]["product"]}')
            print(f'Version: {nm[host][proto][port]["version"]}')
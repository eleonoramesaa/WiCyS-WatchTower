import pyshark

def live_capture(interface="Wi-Fi", packet_limit=10):
    """
    Captures live packets from the given network interface.
    Displays protocol, timestamp, source IP, and destination IP.
    """

    print(f" Starting live capture on interface: {interface}")
    print(f" Capturing {packet_limit} packets...\n")

    # Start live capture
    capture = pyshark.LiveCapture(interface=interface)

    # Sniff packets continuously (up to the limit)
    for i, packet in enumerate(capture.sniff_continuously(packet_count=packet_limit), start=1):
        print(f"Packet #{i}")
        print(f"  Timestamp: {packet.sniff_time}")
        print(f"  Protocol: {packet.highest_layer}")

        # Extract IP layer info safely
        if hasattr(packet, 'ip'):
            print(f"  Source IP: {packet.ip.src}")
            print(f"  Destination IP: {packet.ip.dst}")
        else:
            print("  (No IP layer detected)")

        print("-" * 50)

    print("\n✅ Capture complete!")

if __name__ == "__main__":
    # Change interface name based on your system
    # e.g., "Wi-Fi", "Ethernet", "en0", or "eth0"
    live_capture(interface="Wi-Fi", packet_limit=10)

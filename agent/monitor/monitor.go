package monitor

import (
	"fmt"
	"log"
	"time"

	"github.com/google/gopacket"
	"github.com/google/gopacket/pcap"
)

type PacketMonitor struct {
	iface      string
	handle     *pcap.Handle
	packetChan chan gopacket.Packet
	done       chan struct{}
}

func NewPacketMonitor(iface string, snapshotLen int32, promisc bool, timeout time.Duration) (*PacketMonitor, error) {
	// Open the network interface
	handle, err := pcap.OpenLive(iface, snapshotLen, promisc, timeout)
	if err != nil {
		return nil, fmt.Errorf("failed to open interface %s: %w", iface, err)
	}

	// Set a BPF filter to only capture IP traffic (optional)
	if err := handle.SetBPFFilter("ip"); err != nil {
		log.Printf("Warning: Could not set BPF filter: %v", err)
	}

	return &PacketMonitor{
		iface:      iface,
		handle:     handle,
		packetChan: make(chan gopacket.Packet, 1000), // Buffer up to 1000 packets
		done:       make(chan struct{}),
	}, nil
}

func (m *PacketMonitor) Start() (<-chan gopacket.Packet, error) {
	// Create a new packet data source
	packetSource := gopacket.NewPacketSource(m.handle, m.handle.LinkType())
	packetSource.NoCopy = true
	packetSource.Lazy = true

	// Start a goroutine to read packets
	go func() {
		defer close(m.packetChan)
		
		for {
			select {
			case packet, ok := <-packetSource.Packets():
				if !ok {
					// Channel was closed
					return
				}
				select {
				case m.packetChan <- packet:
					// Packet sent to channel
				case <-m.done:
					return
				}
			case <-m.done:
				return
			}
		}
	}()

	return m.packetChan, nil
}

func (m *PacketMonitor) Stop() {
	if m.handle != nil {
		m.handle.Close()
	}
	close(m.done)
}

// StartPacketMonitor is a convenience function to start monitoring on an interface
func StartPacketMonitor(iface string) (<-chan gopacket.Packet, error) {
	monitor, err := NewPacketMonitor(iface, 1600, true, pcap.BlockForever)
	if err != nil {
		return nil, err
	}

	packetChan, err := monitor.Start()
	if err != nil {
		return nil, err
	}

	return packetChan, nil
}

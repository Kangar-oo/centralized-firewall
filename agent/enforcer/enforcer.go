package enforcer

import (
	"log"
	"sync"

	"github.com/xhhbbshbsj/centralized-firewall/agent/api"
	"github.com/xhhbbshbsj/centralized-firewall/agent/rules"
	"github.com/google/gopacket"
)

type Enforcer struct {
	ruleManager *rules.RuleManager
	packetChan  <-chan gopacket.Packet
	apiClient   *api.Client
	stopChan    chan struct{}
	wg          sync.WaitGroup
}

func NewEnforcer(ruleManager *rules.RuleManager, packetChan <-chan gopacket.Packet, apiClient *api.Client) *Enforcer {
	return &Enforcer{
		ruleManager: ruleManager,
		packetChan:  packetChan,
		apiClient:   apiClient,
		stopChan:    make(chan struct{}),
	}
}

func (e *Enforcer) Start() {
	e.wg.Add(1)
	defer e.wg.Done()

	for {
		select {
		case packet, ok := <-e.packetChan:
			if !ok {
				// Channel closed
				return
			}
			e.processPacket(packet)

		case <-e.stopChan:
			return
		}
	}
}

func (e *Enforcer) Stop() {
	close(e.stopChan)
	e.wg.Wait()
}

func (e *Enforcer) processPacket(packet gopacket.Packet) {
	allow, action := e.ruleManager.CheckPacket(packet)

	// If the packet should be blocked, we need to implement the actual blocking logic here
	// For now, we'll just log it
	if !allow {
		e.handleBlockedPacket(packet, action)
	}
}

func (e *Enforcer) handleBlockedPacket(packet gopacket.Packet, reason string) {
	networkLayer := packet.NetworkLayer()
	if networkLayer == nil {
		return
	}

	src, dst := networkLayer.NetworkFlow().Endpoints()
	srcIP := src.String()
	dstIP := dst.String()

	log.Printf("🚫 Blocked packet: %s → %s | Reason: %s", srcIP, dstIP, reason)

	// Send to server
	go e.apiClient.SendLog("BLOCKED_PACKET", "Blocked packet", map[string]interface{}{
		"source_ip":      srcIP,
		"destination_ip": dstIP,
		"reason":         reason,
		"protocol":       networkLayer.LayerType().String(),
	})
}

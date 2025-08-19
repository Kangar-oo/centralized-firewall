package main

import (
	"fmt"
	"log"
	"net"
	"sync"
	"time"

	"centralized-firewall/agent/api"
	"centralized-firewall/agent/config"

	"github.com/google/gopacket"
)

type RuleManager struct {
	rules     []api.Rule
	rulesLock sync.RWMutex
	apiClient *api.Client
}

func NewRuleManager(apiClient *api.Client) *RuleManager {
	return &RuleManager{
		rules:     make([]api.Rule, 0),
		apiClient: apiClient,
	}
}

func (rm *RuleManager) StartSync(interval time.Duration) {
	// Initial sync
	if err := rm.SyncRules(); err != nil {
		log.Printf("Initial rule sync failed: %v", err)
	}

	// Periodic sync
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for range ticker.C {
		if err := rm.SyncRules(); err != nil {
			log.Printf("Rule sync failed: %v", err)
		}
	}
}

func (rm *RuleManager) SyncRules() error {
	rules, err := rm.apiClient.GetRules()
	if err != nil {
		return fmt.Errorf("failed to fetch rules: %w", err)
	}

	rm.rulesLock.Lock()
	rm.rules = rules
	rm.rulesLock.Unlock()

	log.Printf("Synced %d rules from server", len(rules))
	return nil
}

func (rm *RuleManager) CheckPacket(packet gopacket.Packet) (bool, string) {
	networkLayer := packet.NetworkLayer()
	if networkLayer == nil {
		return true, "no_network_layer"
	}

	src, dst := networkLayer.NetworkFlow().Endpoints()
	srcIP := net.ParseIP(src.String())
	dstIP := net.ParseIP(dst.String())

	// Default to allow if no rules match
	action := "ALLOW"
	rm.rulesLock.RLock()
	defer rm.rulesLock.RUnlock()

	for _, rule := range rm.rules {
		if !rule.IsActive {
			continue
		}

		// Check if packet matches rule
		if matchesRule(rule, srcIP, dstIP) {
			action = rule.Action
			break
		}
	}

	// Log the action
	logMsg := fmt.Sprintf("Packet %s → %s | Action: %s", srcIP, dstIP, action)
	go rm.apiClient.SendLog("PACKET", logMsg, map[string]interface{}{
		"source_ip":      srcIP.String(),
		"destination_ip": dstIP.String(),
		"action":         action,
	})

	return action == "ALLOW", action
}

func matchesRule(rule api.Rule, srcIP, dstIP net.IP) bool {
	// Check source IP
	if rule.SourceIP != nil && *rule.SourceIP != "" && *rule.SourceIP != srcIP.String() {
		return false
	}

	// Check destination IP
	if rule.DestinationIP != nil && *rule.DestinationIP != "" && *rule.DestinationIP != dstIP.String() {
		return false
	}

	// TODO: Add protocol and port matching

	return true
}

// StartEnforcer starts the packet processing loop
func StartEnforcer(ruleManager *RuleManager) {
	for packet := range PacketChannel {
		allow, action := ruleManager.CheckPacket(packet)
		if !allow {
			// TODO: Implement actual packet dropping logic
			log.Printf("Blocked packet: %s", action)
		}
	}
}

// Enforcer.go

package main

import (
	"fmt"
	"net"
	"strings"

	"github.com/google/gopacket"
)

var rules []string

func LoadRules() {
	// TODO: Fetch rules from server
	rules = []string{
		"BLOCK:192.168.1.100",
		"ALLOW:8.8.8.8",
	}
	fmt.Println("📜 Loaded Rules:", rules)
}

func StartEnforcer() {
	for packet := range PacketChannel {
		networkLayer := packet.NetworkLayer()
		if networkLayer == nil {
			continue
		}

		src, dst := networkLayer.NetworkFlow().Endpoints()
		srcIP := net.ParseIP(src.String())
		dstIP := net.ParseIP(dst.String())

		action := CheckRules(dstIP.String())

		logMsg := fmt.Sprintf("Packet %s → %s | Action: %s", srcIP, dstIP, action)
		fmt.Println("⚡", logMsg)

		// Send to server
		SendLog("packet_event", logMsg)
	}
}

func CheckRules(ip string) string {
	for _, rule := range rules {
		if strings.HasPrefix(rule, "BLOCK:") && strings.Contains(rule, ip) {
			return "BLOCKED"
		}
		if strings.HasPrefix(rule, "ALLOW:") && strings.Contains(rule, ip) {
			return "ALLOWED"
		}
	}
	return "ALLOWED"
}

// Agent.go

package main

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"
)

func main() {
	fmt.Println("🚀 Starting Firewall Agent...")

	// Load rules from server (for now static)
	LoadRules()

	// Start packet monitor in goroutine
	go StartPacketMonitor("eth0") // change eth0 to your interface

	// Start enforcement engine
	go StartEnforcer()

	// Graceful shutdown on Ctrl+C
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	<-stop
	fmt.Println("\n🛑 Firewall Agent stopped")
}

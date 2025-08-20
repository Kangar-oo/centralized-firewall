// Agent.go
package main

import (
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"centralized-firewall/agent/api"
	"centralized-firewall/agent/config"
	"centralized-firewall/agent/enforcer"
	"centralized-firewall/agent/monitor"
	"centralized-firewall/agent/rules"
)

var (
	version = "dev"
)

func main() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)
	log.Println("🚀 Starting Firewall Agent v" + version)

	// Load configuration
	log.Println("Loading configuration...")
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("❌ Failed to load configuration: %v", err)
	}
	log.Printf("✅ Configuration loaded: %+v", cfg)

	// Initialize API client
	log.Println("Initializing API client...")
	apiClient := api.NewClient(cfg)

	// Authenticate with the server
	log.Println("Authenticating with server...")
	if err := apiClient.Login(cfg.AgentID, cfg.AgentSecret); err != nil {
		log.Fatalf("❌ Authentication failed: %v", err)
	}
	log.Println("✅ Successfully authenticated with the server")

	// Initialize rule manager
	log.Println("Initializing rule manager...")
	ruleManager := rules.NewRuleManager(apiClient)

	// Start rule synchronization in background
	log.Println("Starting rule synchronization...")
	go ruleManager.StartSync(30 * time.Second)

	// Start packet monitor
	log.Printf("Starting packet monitor on interface: %s...", cfg.Interface)
	packetChan, err := monitor.StartPacketMonitor(cfg.Interface)
	if err != nil {
		log.Fatalf("❌ Failed to start packet monitor: %v", err)
	}
	log.Println("✅ Packet monitor started successfully")

	// Start enforcer
	log.Println("Starting enforcer...")
	enf := enforcer.NewEnforcer(ruleManager, packetChan, apiClient)
	go enf.Start()
	log.Println("✅ Enforcer started successfully")

	// Wait for shutdown signal
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)

	// Block until we receive a signal
	sig := <-sigChan
	log.Printf("\n🛑 Received %v, shutting down...", sig)

	// Perform cleanup
	enf.Stop()

	log.Println("✅ Firewall Agent stopped gracefully")
}

// rules/manager.go

package rules

import (
	"log"
	"sync"
	"time"

	"centralized-firewall/agent/api"
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

// StartSync starts the rule synchronization process
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

// SyncRules fetches rules from the server and updates the local cache
func (rm *RuleManager) SyncRules() error {
	rules, err := rm.apiClient.GetRules()
	if err != nil {
		return err
	}

	rm.rulesLock.Lock()
	defer rm.rulesLock.Unlock()

	rm.rules = rules
	log.Printf("Synced %d rules from server", len(rules))
	return nil
}

// CheckPacket checks if a packet matches any rule and returns the action to take
func (rm *RuleManager) CheckPacket(packet interface{}) (bool, string) {
	// Default to allow if no rules match
	action := "ALLOW"

	rm.rulesLock.RLock()
	defer rm.rulesLock.RUnlock()

	for _, rule := range rm.rules {
		if !rule.IsActive {
			continue
		}

		// Check if packet matches rule
		if matchesRule(rule, packet) {
			action = rule.Action
			break
		}
	}

	return action == "ALLOW", action
}

// matchesRule checks if a packet matches a rule
func matchesRule(rule api.Rule, packet interface{}) bool {
	// TODO: Implement proper packet matching logic based on rule criteria
	// For now, we'll just log that we're using the parameters to avoid unused parameter warnings
	_ = packet // Use packet to avoid unused parameter warning
	_ = rule   // Use rule to avoid unused parameter warning
	
	// Default to allowing all packets until proper matching is implemented
	return true
}

// GetRules returns a copy of the current rules
func (rm *RuleManager) GetRules() []api.Rule {
	rm.rulesLock.RLock()
	defer rm.rulesLock.RUnlock()

	rulesCopy := make([]api.Rule, len(rm.rules))
	copy(rulesCopy, rm.rules)
	return rulesCopy
}

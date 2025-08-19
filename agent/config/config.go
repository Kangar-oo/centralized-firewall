package config

import (
	"fmt"
	"log"

	"github.com/caarlos0/env/v6"
)

type Config struct {
	ServerURL    string `env:"SERVER_URL" envDefault:"http://localhost:5000"`
	AgentID      string `env:"AGENT_ID" envDefault:""`
	AgentSecret  string `env:"AGENT_SECRET" envDefault:""`
	Interface    string `env:"NETWORK_INTERFACE" envDefault:"eth0"`
	LogLevel     string `env:"LOG_LEVEL" envDefault:"info"`
	SyncInterval int    `env:"SYNC_INTERVAL" envDefault:"60"`
}

func Load() (*Config, error) {
	cfg := &Config{}
	
	// Parse environment variables into the config struct
	if err := env.Parse(cfg); err != nil {
		return nil, fmt.Errorf("failed to parse environment variables: %w", err)
	}

	// Validate required fields
	if cfg.AgentID == "" || cfg.AgentSecret == "" {
		return nil, fmt.Errorf("AGENT_ID and AGENT_SECRET environment variables are required")
	}

	log.Printf("Loaded configuration: %+v", cfg)
	return cfg, nil
}

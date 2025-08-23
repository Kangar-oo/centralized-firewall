package config

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"

	"github.com/caarlos0/env/v6"
	"github.com/joho/godotenv"
)

type Config struct {
	ServerURL    string `env:"SERVER_URL" envDefault:"http://localhost:5000" json:"server_url"`
	AgentID      string `env:"AGENT_ID" json:"agent_id"`
	AgentSecret  string `env:"AGENT_SECRET" json:"agent_secret"`
	Interface    string `env:"NETWORK_INTERFACE" envDefault:"eth0" json:"interface"`
	LogLevel     string `env:"LOG_LEVEL" envDefault:"info" json:"log_level"`
	SyncInterval int    `env:"SYNC_INTERVAL" envDefault:"60" json:"sync_interval"`
}

// Load configuration in order of priority:
// 1. Environment variables (loaded from system + .env file)
// 2. config.json (fallback if some values are missing)
func Load() (*Config, error) {
	cfg := &Config{}

	// 1. Load .env file if present
	envPath := filepath.Join("agent", ".env")
	if err := godotenv.Load(envPath); err == nil {
		log.Printf("✅ Loaded environment variables from %s", envPath)
	} else {
		log.Printf("⚠️ No .env file found at %s (using system environment only)", envPath)
	}

	// 2. Parse env vars into struct
	if err := env.Parse(cfg); err != nil {
		return nil, fmt.Errorf("failed to parse environment variables: %w", err)
	}

	// 3. Load from config.json (optional, only if file exists)
	jsonPath := filepath.Join("agent", "config.json")
	if _, err := os.Stat(jsonPath); err == nil {
		file, err := os.Open(jsonPath)
		if err != nil {
			return nil, fmt.Errorf("failed to open config.json: %w", err)
		}
		defer file.Close()

		decoder := json.NewDecoder(file)
		fileCfg := &Config{}
		if err := decoder.Decode(fileCfg); err != nil {
			return nil, fmt.Errorf("failed to decode config.json: %w", err)
		}

		// Override only missing fields from JSON
		if cfg.AgentID == "" {
			cfg.AgentID = fileCfg.AgentID
		}
		if cfg.AgentSecret == "" {
			cfg.AgentSecret = fileCfg.AgentSecret
		}
		if cfg.ServerURL == "" {
			cfg.ServerURL = fileCfg.ServerURL
		}
		if cfg.Interface == "" {
			cfg.Interface = fileCfg.Interface
		}
		if cfg.LogLevel == "" {
			cfg.LogLevel = fileCfg.LogLevel
		}
		if cfg.SyncInterval == 0 {
			cfg.SyncInterval = fileCfg.SyncInterval
		}

		log.Printf("✅ Loaded additional configuration from %s", jsonPath)
	}

	// 4. Validate required fields
	if cfg.AgentID == "" || cfg.AgentSecret == "" {
		return nil, fmt.Errorf("AGENT_ID and AGENT_SECRET are required (set in .env, system env, or config.json)")
	}

	log.Printf("🔧 Final configuration: %+v", cfg)
	return cfg, nil
}

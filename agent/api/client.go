package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"centralized-firewall/agent/config"
)

type Client struct {
	baseURL    string
	httpClient *http.Client
	token      string
}

func NewClient(cfg *config.Config) *Client {
	return &Client{
		baseURL: cfg.ServerURL,
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

type LoginRequest struct {
	AgentID     string `json:"agent_id"`
	AgentSecret string `json:"agent_secret"`
}

type LoginResponse struct {
	AccessToken string `json:"access_token"`
}

type Rule struct {
	ID              int     `json:"id"`
	Name           string  `json:"name"`
	SourceIP       *string `json:"source_ip,omitempty"`
	SourcePort     *string `json:"source_port,omitempty"`
	DestinationIP  *string `json:"destination_ip,omitempty"`
	DestinationPort *string `json:"destination_port,omitempty"`
	Protocol       *string `json:"protocol,omitempty"`
	Action         string  `json:"action"`
	IsActive       bool    `json:"is_active"`
}

func (c *Client) Login(agentID, agentSecret string) error {
	loginReq := LoginRequest{
		AgentID:     agentID,
		AgentSecret: agentSecret,
	}

	var loginResp LoginResponse
	err := c.doRequest("POST", "/api/v1/agent/login", loginReq, &loginResp)
	if err != nil {
		return fmt.Errorf("login failed: %w", err)
	}

	c.token = loginResp.AccessToken
	return nil
}

func (c *Client) GetRules() ([]Rule, error) {
	var rules []Rule
	err := c.doRequest("GET", "/api/v1/rules", nil, &rules)
	if err != nil {
		return nil, fmt.Errorf("failed to get rules: %w", err)
	}

	return rules, nil
}

func (c *Client) SendLog(eventType, message string, metadata map[string]interface{}) error {
	logEntry := map[string]interface{}{
		"event_type": eventType,
		"message":    message,
		"metadata":   metadata,
	}

	return c.doRequest("POST", "/api/v1/logs", logEntry, nil)
}

func (c *Client) doRequest(method, path string, body interface{}, result interface{}) error {
	var bodyReader io.Reader
	if body != nil {
		jsonData, err := json.Marshal(body)
		if err != nil {
			return fmt.Errorf("failed to marshal request body: %w", err)
		}
		bodyReader = bytes.NewReader(jsonData)
	}

	req, err := http.NewRequest(method, c.baseURL+path, bodyReader)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	if c.token != "" {
		req.Header.Set("Authorization", "Bearer "+c.token)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("request failed with status %d: %s", resp.StatusCode, string(body))
	}

	if result != nil {
		if err := json.NewDecoder(resp.Body).Decode(result); err != nil {
			return fmt.Errorf("failed to decode response: %w", err)
		}
	}

	return nil
}

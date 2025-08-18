// Logger.go

package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type LogEntry struct {
	Event   string `json:"event"`
	Details string `json:"details"`
	Time    string `json:"time"`
}

func SendLog(event, details string) {
	logData := LogEntry{
		Event:   event,
		Details: details,
		Time:    Now(),
	}

	jsonData, _ := json.Marshal(logData)
	resp, err := http.Post("http://localhost:5000/logs", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		fmt.Println("❌ Error sending log:", err)
		return
	}
	defer resp.Body.Close()

	fmt.Println("✅ Log sent to server:", event)
}

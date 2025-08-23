// list_iface.go

package main

import (
    "fmt"
    "github.com/google/gopacket/pcap"
)

func main() {
    devices, err := pcap.FindAllDevs()
    if err != nil {
        panic(err)
    }

    fmt.Println("Available interfaces:")
    for _, dev := range devices {
        fmt.Printf("- Name: %s\n  Description: %s\n", dev.Name, dev.Description)
    }
}

Write-Output "Testing Go installation..."

go version

Write-Output "`nEnvironment Variables:"
Get-ChildItem Env: | Where-Object { $_.Name -like "GO*" -or $_.Name -eq "PATH" } | Format-Table -AutoSize

Write-Output "`nGo environment:"
& go env

Write-Output "`nTrying to run a simple Go program..."
@'
package main

import "fmt"

func main() {
    fmt.Println("Go installation test successful!")
}
'@ | Out-File -FilePath "test_go.go" -Encoding ascii

go run test_go.go

#!/bin/bash
echo "=== System Information ==="
uname -a
echo
echo "=== Chrome Installation ==="
which chromium
chromium --version
echo
echo "=== ChromeDriver Installation ==="
which chromedriver
chromedriver --version
echo
echo "=== Process Information ==="
ps aux | grep chrome
echo
echo "=== Network Information ==="
netstat -tulpn
echo
echo "=== Chrome Logs ==="
cat /app/chromedriver.log

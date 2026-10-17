#!/bin/bash

# Script to set up hugepages for DPDK

echo "Setting up hugepages for DPDK..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root"
    echo "Please run: sudo $0"
    exit 1
fi

# Set up 2MB hugepages (default ~1GB total = 512 pages)
HUGEPAGE_COUNT=512

echo "Setting up $HUGEPAGE_COUNT hugepages of 2MB each..."

# Configure hugepages in kernel
echo $HUGEPAGE_COUNT > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages

# Set proper permissions for /dev/hugepages (primary DPDK location)
chmod 755 /dev/hugepages 2>/dev/null || true
chown $SUDO_USER:$SUDO_USER /dev/hugepages 2>/dev/null || true

# Also mount and configure /mnt/huge as alternative location
if ! mountpoint -q /mnt/huge; then
    mkdir -p /mnt/huge
    mount -t hugetlbfs nodev /mnt/huge
    echo "Mounted hugepage filesystem at /mnt/huge"
fi

chmod -R 755 /mnt/huge
chown -R $SUDO_USER:$SUDO_USER /mnt/huge 2>/dev/null || true

# Verify hugepage setup
ACTUAL_PAGES=$(cat /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages)
FREE_PAGES=$(cat /sys/kernel/mm/hugepages/hugepages-2048kB/free_hugepages)

echo "Hugepage setup complete:"
echo "  Allocated: $ACTUAL_PAGES pages"
echo "  Free: $FREE_PAGES pages"
echo "  Total memory: $((ACTUAL_PAGES * 2))MB"

if [ "$ACTUAL_PAGES" -ge "$HUGEPAGE_COUNT" ]; then
    echo "Hugepages configured successfully"
    
    # Show current network interfaces for reference
    echo ""
    echo "Available network interfaces:"
    ip link show | grep -E "^[0-9]+:" | awk -F': ' '{print "  " $2}' | sed 's/@.*//'
    
    echo ""
    echo "DPDK setup complete! You can now run the DPDK tokenizer."
    echo "Hugepages available at:"
    echo "  Primary: /dev/hugepages (default DPDK location)"
    echo "  Alternative: /mnt/huge"
    echo ""
    echo "If you get permission errors, run:"
    echo "  sudo chmod 755 /dev/hugepages"
    echo "  sudo chmod -R 755 /mnt/huge"
    echo "  sudo chown -R \$USER:\$USER /dev/hugepages /mnt/huge"
else
    echo "Failed to allocate sufficient hugepages"
    echo "You may need to:"
    echo "  1. Free up memory"
    echo "  2. Increase vm.nr_hugepages in /etc/sysctl.conf"
    echo "  3. Reboot and try again"
    exit 1
fi

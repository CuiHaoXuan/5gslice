#! /bin/bash

#make config T=x86_64-native-linuxapp-gcc
#make

echo "Hugepage configure"
#remove_mnt_huge
mkdir -p /mnt/huge
mount -t hugetlbfs nodev /mnt/huge
echo 256 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages

echo "Loading uio module"
sudo /sbin/modprobe uio

echo "Loading DPDK uio module"
sudo /sbin/insmod igb_uio.ko

sudo ./dpdk_nic_bind.py --status
ifconfig eth2 down
ifconfig eth5 down
sudo ./dpdk_nic_bind.py --b igb_uio 10:00.0 && echo "ok"
sudo ./dpdk_nic_bind.py --b igb_uio 10:00.1 && echo "ok"

sudo ./dpdk_nic_bind.py --status

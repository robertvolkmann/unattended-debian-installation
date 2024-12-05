# Unattended Debian Installation

This repository contains everything to create a custom Debian minimal ISO for an unattended installation so that the
resulting machine joins automatically an underlay via unnumbered BGP. Check `profiles/custom.postinst` for networking details.

## Test lab

Build the image `localhost/machine` and wait several minutes:
```shell
$ docker build -t localhost/machine .
```

Start the test lab with:
```shell
$ sudo containerlab deploy
+---+--------------------+--------------+------------------------------+-------+---------+--------------+--------------+
| # |        Name        | Container ID |            Image             | Kind  |  State  | IPv4 Address | IPv6 Address |
+---+--------------------+--------------+------------------------------+-------+---------+--------------+--------------+
| 1 | clab-test-frr      | 80ed273b49d3 | quay.io/frrouting/frr:10.1.1 | linux | running | N/A          | N/A          |
| 2 | clab-test-machine  | 167a9275fb18 | localhost/machine            | linux | running | N/A          | N/A          |
| 3 | clab-test-netshoot | bff8c3252054 | docker.io/nicolaka/netshoot  | linux | running | N/A          | N/A          |
+---+--------------------+--------------+------------------------------+-------+---------+--------------+--------------+
```

To see the installation log and to access the machine use:
```shell
$ docker exec -it clab-test-machine telnet 127.0.0.1 9000
Trying 127.0.0.1...
Connected to 127.0.0.1.
Escape character is '^]'.
error: no suitable video mode found.
Booting in blind mode
Starting system log daemon: syslogd, klogd.
Detecting hardware to find installation media  ... 2%... 95%... 100%
Scanning installation media  ... 2%... 11%... 21%... 30%... 40%... 50%... 61%... 71%... 80%... 90%... 100%
Loading additional components  ... 0%... 10%... 20%... 30%... 40%... 50%... 60%... 70%... 80%... 90%... 100%
Detecting network hardware  ... 2%... 95%... 100%
Setting up the clock  ... 0%
Detecting disks and all other hardware  ... 2%... 95%... 100%
Loading additional components  ... 12%... 25%... 37%... 50%... 62%... 75%... 87%... 100%
Loading additional components  ... 25%... 50%... 75%... 100%
Starting up the partitioner  ... 4%... 13%... 21%... 30%... 43%... 52%... 60%... 73%... 82%... 91%... 100%
Guided partitioning  ... 20%... 40%... 60%... 80%... 100%
Starting up the partitioner  ... 4%... 13%... 21%... 30%... 43%... 52%... 60%... 73%... 82%... 91%... 100%
Partitions formatting  ... 33%
Partitions formatting  
Partitions formatting  
Partitions formatting  
Installing the base system  ... 0%... 17%... 20%... 30%... 40%... 50%... 60%... 70%... 79%... 83%... 91%... 100%
Configuring apt  ... 5%... 11%... 22%... 27%... 33%... 38%... 44%... 50%... 61%... 72%... 83%... 94%... 100%
Select and install software  ... 1%... 10%... 13%... 22%... 30%... 40%... 50%... 60%... 70%... 80%... 90%... 100%
Installing GRUB boot loader  ... 16%... 33%... 50%... 66%... 83%... 100%
The system is going down NOW!.. 3%... 10%... 20%... 30%... 36%... 40%... 50%... 53%... 60%... 70%... 80%... 90%
Sent SIGTERM to all processes
Sent SIGKILL to all processes
Requesting system reboot
[  127.608710] reboot: Restarting system
```

The user `root` has the password `insecure`.

To verify the BGP sessions:
```shell
$ docker exec -it clab-test-frr vtysh -c "show bgp summary"
IPv4 Unicast Summary:
BGP router identifier 10.0.0.1, local AS number 4200000001 VRF default vrf-id 0
BGP table version 2
RIB entries 3, using 384 bytes of memory
Peers 1, using 17 KiB of memory
Peer groups 1, using 64 bytes of memory

Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt Desc
machine(eth0)   4 4200000002       643       643        2    0    0 00:10:39            1        2 FRRouting/10.0.2

Total number of neighbors 1
```

To access the machine via SSH use:
```shell
$ docker exec -it clab-test-netshoot ssh ansible@10.0.0.2
```

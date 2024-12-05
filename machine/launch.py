#!/usr/bin/python3
import logging
import os
import signal
import subprocess
import sys
import time

BASE_ISO = "/debian.iso"


class Qemu:
    def __init__(self, name: str, smp: str, memory: str, interfaces: int):
        self._name = name
        self._smp = smp
        self._memory = memory
        self._interfaces = interfaces
        self._p = None
        self._disk = "/overlay.img"

    def create_disk(self) -> None:
        cmd = [
            "qemu-img",
            "create",
            "-f", "qcow2",
            self._disk,
            "10G"
        ]
        subprocess.run(cmd, check=True)

    def start(self) -> None:
        cmd = [
            "qemu-system-x86_64",
            "-cpu", "host",
            "-smp", self._smp,
            "-display", "none",
            "-enable-kvm",
            "-nodefaults",
            "-machine", "q35",
            "-name", self._name,
            "-m", self._memory,
            "-cdrom", BASE_ISO,
            "-drive", "if=pflash,format=raw,readonly=on,file=/opt/OVMF/OVMF_CODE.fd",
            "-drive", "if=pflash,format=raw,file=/opt/OVMF/OVMF_VARS.fd",
            "-drive", f"id=disk,if=none,format=qcow2,file={self._disk}",
            "-device", f"virtio-blk-pci,drive=disk,bootindex=0",
            "-serial", "telnet:127.0.0.1:9000,server,nowait",
        ]

        for i in range(self._interfaces):
            with open(f"/sys/class/net/eth{i}/address", "r") as f:
                mac = f.read().strip()
            cmd.append("-device")
            cmd.append(f"virtio-net-pci,netdev=hn{i},mac={mac},romfile=")
            cmd.append(f"-netdev")
            cmd.append(f"tap,id=hn{i},ifname=tap{i},script=/mirror_tap_to_eth.sh,downscript=no")

        self._p = subprocess.Popen(cmd)

    def wait(self) -> None:
        self._p.wait()


def main():
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logger = logging.getLogger()

    name = os.getenv("CLAB_LABEL_CLAB_NODE_NAME", default="switch")
    smp = os.getenv("QEMU_SMP", default="2")
    memory = os.getenv("QEMU_MEMORY", default="4096")
    interfaces = int(os.getenv("CLAB_INTFS", 0))

    vm = Qemu(name, smp, memory, interfaces)

    logger.info("Create disk")
    vm.create_disk()

    logger.info(f'Waiting for {interfaces} interfaces to be connected')
    wait_until_all_interfaces_are_connected(interfaces)

    logger.info("Start QEMU")
    vm.start()

    logger.info("Wait until QEMU is terminated")
    vm.wait()


def handle_exit(signal, frame):
    sys.exit(0)


def wait_until_all_interfaces_are_connected(interfaces: int) -> None:
    while True:
        i = 0
        for iface in os.listdir('/sys/class/net/'):
            if iface.startswith('eth'):
                i += 1
        if i == interfaces:
            break
        time.sleep(1)


if __name__ == "__main__":
    main()

FROM docker.io/debian:bookworm AS build-iso

RUN apt-get update && \
    apt-get install --yes simple-cdd

RUN mkdir -p /home/nobody

COPY frr.list /etc/apt/sources.list.d/frr.list
COPY frr.asc /tmp/frr.asc

RUN gpg --dearmor --yes --output /etc/apt/keyrings/frr.gpg /tmp/frr.asc

RUN apt-get update && \
    apt-get --download-only --option dir::cache=/home/nobody install --yes frr

RUN chown -R nobody:nogroup /home/nobody

ENV HOME=/home/nobody
WORKDIR /home/nobody
USER nobody

RUN build-simple-cdd --mirror-only --verbose

COPY --chown=nobody:nogroup simple-cdd.conf /home/nobody/
COPY --chown=nobody:nogroup profiles /home/nobody/profiles/

RUN chown -R nobody:nogroup /home/nobody

RUN build-simple-cdd --conf simple-cdd.conf --verbose

FROM docker.io/library/debian:bookworm-backports

RUN apt-get update && \
    apt-get --no-install-recommends install --yes \
        iproute2 \
        procps \
        python3 \
        qemu-utils \
        qemu-system-x86 \
        telnet

COPY --from=ghcr.io/metal-stack/mini-lab-ovmf:edk2-stable202408.01 /OVMF_*.fd /opt/OVMF/

COPY --from=build-iso /home/nobody/images/debian-12-amd64-CD-1.iso /debian.iso

COPY machine/ /

ENTRYPOINT ["/launch.py"]

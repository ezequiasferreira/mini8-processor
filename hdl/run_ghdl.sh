#!/bin/sh
set -eu
cd "$(dirname "$0")"
command -v ghdl >/dev/null 2>&1 || { echo "GHDL is required" >&2; exit 127; }
mkdir -p build results
ghdl -a --std=08 --workdir=build src/mini8_pkg.vhd src/mini8_core.vhd src/mini8_soc.vhd tests/tb_mini8.vhd
ghdl -e --std=08 --workdir=build tb_mini8
ghdl -r --std=08 --workdir=build tb_mini8 --assert-level=error --stop-time=500ns --vcd=results/mini8.vcd

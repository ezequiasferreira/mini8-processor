#!/usr/bin/env python3
"""Mini-8 ISA assembler and functional CPU simulator (Python 3.10+).

One step models one enabled clock edge. Not binary compatible with MIPS.
"""
from __future__ import annotations
import argparse
import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

OPS = {"ADD": 0, "LD": 1, "ST": 2, "BEQZ": 3}
IDLE = 0xC7  # BEQZ R0, -1: self-branch, not a hardware HALT


def signed3(x: int) -> int:
    x &= 7
    return x - 8 if x & 4 else x


def encode(op: str, a: int, b: int) -> int:
    op = op.upper()
    if op not in OPS or not 0 <= a <= 7:
        raise ValueError("Invalid instruction or A register")
    if op == "BEQZ":
        if not -4 <= b <= 3:
            raise ValueError("Branch offset must be -4..+3")
    elif not 0 <= b <= 7:
        raise ValueError("B register must be R0..R7")
    return (OPS[op] << 6) | (a << 3) | (b & 7)


def disassemble(byte: int) -> str:
    op, a, b = (byte >> 6) & 3, (byte >> 3) & 7, byte & 7
    return (
        f"ADD R{b},R{a}" if op == 0 else
        f"LD R{b},[R{a}]" if op == 1 else
        f"ST R{b},[R{a}]" if op == 2 else
        f"BEQZ R{a},{signed3(b):+d}"
    )


def assemble(source: str) -> list[int]:
    labels = {}
    lines = []
    for line_no, raw in enumerate(source.splitlines(), 1):
        line = raw.split(";", 1)[0].strip()
        if not line:
            continue
        if ":" in line:
            name, line = line.split(":", 1)
            name = name.strip()
            if not re.fullmatch(r"[A-Za-z_]\w*", name) or name in labels:
                raise ValueError(f"Line {line_no}: invalid or duplicate label")
            labels[name] = len(lines)
            line = line.strip()
        if line:
            lines.append((line_no, line))
    if len(lines) > 256:
        raise ValueError("Program exceeds 256 bytes")
    code = []
    for pc, (line_no, line) in enumerate(lines):
        try:
            if m := re.fullmatch(r"ADD\s+R([0-7])\s*,\s*R([0-7])", line, re.I):
                code.append(encode("ADD", int(m[2]), int(m[1])))
            elif m := re.fullmatch(r"(LD|ST)\s+R([0-7])\s*,\s*\[\s*R([0-7])\s*\]", line, re.I):
                code.append(encode(m[1], int(m[3]), int(m[2])))
            elif m := re.fullmatch(r"BEQZ\s+R([0-7])\s*,\s*([+-]?\d+|[A-Za-z_]\w*)", line, re.I):
                offset = m[2]
                if re.fullmatch(r"[+-]?\d+", offset):
                    delta = int(offset)
                else:
                    if offset not in labels:
                        raise ValueError("Unknown branch label")
                    delta = (labels[offset] - (pc + 1)) & 255
                    if delta >= 128:
                        delta -= 256
                code.append(encode("BEQZ", int(m[1]), delta))
            else:
                raise ValueError("Invalid assembly syntax")
        except ValueError as exc:
            raise ValueError(f"Line {line_no}: {exc}") from exc
    return code


@dataclass
class CPU:
    rom: list[int] = field(default_factory=lambda: [IDLE] * 256)
    ram: list[int] = field(default_factory=lambda: [0] * 256)
    regs: list[int] = field(default_factory=lambda: [0] * 8)
    pc: int = 0
    cycles: int = 0

    def __post_init__(self):
        if len(self.rom) != 256 or len(self.ram) != 256 or len(self.regs) != 8:
            raise ValueError("Expected 256 ROM bytes, 256 RAM bytes, 8 registers")
        if any(not isinstance(n, int) or not 0 <= n <= 255 for n in self.rom + self.ram + self.regs):
            raise ValueError("State values must be unsigned 8-bit")
        self.pc &= 255
        self.regs[0] = 0

    @classmethod
    def from_program(cls, program: list[int], data: dict[int, int] | None = None) -> "CPU":
        if len(program) > 256:
            raise ValueError("Program too large")
        cpu = cls(rom=program + [IDLE] * (256 - len(program)))
        for address, value in (data or {}).items():
            if not 0 <= address <= 255 or not 0 <= value <= 255:
                raise ValueError("Invalid memory initialization")
            cpu.ram[address] = value
        return cpu

    def reset(self):
        self.pc = 0
        self.cycles = 0
        self.regs = [0] * 8  # RAM remains unchanged

    def step(self, enable: bool = True) -> dict:
        pc = self.pc
        word = self.rom[pc]
        op, a, b = word >> 6, (word >> 3) & 7, word & 7
        ra, rb = self.regs[a], self.regs[b]
        bzero = int(op != 0)
        alu = (ra + (0 if bzero else rb)) & 255
        zero = int(alu == 0)
        branch = int(op == 3)
        pcsrc = branch & zero
        next_pc = ((pc + 1 + signed3(b)) if pcsrc else (pc + 1)) & 255
        event = dict(cycle=self.cycles + int(enable), pc=pc, hex=f"{word:02X}",
                     bits=f"{word:08b}", instruction=disassemble(word), A=a, B=b,
                     RA=ra, RB=rb, BZero=bzero, ALU=alu, Zero=zero,
                     DvC=branch, FontePC=pcsrc, LerMem=int(op == 1),
                     EscMem=int(op == 2), EscReg=int(op in (0, 1)),
                     MemParaReg=int(op == 1), next_pc=next_pc if enable else pc)
        if enable:
            if op in (0, 1):
                if b:
                    self.regs[b] = self.ram[alu] if op == 1 else alu
                    effect = f"R{b} <- {self.regs[b]}"
                else:
                    effect = "R0 write discarded"
            elif op == 2:
                self.ram[alu] = rb
                effect = f"RAM[{alu}] <- {rb}"
            else:
                effect = "branch taken" if pcsrc else "branch not taken"
            self.pc = next_pc
            self.cycles += 1
        else:
            effect = "paused"
        self.regs[0] = 0
        event["effect"] = effect
        for i, value in enumerate(self.regs):
            event[f"R{i}"] = value
        return event


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("program", type=Path)
    parser.add_argument("--data", type=Path)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--hex", type=Path)
    args = parser.parse_args()
    if args.steps < 1:
        parser.error("--steps must be positive")
    raw = json.loads(args.data.read_text(encoding="utf-8")) if args.data else {}
    cpu = CPU.from_program(assemble(args.program.read_text(encoding="utf-8")),
                           {int(k): int(v) for k, v in raw.items()})
    if args.hex:
        args.hex.write_text("\n".join(f"{x:02X}" for x in cpu.rom) + "\n", encoding="ascii")
    rows = [cpu.step() for _ in range(args.steps)]
    for row in rows:
        print(f'{row["cycle"]:>3} PC={row["pc"]:03} {row["hex"]} '
              f'{row["instruction"]:<20} {row["effect"]}')
    print("Registers:", cpu.regs)
    print("Nonzero RAM:", {i: v for i, v in enumerate(cpu.ram) if v})
    if args.csv:
        with args.csv.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


if __name__ == "__main__":
    main()

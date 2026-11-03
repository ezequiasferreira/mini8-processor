"""Mini-8 functional verification; not RTL or FPGA validation."""
import random
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mini8 import CPU, IDLE, assemble, disassemble, encode, signed3

ROOT = Path(__file__).resolve().parents[1]


class TestMini8(unittest.TestCase):
    def test_add_encoding(self):
        self.assertEqual(assemble("ADD R5,R2"), [0x15])

    def test_all_encodings_roundtrip(self):
        for word in range(256):
            self.assertEqual(assemble(disassemble(word)), [word])

    def test_signed3(self):
        self.assertEqual([signed3(i) for i in range(8)], [0, 1, 2, 3, -4, -3, -2, -1])

    def test_all_add_operand_pairs(self):
        cpu = CPU()
        cpu.rom = [encode("ADD", 1, 2)] * 256
        for a in range(256):
            for b in range(256):
                cpu.regs[1], cpu.regs[2] = a, b
                cpu.step()
                self.assertEqual(cpu.regs[2], (a + b) % 256)

    def test_all_ram_addresses_and_values(self):
        cpu = CPU()
        for address in range(256):
            for value in range(256):
                cpu.pc = 0
                cpu.rom[:2] = [encode("ST", 1, 2), encode("LD", 1, 3)]
                cpu.regs[1], cpu.regs[2] = address, value
                cpu.step()
                cpu.step()
                self.assertEqual((cpu.ram[address], cpu.regs[3]), (value, value))

    def test_all_branch_pc_offsets(self):
        cpu = CPU()
        for pc in range(256):
            for offset in range(-4, 4):
                for value in (0, 1, 128, 255):
                    cpu.pc, cpu.regs[1] = pc, value
                    cpu.rom[pc] = encode("BEQZ", 1, offset)
                    row = cpu.step()
                    self.assertEqual(cpu.pc, (pc + 1 + (offset if value == 0 else 0)) & 255)
                    self.assertEqual(row["FontePC"], int(value == 0))

    def test_zero_does_not_branch_for_add(self):
        cpu = CPU.from_program([encode("ADD", 0, 1)])
        row = cpu.step()
        self.assertEqual((row["Zero"], row["DvC"], cpu.pc), (1, 0, 1))

    def test_r0_readonly(self):
        cpu = CPU.from_program([encode("LD", 0, 0), encode("ADD", 1, 0)], {0: 123})
        cpu.regs[1] = 9
        cpu.step(); cpu.step()
        self.assertEqual(cpu.regs[0], 0)

    def test_same_source_destination_add(self):
        cpu = CPU.from_program([encode("ADD", 2, 2)])
        cpu.regs[2] = 127
        cpu.step()
        self.assertEqual(cpu.regs[2], 254)

    def test_load_same_register(self):
        cpu = CPU.from_program([encode("LD", 2, 2)], {5: 99})
        cpu.regs[2] = 5
        cpu.step()
        self.assertEqual(cpu.regs[2], 99)

    def test_store_same_register(self):
        cpu = CPU.from_program([encode("ST", 2, 2)])
        cpu.regs[2] = 37
        cpu.step()
        self.assertEqual(cpu.ram[37], 37)

    def test_pause_does_not_store(self):
        cpu = CPU.from_program([encode("ST", 1, 2)])
        cpu.regs[1], cpu.regs[2] = 10, 77
        cpu.step(enable=False)
        self.assertEqual((cpu.pc, cpu.ram[10], cpu.cycles), (0, 0, 0))
        cpu.step()
        self.assertEqual(cpu.ram[10], 77)

    def test_reset_preserves_ram(self):
        cpu = CPU.from_program([0], {5: 33})
        cpu.pc, cpu.regs[2] = 200, 44
        cpu.reset()
        self.assertEqual((cpu.pc, cpu.regs, cpu.ram[5]), (0, [0] * 8, 33))

    def test_idle_is_branch_not_halt(self):
        cpu = CPU.from_program([IDLE])
        for _ in range(8): cpu.step()
        self.assertEqual((cpu.pc, cpu.cycles), (0, 8))

    def test_sum_program(self):
        cpu = CPU.from_program(assemble((ROOT/"examples/soma.asm").read_text()), {0:2, 2:3})
        for _ in range(7): cpu.step()
        self.assertEqual(cpu.regs, [0, 2, 2, 3, 5, 0, 0, 0])
        self.assertEqual((cpu.ram[2], cpu.pc), (5, 6))

    def test_loop_program(self):
        cpu = CPU.from_program(assemble((ROOT/"examples/laco.asm").read_text()), {0:1, 1:3, 3:255})
        rows = [cpu.step() for _ in range(18)]
        self.assertEqual((cpu.regs[4], cpu.regs[2], cpu.ram[1], cpu.pc), (6, 0, 6, 8))
        branches = [r["FontePC"] for r in rows if r["DvC"]]
        self.assertIn(0, branches)
        self.assertIn(1, branches)

    def test_pc_wrap(self):
        cpu = CPU()
        cpu.pc, cpu.rom[255] = 255, encode("ADD", 0, 0)
        cpu.step()
        self.assertEqual(cpu.pc, 0)

    def test_assembler_rejects_invalid(self):
        for source in ["ADD R8,R0", "BEQZ R1,4", "BEQZ R1,-5", "LD R1,8(R2)",
                       "HALT", "BEQZ R0,missing", "x: ADD R1,R0\nx: ADD R1,R0"]:
            with self.assertRaises(ValueError):
                assemble(source)

    def test_all_opcodes_against_reference(self):
        rng = random.Random(3112026)
        for word in range(256):
            for _ in range(32):
                regs = [0] + [rng.randrange(256) for _ in range(7)]
                ram = [rng.randrange(256) for _ in range(256)]
                pc = rng.randrange(256)
                cpu = CPU(regs=regs.copy(), ram=ram.copy(), pc=pc)
                cpu.rom[pc] = word
                er, em = regs.copy(), ram.copy()
                op, a, b = word >> 6, (word >> 3) & 7, word & 7
                nxt = (pc + 1) & 255
                if op == 0 and b: er[b] = (regs[b] + regs[a]) & 255
                if op == 1 and b: er[b] = ram[regs[a]]
                if op == 2: em[regs[a]] = regs[b]
                if op == 3 and regs[a] == 0: nxt = (nxt + signed3(b)) & 255
                cpu.step()
                self.assertEqual((cpu.regs, cpu.ram, cpu.pc), (er, em, nxt))


if __name__ == "__main__":
    unittest.main(verbosity=2)

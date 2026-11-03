-- Draft testbench; run with GHDL VHDL-2008.
-- 10 ns is a stimulus period, not a measured maximum frequency.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.env.all;
use work.mini8_pkg.all;

entity tb_mini8 is end entity;
architecture sim of tb_mini8 is
  signal clk : std_logic := '0';
  signal reset : std_logic := '1';
  signal enable : std_logic := '0';
  signal sum_pc, loop_pc, sum_mem, loop_mem : byte_t;
  signal sum_regs, loop_regs : std_logic_vector(63 downto 0);
  signal z1,b1,p1,z2,b2,p2 : std_logic;
begin
  clk <= not clk after 5 ns;
  sum_dut: entity work.mini8_soc
    generic map (ROM_INIT => SUM_ROM, RAM_INIT => SUM_RAM)
    port map (clk, reset, enable, sum_pc, sum_regs, x"02", sum_mem, z1,b1,p1);
  loop_dut: entity work.mini8_soc
    generic map (ROM_INIT => LOOP_ROM, RAM_INIT => LOOP_RAM)
    port map (clk, reset, enable, loop_pc, loop_regs, x"01", loop_mem, z2,b2,p2);
  stimulus: process
  begin
    wait until rising_edge(clk); wait for 1 ns;
    assert sum_pc = x"00" and loop_pc = x"00" severity failure;
    wait until falling_edge(clk);
    reset <= '0'; enable <= '1';
    for i in 1 to 18 loop
      wait until rising_edge(clk); wait for 1 ns;
      assert sum_regs(7 downto 0) = x"00" severity failure;
      assert loop_regs(7 downto 0) = x"00" severity failure;
      if i = 6 then
        assert sum_regs(39 downto 32) = x"05" severity failure;
        assert sum_mem = x"05" and sum_pc = x"06" severity failure;
      end if;
    end loop;
    assert loop_regs(39 downto 32) = x"06" severity failure;
    assert loop_regs(23 downto 16) = x"00" severity failure;
    assert loop_mem = x"06" and loop_pc = x"08" severity failure;
    assert sum_pc = x"06" severity failure;
    wait until falling_edge(clk); enable <= '0';
    wait until rising_edge(clk); wait for 1 ns;
    assert loop_pc = x"08" and loop_mem = x"06" severity failure;
    wait until falling_edge(clk); reset <= '1';
    wait until rising_edge(clk); wait for 1 ns;
    assert sum_pc = x"00" and loop_pc = x"00" severity failure;
    assert sum_regs = x"0000000000000000" severity failure;
    assert loop_regs = x"0000000000000000" severity failure;
    assert sum_mem = x"05" and loop_mem = x"06" severity failure;
    report "Mini-8 RTL testbench: PASS" severity note;
    stop;
    wait;
  end process;
end architecture;

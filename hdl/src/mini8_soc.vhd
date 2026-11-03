-- Integration wrapper; synchronous RAM writes and asynchronous reads.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.mini8_pkg.all;

entity mini8_soc is
  generic (ROM_INIT : memory_t := SUM_ROM; RAM_INIT : memory_t := SUM_RAM);
  port (
    clk, reset, enable : in std_logic;
    dbg_pc : out byte_t;
    dbg_regs : out std_logic_vector(63 downto 0);
    dbg_mem_addr : in byte_t;
    dbg_mem_data : out byte_t;
    dbg_zero, dbg_dvc, dbg_fontepc : out std_logic
  );
end entity;

architecture rtl of mini8_soc is
  constant rom : memory_t := ROM_INIT;
  signal ram : memory_t := RAM_INIT;
  signal iaddr, idata, daddr, dwdata, drdata : byte_t := (others => '0');
  signal rd, wr : std_logic := '0';
begin
  idata <= rom(to_integer(unsigned(iaddr)));
  drdata <= ram(to_integer(unsigned(daddr))) when rd = '1' else (others => '0');
  process(clk)
  begin
    if rising_edge(clk) then
      if wr = '1' then ram(to_integer(unsigned(daddr))) <= dwdata; end if;
    end if;
  end process;
  cpu: entity work.mini8_core
    port map (
      clk => clk, reset => reset, enable => enable,
      imem_addr => iaddr, imem_data => idata,
      dmem_addr => daddr, dmem_wdata => dwdata, dmem_rdata => drdata,
      dmem_read => rd, dmem_write => wr, dbg_regs => dbg_regs,
      dbg_zero => dbg_zero, dbg_dvc => dbg_dvc, dbg_fontepc => dbg_fontepc);
  dbg_pc <= iaddr;
  dbg_mem_data <= ram(to_integer(unsigned(dbg_mem_addr)));
end architecture;

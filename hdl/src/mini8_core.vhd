-- Mini-8 VHDL-2008 draft. RTL simulation has not been verified.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.mini8_pkg.all;

entity mini8_core is
  port (
    clk, reset, enable : in std_logic;
    imem_addr : out byte_t;
    imem_data : in byte_t;
    dmem_addr, dmem_wdata : out byte_t;
    dmem_rdata : in byte_t;
    dmem_read, dmem_write : out std_logic;
    dbg_regs : out std_logic_vector(63 downto 0);
    dbg_zero, dbg_dvc, dbg_fontepc : out std_logic
  );
end entity;

architecture rtl of mini8_core is
  type regs_t is array (0 to 7) of unsigned(7 downto 0);
  signal regs : regs_t := (others => (others => '0'));
  signal pc : unsigned(7 downto 0) := (others => '0');
  signal opcode : std_logic_vector(1 downto 0);
  signal idx_a, idx_b : integer range 0 to 7;
  signal ra, rb, alu_b, alu_result, writeback : unsigned(7 downto 0);
  signal pc_seq, pc_target, pc_next : unsigned(7 downto 0);
  signal imm : signed(7 downto 0);
  signal bzero, regwrite, memread, memwrite, memtoreg, dvc : std_logic;
  signal zero_flag, pcsrc : std_logic;
begin
  imem_addr <= std_logic_vector(pc);
  opcode <= imem_data(7 downto 6);
  idx_a <= to_integer(unsigned(imem_data(5 downto 3)));
  idx_b <= to_integer(unsigned(imem_data(2 downto 0)));
  ra <= regs(idx_a);
  rb <= regs(idx_b);
  process(all)
  begin
    bzero <= '1'; regwrite <= '0'; memread <= '0';
    memwrite <= '0'; memtoreg <= '0'; dvc <= '0';
    case opcode is
      when "00" => bzero <= '0'; regwrite <= '1';
      when "01" => regwrite <= '1'; memread <= '1'; memtoreg <= '1';
      when "10" => memwrite <= '1';
      when "11" => dvc <= '1';
      when others => null;
    end case;
  end process;
  alu_b <= (others => '0') when bzero = '1' else rb;
  alu_result <= ra + alu_b;
  zero_flag <= '1' when alu_result = to_unsigned(0, 8) else '0';
  writeback <= unsigned(dmem_rdata) when memtoreg = '1' else alu_result;
  dmem_addr <= std_logic_vector(alu_result);
  dmem_wdata <= std_logic_vector(rb);
  dmem_read <= memread and enable and not reset;
  dmem_write <= memwrite and enable and not reset;
  pc_seq <= pc + to_unsigned(1, 8);
  imm <= resize(signed(imem_data(2 downto 0)), 8);
  pc_target <= unsigned(signed(pc_seq) + imm);
  pcsrc <= dvc and zero_flag;
  pc_next <= pc_target when pcsrc = '1' else pc_seq;
  process(clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        pc <= (others => '0');
        regs <= (others => (others => '0'));
      elsif enable = '1' then
        pc <= pc_next;
        if regwrite = '1' and idx_b /= 0 then
          regs(idx_b) <= writeback;
        end if;
        regs(0) <= (others => '0');
      end if;
    end if;
  end process;
  reg_debug: for i in 0 to 7 generate
    dbg_regs(8*i+7 downto 8*i) <= std_logic_vector(regs(i));
  end generate;
  dbg_zero <= zero_flag;
  dbg_dvc <= dvc;
  dbg_fontepc <= pcsrc;
end architecture;

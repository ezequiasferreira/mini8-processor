library ieee;
use ieee.std_logic_1164.all;

package mini8_pkg is
  subtype byte_t is std_logic_vector(7 downto 0);
  type memory_t is array (0 to 255) of byte_t;
  constant IDLE_INSTRUCTION : byte_t := x"C7"; -- BEQZ R0,-1
  constant EMPTY_ROM : memory_t := (others => IDLE_INSTRUCTION);
  constant EMPTY_RAM : memory_t := (others => (others => '0'));
  constant SUM_ROM : memory_t := (
    0 => x"41", 1 => x"0A", 2 => x"53", 3 => x"0C",
    4 => x"1C", 5 => x"94", 6 => x"C7", others => x"C7");
  constant SUM_RAM : memory_t := (0 => x"02", 2 => x"03", others => x"00");
  constant LOOP_ROM : memory_t := (
    0 => x"41", 1 => x"4A", 2 => x"53", 3 => x"D3", 4 => x"14",
    5 => x"1A", 6 => x"C4", 7 => x"8C", 8 => x"C7", others => x"C7");
  constant LOOP_RAM : memory_t := (
    0 => x"01", 1 => x"03", 3 => x"FF", others => x"00");
end package;

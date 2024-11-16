////////////////////////////////////////////////////////////////////////////////
// Author: Sudeep Joshi
// Date: 24/08/2023
// Description: Arctan Look-Up table for CORDIC Unit ( Q3.29 representation is chosen)
////////////////////////////////////////////////////////////////////////////////

module arctan_lookup #(parameter N = 32)
(
input [4:0] j,
output [N-1:0] arctan
);

reg [N-1:0] lookup_table[0:31];

initial
begin
	lookup_table[0]  <= 32'b000_11001001000011111101101010100;
	lookup_table[1]  <= 32'b000_01110110101100011001110000010;
	lookup_table[2]  <= 32'b000_00111110101101101110101111110;
	lookup_table[3]  <= 32'b000_00011111110101011011101010011;
	lookup_table[4]  <= 32'b000_00001111111110101010110111011;
	lookup_table[5]  <= 32'b000_00000111111111110101010101101;
	lookup_table[6]  <= 32'b000_00000011111111111110101010101;
	lookup_table[7]  <= 32'b000_00000001111111111111110101010;
	lookup_table[8]  <= 32'b000_00000000111111111111111110101;
	lookup_table[9]  <= 32'b000_00000000011111111111111111110;
	lookup_table[10] <= 32'b000_00000000001111111111111111111;
	lookup_table[11] <= 32'b000_00000000000111111111111111111;
	lookup_table[12] <= 32'b000_00000000000011111111111111111;
	lookup_table[13] <= 32'b000_00000000000000111111111111111;
	lookup_table[14] <= 32'b000_00000000000000011111111111111;
	lookup_table[15] <= 32'b000_00000000000000001111111111111;
	lookup_table[16] <= 32'b000_00000000000000000111111111111;
	lookup_table[17] <= 32'b000_00000000000000000011111111111;
	lookup_table[18] <= 32'b000_00000000000000000001111111111;
	lookup_table[19] <= 32'b000_00000000000000000000111111111;
	lookup_table[20] <= 32'b000_00000000000000000000011111111;
	lookup_table[21] <= 32'b000_00000000000000000000001111111;
	lookup_table[22] <= 32'b000_00000000000000000000000111111;
	lookup_table[23] <= 32'b000_00000000000000000000000011111;
	lookup_table[24] <= 32'b000_00000000000000000000000001111;
	lookup_table[25] <= 32'b000_00000000000000000000000000111;
	lookup_table[26] <= 32'b000_00000000000000000000000000011;
	lookup_table[27] <= 32'b000_00000000000000000000000000001;
	lookup_table[28] <= 32'b000_00000000000000000000000000000;
end

assign arctan = lookup_table[j];

endmodule
"""
CORDIC Lookup Table and Gain Generator with optional Qm.n fixed-point output.

This module generates:
  - angles = [atan(2**-i) for i in range(n_iter)]
  - K = product_{i=0..n_iter-1} (1/sqrt(1 + 2**(-2*i)))

Optionally, angles can be quantized into signed Qm.n format within 32 bits.
"""

import argparse
import math
import sys


def generate_cordic_lut(n_iter: int) -> tuple[list[float], float]:
    """
    Generate CORDIC arctan lookup table (LUT) and gain constant K.

    Args:
        n_iter: Number of iterations (size of LUT).

    Returns:
        A tuple containing:
          - angles: List of arctan(2^-i) values in radians.
          - K: Product of 1/sqrt(1 + 2^(-2*i)) over i in [0, n_iter).
    """
    angles: list[float] = []
    K: float = 1.0

    for i in range(n_iter):
        angle = math.atan(2.0 ** -i)
        angles.append(angle)
        K *= 1.0 / math.sqrt(1.0 + 2.0 ** (-2.0 * i))

    return angles, K


def format_qmn(
    angles: list[float], m: int, n: int
) -> list[str]:
    """
    Convert a list of radian angles into signed Qm.n fixed-point 32-bit values.

    Layout (bit indices):
      [31: sign]
      [30..30-m+1: integer bits]
      [30-m..30-m-n+1: fractional bits]

    Any remaining LSBs (to fill 32 bits) are zeros.

    Args:
        angles: List of float angles (radians).
        m: Number of integer bits (excluding sign).
        n: Number of fractional bits.

    Returns:
        List of formatted hex strings representing each angle in Qm.n.

    Raises:
        SystemExit: If total bits (1 + m + n) exceed 32.
    """
    total_bits = 1 + m + n
    if total_bits > 32:
        sys.exit(
            f"Error: 1 (sign) + m ({m}) + n ({n}) = {total_bits} bits exceeds 32."
        )

    shift_left = 32 - total_bits
    max_int = (1 << (m + n)) - 1
    half_range = 1 << (m + n)
    mask = (1 << total_bits) - 1

    result: list[str] = []

    for angle in angles:
        # Scale to integer value
        scaled = int(round(angle * (1 << n)))
        # Clamp to representable range
        if scaled > max_int:
            scaled = max_int
        if scaled < -half_range:
            scaled = -half_range

        # Two's complement representation
        twos = scaled & mask
        word = twos << shift_left
        result.append(f"0x{word:08X}")

    return result


def main() -> None:
    """
    Parse arguments and generate CORDIC LUT and gain constant K.
    """
    parser = argparse.ArgumentParser(
        description="Generate CORDIC LUT and gain K."
    )
    parser.add_argument(
        "-N", "--niter",
        type=int,
        default=16,
        help="Number of CORDIC iterations (default: 16)"
    )
    parser.add_argument(
        "--m",
        type=int,
        help="Number of integer bits in Qm.n (excluding sign)"
    )
    parser.add_argument(
        "--n",
        type=int,
        help="Number of fractional bits in Qm.n"
    )
    parser.add_argument(
        "-V", "--genverilog",
        action="store_true",
        help="Generate a Verilog module for the LUT"
    )
    args = parser.parse_args()

    angles, K = generate_cordic_lut(args.niter)

    print("# CORDIC Arctan LUT")
    if args.m is None or args.n is None:
        for i, angle in enumerate(angles):
            print(f"iter {i:2d}: atan(2^-{i}) = {angle:.12f} rad")
    else:
        hex_values = format_qmn(angles, args.m, args.n)
        for i, hex_val in enumerate(hex_values):
            print(f"iter {i:2d}: {hex_val}")

    print(f"\n# CORDIC Gain K = {K:.12f}")

    if args.genverilog:
        print("\n# Generating Verilog file for the lookup table")
        with open("rtl/lookup.v", "w") as f:
            f.write(
                "////////////////////////////////////////////////////////////////////////////////\n"
                "// Author: Sudeep Joshi\n"
                "// Description: Arctan Look-Up table for CORDIC Unit\n"
                "////////////////////////////////////////////////////////////////////////////////\n"
                "`default_nettype none\n\n"
                "module arctan_lookup #(\n"
                f"    parameter N = {1+args.m+args.n},\n"
                f"    parameter I = {args.niter}\n"
                ") (\n"
                "    input  wire                 clk,\n"
                "    input  wire                 rst_n,\n"
                "    input  wire [$clog2(I)-1:0] j,\n"
                "    output reg  [N-1:0]         arctan\n"
                ");\n\n"
                "    reg [N-1:0] lookup_table[0:I];\n\n"
                "    /*** Python Generated Block ***/\n"
                "    always @(posedge clk) begin\n"
                "       if(~rst_n) begin\n"
            )
            for i, hex_val in enumerate(hex_values):
                f.write(f"        lookup_table[{i}] <= 32'h{hex_val[2:]};\n")
            f.write(
                "    end\n\n"
                "    end\n\n"
                "    always @(posedge clk) begin\n"
                "        arctan <= lookup_table[j];\n"
                "    end \n\n"
                "endmodule\n"
            )


if __name__ == "__main__":
    main()


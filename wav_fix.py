#!/usr/bin/env python3

import struct
import sys


def main(argv0, in_fn, out_fn):

	try:
		in_fh = open(in_fn, 'rb')
	except:
		print("[!] Failed to open input file\n")
		return

	try:
		out_fh = open(out_fn, 'wb')
	except:
		print("[!] Failed to open output file\n")
		return

	# File header
	hdr = in_fh.read(12)
	if (hdr[0:4] != b'RIFF') or (hdr[8:12] != b'WAVE'):
		print("[!] Unexpected file header")
		return


	out_fh.write(hdr)

	# Chunks
	corr = 0

	while True:
		# Read chunk header
		chunk = in_fh.read(8)
		if not chunk:
			break

		# Write to output
		out_fh.write(chunk)

		# Split 4cc / length
		c_4cc = chunk[0:4]
		c_len = struct.unpack('<I', chunk[4:8])[0]

		# Data ?
		if c_4cc == b'data':
			# Read samples per sample
			for i in range(c_len // 4):
				sd = in_fh.read(4)
				sv = struct.unpack('<f', sd)[0]
				if sv > 1e3:
					out_fh.write(b'\x00\x00\x00\x00')
					corr += 1
				else:
					out_fh.write(sd)

		# Format ?
		elif c_4cc == b'fmt ':
			# Copy it
			fmt = in_fh.read(c_len)
			out_fh.write(fmt)

			# But also validate it's float data ...
			if fmt[0:2] != b'\x03\x00':
				print("[!] File is not float32 WAV")
				return

		# Other ?
		else:
			# Just copy
			out_fh.write(in_fh.read(c_len))

	out_fh.close()
	in_fh.close()

	print(f"[+] Done. Corrected {corr} samples")


if __name__ == '__main__':
	if len(sys.argv) != 3:
		print(f"Usage: {sys.argv[0]} in_file.wav out_file.wav")

	main(*sys.argv)

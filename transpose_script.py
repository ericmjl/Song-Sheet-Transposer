import transpose
import sys

from transpose import SheetMusic

if __name__ == '__main__':
	input_file = sys.argv[1]
	output_file = sys.argv[2]
	new_key = sys.argv[3]

	sm = SheetMusic()
	sm.read_song(input_file)
	sm.parse_song()
	sm.set_new_key(new_key)
	# sm.set_transpose_delta()
	# sm.set_transposed_parts()
	# print(sm.transposed_parts)
	# print(sm.arrangement)
	sm.write_chords(output_file)
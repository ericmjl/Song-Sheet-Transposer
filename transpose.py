import codecs

from copy import deepcopy

class SheetMusic(object):
	"""docstring for SheetMusic"""
	def __init__(self):
		super(SheetMusic, self).__init__()
		self.base_key = ''
		self.base_key_modifier = ''
		self.new_base_key = ''
		self.title = ''
		self.arrangement = []
		self.parts = dict()
		self.transposed_parts = None
		self.song = None
		self.transpose_delta = 0

		self.keys = ['A', 'Bb', 'B', 'C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab']
		
	def read_song(self, filename):
		self.song = codecs.open(filename, 'r', 'utf-8').readlines()

	def parse_song(self):
		for line in self.song:
			# Parse the title
			if line[0:7] == '>>Title':
				self.title = line.split(': ')[1].strip('\n')

		   	# Parse the current base_key of the arrangement
			if line[0:5] == '>>Key':
				current_key = line.split(':')[1].strip('\n').strip(' ').split(';')
				self.base_key = current_key[0]
				if len(current_key) > 1:
					self.base_key_modifier = current_key[1]
				else:
					self.base_key_modifier = ''
					
			# Parse the arrangement
			if line[0:13] == '>>Arrangement':
				self.arrangement = [part.strip('\n').strip(' ') for part in line.split(': ')[1].split(',')]


			# Parse out each part
			if line[0:3] == '>>>':
				part = line[3:].strip('\n')
				self.parts[part] = dict()
				line_counter = 0

				# This variable checks to make sure that we are parsing the correct part
				part_is_correct = False 
				
				for line2 in self.song:
					# Make sure that the part variable is correct, then we can proceed
					if line2[0:3] == '>>>' and line2[3:].strip('\n') == part:
						part_is_correct = True
					
					# Grab each chord and its position in the chord progression
					if line2[0:2] == 'C:' and part_is_correct:
						line_counter += 1
						self.parts[part][line_counter] = dict()
						self.parts[part][line_counter]['chords'] = dict()
						chords = [c for c in line2.strip('\n').split(':')[1].split(' ') if c != '']
						for chord in chords:
							position = line2[2:].index(chord)
							self.parts[part][line_counter]['chords'][position] = chord

					# Grab out the lyrics
					if line2[0:2] == 'L:' and part_is_correct:
						self.parts[part][line_counter]['lyrics'] = line2.strip('\n').split(':')[1]
						
					# End parsing
					if line2[0:3] == '<<<' and part_is_correct:
						break

	def set_new_key(self, newkey):
		# Check to make sure that newkey has the same set of modifiers as the old key.
		new_key = newkey.split(';')
		if len(new_key) > 1:
			new_modifier = newkey.split(';')[1]
		else:
			new_modifier = ''

		if new_modifier != self.base_key_modifier:
			raise Exception('New key has a different modifier from the old key.')

		else:
			self.new_base_key = newkey
			self._set_transpose_delta()
			self._set_transposed_parts()

	def _set_transpose_delta(self):
		old_idx = self.keys.index(self.base_key)
		new_idx = self.keys.index(self.new_base_key)
		
		self.transpose_delta = new_idx - old_idx

	def _set_transposed_parts(self):
		self.transposed_parts = deepcopy(self.parts)
		for part, lines in self.transposed_parts.items():
			for line, contents in lines.items():
				for position, chord in contents['chords'].items():
					contents['chords'][position] = self._get_transposed_chord(chord, self.transpose_delta)

	def _get_transposed_chord(self, current_chord, transpose_delta):
		# Get the base key
		if len(current_chord.split('/')) > 1:
			basekey = current_chord.split('/')[1]
		else:
			basekey = ''

		# Get the chord key
		chordkey = current_chord.split('/')[0].split(';')[0]
		
		# Get any modifiers
		if len(current_chord.split(';')) > 1:
			modifier = current_chord.split(';')[1].split('/')[0]
		else:
			modifier = ''
		
		# Transpose the chord key:
		new_chordkey = self._get_transposed_key(chordkey, transpose_delta)

		
		# Transpose the base key:
		if basekey != '':
			new_basekey = self._get_transposed_key(basekey, transpose_delta)

			return(new_chordkey + modifier + '/' + new_basekey)
		else:
			return(new_chordkey + modifier)

	def _get_transposed_key(self, current_key, transpose_delta):
		"""
		Note: only handles the base key and chord key, no modifiers allowed!
		"""
		
		current_idx = self.keys.index(current_key)
		new_idx = current_idx + transpose_delta
		
		if new_idx >= len(self.keys):
			new_idx = new_idx % len(self.keys)
			
		return self.keys[new_idx]


	def write_chords(self, filename):
		
		import codecs
		
		with codecs.open(filename, "w+", "utf-8") as f: 
			f.write(u'Title: {0}\n'.format(self.title))
			f.write(u'Key: {0}{1}\n'.format(self.new_base_key, self.base_key_modifier))
			f.write(u'Arrangement: ')
			for part in self.arrangement:
				f.write(u'{0} '.format(part))
			f.write('\n\n')
			
			for part in self.arrangement:
				f.write(u'----{0}----\n'.format(part))
				lines = self.transposed_parts[part]
				for line, contents in lines.items():

					chordstring = ' '
					maxchordpos = max(contents['chords'].keys())
					i = 1
					while i < maxchordpos + 1:
						if i not in contents['chords'].keys():
							chordstring += ' '
							i += 1
						else:
							for s in contents['chords'][i].split(';'):
								chordstring += s
								i += len(s)
					f.write(u'{0}\n'.format(chordstring))
					f.write(u'{0}\n'.format(contents['lyrics']))
				f.write('\n')
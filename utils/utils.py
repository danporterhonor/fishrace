def join_words(words):
    if len(words) > 2:
        return '%s, and %s' % ( ', '.join(words[:-1]), words[-1] )
    else:
        return ' and '.join(words)

def read_names_from_file(filename):
    with open(filename, 'r') as file:
        names = file.read().splitlines()
    return names

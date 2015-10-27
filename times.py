import random


def file_times(filename):
    with open(filename) as f:
        lines = f.read().splitlines()
        for line in lines:
            yield int(line)


def random_times(p):
    """Selects a key at random with the paired value as the probability."""
    while True:
        if sum(p.values()) != 1:
            raise ValueError('Probabilities must sum to unity')
        r = random.random()
        remaining = 1
        for category, probability in p.items():
            remaining -= probability
            if remaining <= r:
                yield category
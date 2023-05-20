import string
import random


def generate_random_string(length=10):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))
import re
import os
import glob
import sys
from decimal import Decimal
from enum import IntEnum
from termcolor import colored

class Item(IntEnum):
    KEY = 0
    NONCE = 1
    NONCES = 2
    STAGGER = 3

def parse_file_name(file_name):
    rx = r"(\d+)_(\d+)_(\d+)_(\d+)"
    regex = re.compile(rx)

    res = regex.match(file_name)
    if res is None: return None

    groups = res.groups()
    if len(groups) == 0: return None

    result = list()
    for group in groups:
        result.append(Decimal(group))

    return result


def get_file_size(file_path):
    st = os.stat(file_path)
    return Decimal(st.st_size)


if len(sys.argv) < 2:
    sys.stdout.write(colored("BURST plots checker (version 1.0)\nChecking and validation plots for BURST\t\n", color='green'))
    print(colored("[Original idea: Blago]", color = 'blue'))
    print(colored("[Sponsored by: VPS.ag - Quality VPS for only 2 EUR ]", color = 'blue'))
    print(colored("[]", color = 'blue'))  
    print(colored("Usage: plotschecker.py [PATH]\nExample: plotschecker.py D:/plots", color='green'))

    sys.exit(0)

#for filepath in glob.iglob(sys.argv[1] + '**/*', recursive=True):
for root, dirnames, filenames in os.walk(sys.argv[1]):
    for file in filenames:
        filepath = os.path.join(root, file)
        filename = os.path.split(filepath)[-1]
        items = parse_file_name(filename)
        if items is None: continue

        file_size = get_file_size(filepath)
        expected_size = items[Item.NONCES] * 4096 * 64

        sys.stdout.write("file {}\t".format(filename))

        if file_size == expected_size:
            print(colored("checked - OK", color='green'))
            continue

        if items[Item.NONCES] == items[Item.STAGGER]:
            print(colored("need to delete and repot", color='red'))
            continue

        new_nonces = Decimal(file_size / 4096 / 64)
        new_nonces = Decimal((new_nonces / items[Item.STAGGER]) * items[Item.STAGGER])

        new_name = "{}_{}_{}_{}".format(items[Item.KEY], items[Item.NONCE], new_nonces, items[Item.STAGGER])
        new_path = os.path.dirname(filepath) + "/" + new_name
        os.rename(filepath, new_path)

        print(colored("renamed to {}".format(new_name), color = 'yellow'))

        new_nonces_size = Decimal(new_nonces * 4096 * 64)
        if file_size == new_nonces_size: continue

        os.truncate(new_path, new_nonces_size)
        colored("truncated to {}".format(new_nonces_size), color='blue')

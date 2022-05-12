import os
import time
import sys
import argparse

from huffman import (
    encode,
    decode,
)
from utils import (
    correct_test,
    MODE_COMPRESS,
    MODE_DECOMPRESS,
    MODE_TEST,
)


def createParser():
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
            prog = 'main.py',
            description = """This program allows you to compress and decompress files using the Huffman method.""",
            epilog = """(c) Sait Sharipov, group 519/2, CMC MSU""",
    )
    parser.add_argument('-f', '--filename', type=str, required=True,
                        help='filename/filepath to file for compress/decompress')
    parser.add_argument('-m', '--mode', choices=[1, 2, 3], type=int, required=True,
                        help='mode of program: mode=1 is compress, mode=2 is decompress, mode=3 for testing')
    return parser


def get_arguments() -> (str, int):
    """Return filename for compress/decompress and mode of program."""
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    return namespace.filename, namespace.mode


if __name__ == '__main__':

    start_time = time.perf_counter()


    filename, mode = get_arguments()

    if not os.path.exists(filename):
        print("File doesn't find!")
        exit(1)

    if mode == MODE_COMPRESS:
        encode(filename, start_time)

    if mode == MODE_DECOMPRESS:
        decode(filename, mode, start_time)

    if mode == MODE_TEST:
        encode_filepath = encode(filename, start_time)
        mid_time = time.perf_counter()
        decode_filepath = decode(encode_filepath, mode, mid_time)
        correct_test(filename, encode_filepath, decode_filepath)

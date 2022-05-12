import os
import time
import filecmp
from collections import defaultdict


MODE_COMPRESS = 1
MODE_DECOMPRESS = 2
MODE_TEST = 3


def get_byte_representation_from_file(file_path: str) -> list:
    """
    Returns a list of file bytes.

    :param file_path: str, path to this file
    :return: list_of_bytes: list of file bytes
    """
    list_of_bytes = []

    try:
        with open(file_path, 'rb') as fin:  # open file in binary format
            byte = fin.read(1)
            while byte != b'':                      # until we reached the end of the file
                list_of_bytes.append(byte)
                byte = fin.read(1)
    except:
        print("File can't be open for reading!")
        exit(1)

    return list_of_bytes


def get_frequency_dict_from_byte_representation(list_of_bytes: list) -> dict:
    """
    According to the list of bytes in the file, the function returns
    a dictionary containing how many times each byte occurs in the file.

    :param list_of_bytes: list of file bytes
    :return: dictionary of byte frequencies in the source file
    """

    byte_to_frequency_dict = defaultdict(int)
    for byte in list_of_bytes:
        byte_to_frequency_dict[byte] += 1
    return byte_to_frequency_dict


def write_bytes_to_file(all_bytes: bytes, file_path: str) -> None:
    """Write bytes to file."""
    try:
        with open(file_path, 'wb') as fout:
            fout.write(all_bytes)
    except:
        print("File can't be open for writing!")
        exit(1)


def correct_test(start_filepath: str, encode_filepath: str, decode_filepath: str) -> None:
    flag = filecmp.cmp(start_filepath, decode_filepath, shallow=False)
    if not flag:
        print("Error: input file and decompress file (after compression) don't equal.")
    else:
        print("OK: input file and decompress file (after compression) are equal.")
        sz1 = os.path.getsize(start_filepath)
        sz2 = os.path.getsize(encode_filepath)
        if sz1 > 0:
            print(f"Deflated {100 - 100 * (sz2 / sz1):0.1f}% of the original file.")


def print_execution_time(start_time: float, mode: int) -> None:
    finish_time = time.perf_counter()
    if mode == MODE_COMPRESS:
        print(f"Compression time: {finish_time - start_time:0.4f} seconds.")
    elif mode == MODE_DECOMPRESS:
        print(f"Decompression time: {finish_time - start_time:0.4f} seconds.")

def print_size_of_files(file_path: str, mode: int=None) -> None:
    if mode is None:
        print(f"Input file size: {os.path.getsize(file_path)} bytes.")
    if mode == MODE_COMPRESS:
        print(f"Compression file size: {os.path.getsize(file_path)} bytes.")
    if mode == MODE_DECOMPRESS:
        print(f"Decompression file size: {os.path.getsize(file_path)} bytes.")



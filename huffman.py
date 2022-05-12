import os
import heapq # priority queue
from bitarray import bitarray

from node import Node
from utils import (
    get_byte_representation_from_file,
    get_frequency_dict_from_byte_representation,
    write_bytes_to_file,
    MODE_COMPRESS,
    MODE_DECOMPRESS,
    MODE_TEST,
    print_execution_time,
    print_size_of_files,
)


BYTE_SIZE = 8


def get_huffman_tree(byte_to_frequency_dict: dict) -> Node:
    """By byte frequencies, we return the root of the Huffman tree."""

    sorted_frequency_byte = [Node(key, val) for key, val in byte_to_frequency_dict.items()]
    # Built priority queue.
    heapq.heapify(sorted_frequency_byte)

    while len(sorted_frequency_byte) > 1:
        # We take two elements with the lowest frequency.
        min_elem1 = heapq.heappop(sorted_frequency_byte)
        min_elem2 = heapq.heappop(sorted_frequency_byte)
        # We add the sum of these elements to the rest of the elements.
        sum_of_min_elems = Node(value=min_elem1.value + min_elem2.value, left=min_elem1, right=min_elem2)
        sorted_frequency_byte.append(sum_of_min_elems)
    root = heapq.heappop(sorted_frequency_byte)
    return root


def build_huffman_codes_dict(node: Node, code: bitarray, huffman_codes_dict: dict) -> None:
    """
    Building the Huffman codes.
    Recursively we descend from the root to the leaves.
    """
    if node.key is None: # we are in an intermediate node
        build_huffman_codes_dict(node.left, code + bitarray('0'), huffman_codes_dict)
        build_huffman_codes_dict(node.right, code + bitarray('1'), huffman_codes_dict)
    else:                    # we are in the initial byte - tree leaf
        huffman_codes_dict[node.key] = code


def get_huffman_codes_dict(byte_to_frequency_dict: dict) -> dict:
    """By byte frequencies, we get a dictionary with Huffman codes for each byte."""
    root = get_huffman_tree(byte_to_frequency_dict)
    huffman_codes_dict = {}
    build_huffman_codes_dict(root, bitarray(), huffman_codes_dict)
    if len(huffman_codes_dict) == 1:
        huffman_codes_dict[list(huffman_codes_dict.keys())[0]] = bitarray('0')
    return huffman_codes_dict


def get_huffman_bit_code(list_of_bytes: list, huffman_codes_dict: dict) -> bitarray:
    bit_code = bitarray()
    for byte in list_of_bytes:
        bit_code += huffman_codes_dict[byte]
    return bit_code


def encode_huffman_bit_code(my_bitarray: bitarray) -> bytes:
    """
    Complements the bitarray with zero bits to fill the last byte and adds
    a byte encoding the number of significant bits in the last byte.
    """
    # Complements the bitarray with zero bits to fill the last byte.
    cnt_bits_of_last_byte = len(my_bitarray) % BYTE_SIZE
    if cnt_bits_of_last_byte == 0: # it is full byte
        cnt_bits_of_last_byte = BYTE_SIZE
    my_bitarray += bitarray('0' * (BYTE_SIZE - cnt_bits_of_last_byte))
    # Adds a byte encoding the number of significant bits in the last byte.
    first_byte_bitarray = bitarray()
    first_byte_bitarray.frombytes((cnt_bits_of_last_byte.to_bytes(length=1, byteorder='big')))
    return bytes(first_byte_bitarray + my_bitarray)


def decode_huffman_bit_code(list_of_bytes: list, huffman_codes_dict: dict) -> bytes:
    cnt_bits_of_last_byte = ord(list_of_bytes[0])
    bit_code = bitarray()
    for byte in list_of_bytes[1:]:
        tmp = bitarray()
        tmp.frombytes(byte)
        bit_code += tmp
    finish_bit = len(bit_code)
    if cnt_bits_of_last_byte != BYTE_SIZE:
        finish_bit = -(BYTE_SIZE - cnt_bits_of_last_byte)
    list_of_bytes = bit_code[:finish_bit].decode(huffman_codes_dict)
    all_bytes = b"".join(list_of_bytes)
    return all_bytes


def encode_file_extension(file_path: str) -> bytes:
    filename, file_extension = os.path.splitext(file_path)
    if len(file_extension) != 0: # file_path has extension
        file_extension = file_extension[1:] # remove dot
    file_extension_bytes = bytes()
    file_extension_bytes += int.to_bytes(len(file_extension), length=1, byteorder='big')
    file_extension_bytes += file_extension.encode('utf-8')
    return file_extension_bytes


def decode_file_extension(list_of_bytes: list) -> str:
    all_bytes = bytes()
    for byte in list_of_bytes:
        all_bytes += byte
    return all_bytes.decode()


def encode_huffman_codes_dict(huffman_codes_dict: dict) -> bytes:
    dict_bytes = bytes()
    dict_bytes += int.to_bytes(len(huffman_codes_dict) - 1, length=1, byteorder='big')
    for k, v in huffman_codes_dict.items():
        dict_bytes += k
        dict_bytes += int.to_bytes(len(v), length=1, byteorder='big')

        # Complements the bitarray with zero bits to fill the last byte.
        tmp_bitarray = bitarray()
        tmp_bitarray += v
        cnt_bits_of_last_byte = len(tmp_bitarray) % BYTE_SIZE
        if cnt_bits_of_last_byte == 0:  # it is full byte
            cnt_bits_of_last_byte = BYTE_SIZE
        tmp_bitarray += bitarray('0' * (BYTE_SIZE - cnt_bits_of_last_byte))

        dict_bytes += bytes(tmp_bitarray)
    return dict_bytes


def decode_huffman_codes_dict(list_of_bytes: list, len_of_dict: int) -> (dict, int):
    huffman_codes_dict = {}
    i = 0
    cnt_of_dict_elems = 0
    while i < len(list_of_bytes) and cnt_of_dict_elems < len_of_dict:
        cnt_of_dict_elems += 1
        byte_val = list_of_bytes[i]
        len_byte_code_in_bits = ord(list_of_bytes[i + 1])
        cnt_of_bytes = len_byte_code_in_bits // BYTE_SIZE + (len_byte_code_in_bits % BYTE_SIZE != 0)
        byte_code = bitarray()
        for byte in list_of_bytes[i+2:i+2+cnt_of_bytes]:
            tmp = bitarray()
            tmp.frombytes(byte)
            byte_code += tmp
        byte_code = byte_code[:len_byte_code_in_bits]
        huffman_codes_dict[byte_val] = byte_code
        i += 2 + cnt_of_bytes
    return huffman_codes_dict, i


def encode(file_path: str, start_time: float) -> str:
    print_size_of_files(file_path)
    list_of_bytes = get_byte_representation_from_file(file_path)

    if len(list_of_bytes) > 0: # file doesn't empty
        byte_to_frequency_dict = get_frequency_dict_from_byte_representation(list_of_bytes)
        huffman_codes_dict = get_huffman_codes_dict(byte_to_frequency_dict)
        huffman_code_bitarray = get_huffman_bit_code(list_of_bytes, huffman_codes_dict)

    all_bytes = encode_file_extension(file_path)
    if len(list_of_bytes) > 0: # file doesn't empty
        bytes_of_huffman_codes_dict = encode_huffman_codes_dict(huffman_codes_dict)
        bytes_of_huffman_code = encode_huffman_bit_code(huffman_code_bitarray)
        all_bytes += bytes_of_huffman_codes_dict + bytes_of_huffman_code

    filename, _ = os.path.splitext(file_path)
    new_file_path = filename + ".zmh"

    write_bytes_to_file(all_bytes, new_file_path)
    print_execution_time(start_time, MODE_COMPRESS)
    print_size_of_files(new_file_path, MODE_COMPRESS)
    return new_file_path


def decode(file_path: str, mode: int, start_time: float) -> str:

    list_of_bytes = get_byte_representation_from_file(file_path)

    # Get file extension.
    len_file_extension = ord(list_of_bytes[0])
    file_extension = decode_file_extension(list_of_bytes[1:1+len_file_extension])

    bytes_of_unzip_file = bytes()
    # Get Huffman_codes_dict.
    if len(list_of_bytes) > 1 + len_file_extension:
        len_of_huffman_codes_dict = ord(list_of_bytes[1+len_file_extension]) + 1
        huffman_codes_dict, byte_size_of_dict = decode_huffman_codes_dict(list_of_bytes[2+len_file_extension:],
                                                                          len_of_huffman_codes_dict)
        # Get bytes of unzip file.
        bytes_of_unzip_file = decode_huffman_bit_code(list_of_bytes[2+len_file_extension+byte_size_of_dict:], huffman_codes_dict)

    filename, _ = os.path.splitext(file_path)
    if mode == MODE_TEST:
        new_file_path = filename + "_new" + "." + file_extension
    else:
        new_file_path = filename + "." + file_extension

    write_bytes_to_file(bytes_of_unzip_file, new_file_path)
    print_execution_time(start_time, MODE_DECOMPRESS)
    print_size_of_files(new_file_path, MODE_DECOMPRESS)
    return new_file_path

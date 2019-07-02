#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IPS Patcher
# Copyright (©) itari 2014
# Do whatever you want with this, I don't care. :D
#
# Modified by sli to work on the command line and with
# Python 3. Who even uses Tkinter anymore?

import os
import sys
import shutil


# Some arrays with byte data for the "PATCH" and "EOF" of the IPS
patch_magic = [0x50, 0x41, 0x54, 0x43, 0x48]
eof_magic = [0x45, 0x4F, 0x46]


# Read and write a bytearray to a file cheats :D
def read_all_bytes(file):
    return bytearray(open(file, 'rb').read())


def write_all_bytes(file, data):
    open(file, 'wb').write(data)


# Functions to help with getting an integer from a bytearray
# This are big endian, because that's how IPS rolls~
def get_uint16(data, index):
    return int((data[index] << 8) | data[index + 1])


def get_uint24(data, index):
    return int((data[index] << 16) | (data[index + 1] << 8) | data[index + 2])


# Compare two byte arrays
def compare(data1, data2, count, index1=0, index2=0):
    for i in range(count):
        if not data1[index1 + i] == data2[index2 + i]:
            return False
    return True


def apply_patch(rom, patch):
    # Read files
    patch_data = read_all_bytes(patch)
    file_data = read_all_bytes(rom)

    # Check patch "PATCH" header
    if not compare(patch_data, patch_magic, 5):
        print('Error: invalid patch file (bad header)')
        return

    # Check patch "EOF" footer
    if not compare(patch_data, eof_magic, 3,
                   index1=(len(patch_data) - 3), index2=0):
        print('Error: invalid patch file (bad footer)')
        return

    # Backup original ROM
    rom_bak = rom + '.bak'
    shutil.copy(rom, rom_bak)
    print('Backup -> {}'.format(rom_bak))
    print('Patch -> {}'.format(rom))

    # Apply patch
    i = 5
    while i < len(patch_data) - 3:
        # Get offset
        offset = get_uint24(patch_data, i)
        i += 3

        # Packet cannot be at 0x454F46 because it is "EOF"
        # if offset == 0x454F46:
        #    break

        # Get packet size
        size = get_uint16(patch_data, i)
        i += 2

        # Check & apply
        if size == 0:
            # Get RLE repeat count
            rle_size = get_uint16(patch_data, i)
            i += 2

            # Get repeat byte
            repeat = patch_data[i]
            i += 1

            # Apply to file
            for x in range(rle_size):
                file_data[offset + x] = repeat
        else:
            # Normal packet
            # Copy from patch to file
            for x in range(size):
                file_data[offset + x] = patch_data[i]
                i += 1


    # Write modified data
    write_all_bytes(rom, file_data)

    # All done
    print('Patch applied successfully.')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python ips.py <ROM file> <patch file>')
        sys.exit(1)

    rom = sys.argv[1]
    patch = sys.argv[2]
    err = False

    if not os.path.isfile(rom):
        print('Error: ROM file not found.')
        err = True

    if not os.path.isfile(patch):
        print('Error: patch file not found.')
        err = True

    if err:
        sys.exit(1)

    apply_patch(rom, patch)

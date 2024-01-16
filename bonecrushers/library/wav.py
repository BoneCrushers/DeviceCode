# WAV File Parse Utilities
# (C) 2019-2023 Flint Million <flint.million@mnsu.edu>
# extracted from "wavtool" project and adapted for Bonecrushers

import os.path
import struct
import sys

class WavError(Exception):
    """Raised when errors are encountered parsing WAV files."""
    pass

def __print_err(s, end="\n", flush=True):
    """convenience method to print to stderr, partially mirrors normal print() statement"""
    sys.stderr.write(s+end)
    if flush:
        sys.stderr.flush()
    
def get_chunks(wavFile):

    """Parses a WAV file and retrieves its chunks as a dictionary"""
    
    chunks = {} # dict to store all chunks in the WAV file
    # note that entire WAV will be loaded into RAM - for small WAVs this is ok, but
    # might be a problem for big files - maybe look at a streaming file strategy
    # for the future?

    # If file doesn't exist, return error
    if not os.path.isfile(wavFile): raise WavError("No such file or directory")

    # Get file size
    wav_size = os.path.getsize(wavFile)

    # if wav size is too small, return error
    # minimum wav file size (empty PCM file with no samples) is 44 bytes
    if wav_size < 44: raise WavError("Not a WAV file [too small]")

    # Open the wav file
    wav_fh = open(wavFile,"rb")

    # Read the riff header
    test_riff = wav_fh.read(4).decode('ascii')
    if test_riff != "RIFF": raise WavError("Not a WAV file [no RIFF header]")

    # Check the file size
    test_fsize = struct.unpack("<L",wav_fh.read(4))[0]
    if (test_fsize + 8) > wav_size: raise WavError("Invalid WAV file [total file size in header > actual file size]")

    # Check the WAV header
    test_wav = wav_fh.read(4).decode('ascii')
    if test_wav != "WAVE": raise WavError("Not a WAV file [type is '%s', not 'WAVE']"%test_wav)

    # Start loading chunks
    while True:

        ck_head = wav_fh.read(8) # Header includes both chunk ID and chunk size

        if len(ck_head)<8:
            break # no more data

        # TODO: figure out what causes this?
        # if ck_head starts with a 0x00, then move one byte forward and try again
        if ck_head[0] == 0x00:
            __print_err("WARNING: byte at position %d should be chunk ID but is null. Skipping one byte."% (wav_fh.tell()-8))
            wav_fh.seek(-7,1) # move back 7 bytes 
            continue

        ck_size = struct.unpack("<L",ck_head[4:])[0] # chunk size is little endian
        ck_name_raw = ck_head[:4] 
        try:
            ck_name = ck_head[:4].decode('utf-8') # warning, might fail
        except UnicodeDecodeError:
            ck_name = "(unprintable)"

        ck_data = wav_fh.read(ck_size)

        #__print_err("%s chunk, %d bytes"%(ck_name,ck_size))

        chunks[ck_name_raw] = ck_data

    return chunks


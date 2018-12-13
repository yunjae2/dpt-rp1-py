#!/usr/bin/env python3
"""
usage: notes.py ip_address
"""

import json
import os
import dateparser

from dptrp1.dptrp1 import DigitalPaper

SYNC_DIR = os.path.expanduser('~/dev/dptrp1/sync/')
CLIENT_DAT = os.path.expanduser('~/dev/dptrp1/.client.dat')
KEY_DAT = os.path.expanduser('~/dev/dptrp1/.key.dat')

def connect(address):
    """
    Loads the key and client ID to authenticate with the DPT-RP1
    """
    with open(CLIENT_DAT, 'r') as f:
        client_id = f.readline().strip()

    with open(KEY_DAT, 'r') as f:
        key = f.read()

    dpt = DigitalPaper(address)
    dpt.authenticate(client_id, key)
    return dpt

def download_notes(dpt):
    """
    Given an authenticated DigitalPaper instance, download all note files to a
    specified directory.
    """
    for doc in [f for f in dpt.list_documents() if is_modified_note(f)]:
        data = dpt.download(doc['entry_path'])
        local_path = SYNC_DIR + os.path.basename(doc['entry_path'])
        os.makedirs(os.path.dirname(local_path), exist_ok = True)
        with open(local_path, 'wb') as f:
            f.write(data)
        print('Saved {} to {}'.format(doc['entry_path'], local_path))


def is_modified_note(doc):
    if doc['document_type'] == 'note':
        local_path = SYNC_DIR + os.path.basename(doc['entry_path'])
        if not os.path.exists(local_path):
            return True
        else:
            return os.path.getmtime(local_path) < dateparser.parse(
                doc['modified_date']).timestamp()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('address', help="IP address of the DPT-RP1")
    args = parser.parse_args()

    try:
        dpt = connect(args.address)
        print('connect success')
        download_notes(dpt)
    except OSError:
        print('Unable to reach device, verify it is connected to the same network segment.')
        exit(1)

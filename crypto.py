#!/usr/bin/env python

import argparse
import re

from cryptography.fernet import Fernet

from configtracker import Decrypter
from api.src.encryptor import Encryptor

parser = argparse.ArgumentParser(description="""Configtracker crypto script. You can:
- encrypt/decrypt strings with defined master key in this system or define it manually
- get new master key (IT ONLY SHOWS EXAMPLE OF KEY!)""", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-m', '--master-key', action='store', type=str,
                    help='Master Key. If not set, the script will try to get it from environment or from ' +
                         'setting/master_key file')
parser.add_argument('-g', '--generate-master-key', action='store_true',
                    help='Generate new master key (IT ONLY SHOWS EXAMPLE OF NEW KEY)')
parser.add_argument('-e', '--encrypt', action='store', metavar='STRING',
                    type=str, help='Encrypt string')
parser.add_argument('-d', '--decrypt', action='store', metavar='STRING',
                    type=str, help='Decrypt string')

args = parser.parse_args()

if args.generate_master_key:
    print(Fernet.generate_key().decode('utf-8'))
    quit()

if args.master_key:
    try:
        f = Fernet(args.master_key)
    except Exception as e:
        print(e)
        print('Error! Incorrect master key')
    if args.encrypt:
        try:
            print(f"fernet({f.encrypt(args.encrypt.encode()).decode('utf-8')})")
        except Exception as e:
            print(e)
            print('Error! Cannot encrypt data')
    elif args.decrypt:
        try:
            token = re.search(r'fernet\((.*?)\)', args.decrypt).group(1)
        except:
            token = args.decrypt
        try:
            print(f.decrypt(token.encode()).decode('utf-8'))
        except Exception as e:
            print(e)
            print('Error! Cannot decrypt data')
    else:
        print('Error! Please set string for encryption or decryption')
    quit()

if args.encrypt:
    _data = Encryptor.run(args.encrypt)
    if _data == args.encrypt:
        print('Error! Encryption is failed please check master key')
    else:
        print(_data)
    quit()

if args.decrypt:
    _data = Decrypter.run(args.decrypt)
    if _data == args.decrypt:
        print('Error! Decryption is failed please check master key')
    else:
        print(_data)
    quit()


parser.print_help()

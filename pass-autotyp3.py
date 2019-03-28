#!/usr/bin/python3
import os
import subprocess
from xdo import Xdo
from zenipy import zlist
from time import sleep


PASSWORD_STORE_DIR = (os.environ.get('PASSWORD_STORE_DIR') or os.path.expanduser('~/.password-store'))
USER_FIELD = 'user'
AUTOTYPE_SEQUENCE = ':user |Tab :password |Return'
SLEEP = 0.1
BACKSPACE = True
DELAY = 20000
DEBUG = False


def get_window(debug=False):
    win_id = xdo.get_active_window()
    win_name = xdo.get_window_name(win_id).decode()

    if debug:
        print("window:", win_id, "title:", win_name)

    return win_id, win_name


def run(*cmd):
    ret = subprocess.run(cmd, stdout=subprocess.PIPE)
    return [out.strip() for out in ret.stdout.decode('utf-8').split("\n") if out.strip()]


def read_gpg(gpgpath):
    rel = os.path.relpath(gpgpath, start=PASSWORD_STORE_DIR)
    split = os.path.splitext(gpgpath)

    group = os.path.dirname(rel) if os.path.dirname(rel) else '/'
    name = os.path.basename(split[0])

    out = run('pass', 'show', os.path.join(group, name))

    password = out[0] if out else None

    # create minimal contents dict, _group, and _name is meta content
    gpg = {'_group': group,
           '_name': name,
           'password': password,
           USER_FIELD: None}

    # add additional fields
    if len(out) > 1:
        for line in out[1:]:
            if ':' in line:
                t = line.split(':', maxsplit=1)

                gpg[t[0]] = t[1].lstrip()

    return gpg


def get_autotype_entries(debug=False):
    tree = os.walk(PASSWORD_STORE_DIR)

    entries = {}

    for root, _, files in list(tree):
        autotypes = [f for f in files if f.endswith('.autotype')]

        for autotype in autotypes:
            gpgpath = os.path.join(root, autotype.replace('.autotype', '.gpg'))

            if os.path.exists(gpgpath):
                with open(os.path.join(root, autotype), 'r') as f:
                    # fetch all lines, ignore empty ones
                    lines = [line for line in f.read().splitlines() if line]

                autotype_sequences = [line for line in lines if line.startswith(':')]
                autotype_matching = set(lines) - set(autotype_sequences)

                # only create entries, if matchstrings is not empty
                if autotype_matching:
                    entries[gpgpath] = {}
                    entries[gpgpath]['matches'] = False
                    entries[gpgpath]['matching'] = autotype_matching
                    entries[gpgpath]['sequence'] = autotype_sequences[0] if autotype_sequences else AUTOTYPE_SEQUENCE


    if debug:
        print()
        print("AUTOTYPE ENTRIES")
        if entries:
            for gpgpath, entry in entries.items():
                print(gpgpath)
                print("   matches:", entry['matches'])
                print("   matching:", [match for match in entry['matching']])
                print("   sequence:", entry['sequence'])

        else:
            print(None)

    return entries


def get_matching_entries(entries, window_title, debug=False):
    for gpgpath, entry in sorted(entries.items()):
        for string in entry['matching']:
            if string in window_title:
                entry['matches'] = True
                break

    matches = {gpgpath: entry for gpgpath, entry in entries.items() if entry['matches']}

    if debug:
        print()
        print("MATCHING ENTRIES")

        if matches:
            for gpgpath, entry in matches.items():
                print(gpgpath)
                print("   matches:", entry['matches'])
                print("   matching:", [match for match in entry['matching']])
                print("   sequence:", entry['sequence'])

        else:
            print(None)

    return matches


def get_entry(matches, debug=False):
    entries = []
    items = []
    columns = ['Index', 'Group', 'Name', 'User']

    entry = None

    for idx, (gpgpath, match) in enumerate(sorted(matches.items())):
        gpg = read_gpg(gpgpath)

        # add the sequence
        gpg['_sequence'] = match['sequence']

        entries.append(gpg)
        items.extend([str(idx), gpg['_group'], gpg['_name'], str(gpg[USER_FIELD])])

    if len(entries) > 1:
        index = zlist(columns=columns, items=items, print_columns=0, text='choose a password entry', title='pass-autotype')

        if index:
            entry = entries[int(index[0])]

    else:
        entry = entries[0]

    if debug:
        print()
        print("ENTRY")

        if entry:
            fields = ['_group', '_name', '_sequence', 'password']

            if entry.get(USER_FIELD):
                fields.insert(-1, USER_FIELD)

            for field in fields + [f for f in entry.keys() if f not in fields]:
                print("%s: %s" % (field, entry[field]))
        else:
            print(None)

    return entry


def xdo_keys(*keys):
    for k in keys:
        xdo.send_keysequence_window(0, k.encode())


def xdo_type(text, delay=12000):
    xdo.enter_text_window(0, text.encode(), delay=delay)


def autotype(entry, delay=12000, debug=False):
    if debug:
        xdo_type('Hello world!')
        xdo_keys('Return')

        xdo_type('Abc&abc')
        xdo_keys('Return')

        xdo_type("""`r}Ltb}¸K4g'Bt*>{v5nk""")
        xdo_keys('Return')

    else:
        sequence = entry['_sequence']

        # :user |Tab :password |Return !0.5 :myfield
        for item in sequence.split(' '):
            typ, arg = item[0], item[1:]

            xdo_type(entry[arg], delay=delay) if typ == ':' else xdo_keys(arg) if typ == '|' else sleep(float(arg)) if typ == '!' else 0


if DEBUG:
    os.system('clear')


xdo = Xdo()
_, win_name = get_window()

autotype_entries = get_autotype_entries(debug=DEBUG)

if autotype_entries:
    matching_entries = get_matching_entries(autotype_entries, win_name, debug=DEBUG)

    if matching_entries:
        entry = get_entry(matching_entries, debug=DEBUG)

        if entry:
            sleep(SLEEP)

            if BACKSPACE:
                xdo_keys('BackSpace')

            autotype(entry, delay=DELAY)

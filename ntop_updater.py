#!/usr/bin/env python

# Everything about this code makes me sad.
#
# We can't use ctypes or the native Python library for nTop because
# nTop has unresolved dependencies that are fulfilled only by the
# ntop binary itself (static_ntop and welcome, for example).
#
# Apparently nTop also adds their own sauce into gdbm for storing
# numeric values (string keys and contents end with \0 while keys that
# store numeric values end with \000).
#
# It also appears that there's no way to make nTop HUP to re-read the
# preferences database to begin with so we get to restart the service
# when something changes.

import collections
import anydbm
import re
import SocketServer

PREFS_DB = "/var/lib/ntop/prefsCache.db"    # Default location for Ubuntu
HOST = "0.0.0.0"
PORT = 2056                                 # Default port for dd-wrt's macupd
VALID_HOST = "192.168.1.1"                  # Listen for data from this host
DEBUG = False

class CaseInsensitiveDict(collections.Mapping):
    def __init__(self, d):
        self._d = d
        self._s = dict((k.lower(), k) for k in d)

    def __contains__(self, k):
        return k.lower() in self._s

    def __len__(self):
        return len(self._s)

    def __iter__(self):
        return iter(self._s)

    def __getitem__(self, k):
        return self._d[self._s[k.lower()]]

    def actual_key_case(self, k):
        return self._s.get(k.lower())


MAPPINGS = CaseInsensitiveDict({
    "AA:BB:CC:DD:EE:FF": "Computer 1",
    "BB:AA:CC:DD:EE:FF": "Computer 2",
})

class MacAddressUdpHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        client = self.client_address[0]

        if client != VALID_HOST:
            if DEBUG:
                print "Data received from invalid host %s" % client

            return

        # Ignore rssi/wireless
        if "+" in data:
            return

        data_array = re.split(r"\s+", data)

        # Ignore invalid format
        if len(data_array) != 7:
            return

        ip = data_array[1]
        mac = data_array[4]

        # Only update if we have a mapping for that MAC address
        if mac in MAPPINGS:
            key = "hostname.%s" % ip

            if DEBUG:
                print "Updating %s to %s" % (key, MAPPINGS[mac])

            changed = set_preference_key(key, MAPPINGS[mac])

            if changed:
                print "Value was changed, restarting nTop"


def print_db_contents(file):
    db = anydbm.open(file, "r")

    key = db.firstkey()

    while key != None:
        print "%s: %s" % (key, db[key])

        key = db.nextkey(key)

    db.close()


def set_preference_key(key, value):
    db = anydbm.open(PREFS_DB, "w")

    changed = False

    if db[key] != value:
        key = key + "\0"
        value = value + "\0"

        db[key] = value

        changed = True

    db.close()

    return changed

if __name__ == "__main__":
    print "Listening on %s:%s for data from %s" % (HOST, PORT, VALID_HOST)

    server = SocketServer.UDPServer((HOST, PORT), MacAddressUdpHandler)

    server.serve_forever()

from bluepy.btle import Scanner, Peripheral, BTLEException
import binascii
import pprint
import datetime
import json

class read_char(Peripheral):
    def __call__(self, addr, char, debug=False):
        for a in range(10):
            debug and print("Try %d to read %02x from %s" % (a, char, addr),end='',flush=1)
            try:
                self.connect(addr)
            except BTLEException:
                debug and print()
                continue
            try:
                dat = self.readCharacteristic(char)
                debug and print(':',binascii.hexlify(dat))
                return dat
            except BTLEException:
                debug and print()
                continue
            finally:
                self.disconnect()
        return b'\xe0'
read_char = read_char()

class Tag(Peripheral):
    def __init__(self, addr, debug=False):
        self.addr = addr
        self.tid = -1
        Peripheral.__init__(self)
        for a in range(10):
            debug and print("Try %d to connect to %s" % (a, addr),end='',flush=1)
            try:
                self.connect(addr)
            except BTLEException:
                debug and print()
                continue
            try:
                self.tid = int(self.readCharacteristic(3)[2:], 16)
                debug and print(':',self.name)
                break
            except BTLEException:
                debug and print()
                continue
            finally:
                self.disconnect()

    @staticmethod
    def interp_locdata(tid, data):
        if not data:
            return
        data=list(data)
        ret = {'stamp':datetime.datetime.now().isoformat(), 'id':tid}
        if data[0] in (0,2):
            pos = {}
            pos['x'] = data[1] | (data[2]<<8) | (data[3]<<16) | (data[4]<<24)
            del data[1:5]
            pos['y'] = data[1] | (data[2]<<8) | (data[3]<<16) | (data[4]<<24)
            del data[1:5]
            pos['z'] = data[1] | (data[2]<<8) | (data[3]<<16) | (data[4]<<24)
            del data[1:5]
            pos['q'] = data[1]
            del data[1]
            ret['pos'] = pos
        if data[0] in (1,2):
            dist = {}
            for i in range(2, 2+data[1]*7, 7):
                thisd = {}
                thisd['d'] = data[i+2] | (data[i+3]<<8) | (data[i+4]<<16) | (data[i+5]<<24)
                thisd['q'] = data[i+6]
                dist[data[i] + (data[i+1]<<8)] = thisd
            ret['dist'] = dist
        return ret

    def read_char(self, char=0x10):
        try:
            for a in range(10):
                try:
                    #print("Try %d to read %02x from %s" % (a, char, self.addr),end='',flush=1)
                    return self.readCharacteristic(char)
                except BTLEException:
                    for b in range(10):
                        try:
                            self.disconnect()
                            self.connect(self.addr)
                        except BTLEException:
                            continue
                        break
                    continue
        finally:
            pass#print("")
        return b''

    def get_reading(self):
        return self.interp_locdata(self.tid, self.read_char(0x10))

scanner = Scanner()
devices = scanner.scan(1)
print(devices)
# Filter for Decawave modules
devices = [(x.addr,x.scanData.get(x.SHORT_LOCAL_NAME,b'')) for x in devices
            if x.scanData.get(x.SHORT_LOCAL_NAME,b'').startswith(b'DW')]
print(devices)

# Filter for tags
devices = [x for x in devices if (read_char(x[0], 0xd, 1)[0]>>5) == 2]
print(devices)

# Convert to Tag elements

devices = [Tag(a) for (a,n) in devices]
devices = [a for a in devices if a.tid >= 0]

while True:
    for x in devices:
        print(json.dumps(x.get_reading(), indent=4))

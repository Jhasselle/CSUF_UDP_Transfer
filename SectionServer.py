#Author: Jason Hasselle and Mikey Kaminsky
#Sources utilized:
#<https://stackoverflow.com/questions/2104080/how-to-check-file-size-in-python>
#<https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file>
#<https://en.wikipedia.org/wiki/User_Datagram_Protocol>
#<the mind of Professor Avery>


#!/usr/bin/env python3
import sys
import socket
import hashlib
import os


PORT = 7037
MAX_UDP_PAYLOAD = 65507
SECTION_SIZE = 32768


def md5(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()


#taken from stackoverflow <https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file>
def md5file(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def usage(program):     
    sys.exit(f'Usage: python3 {program} [FILE] ')


def main(fileName):
    
    f = open(fileName, "rb")
    fileStart = f.tell()
    f.seek(0, os.SEEK_END)
    fileSize = f.tell()
    f.seek(fileStart, os.SEEK_SET)
    numOfChunks = int(fileSize / SECTION_SIZE)
    modulus = fileSize % SECTION_SIZE

    if (modulus != 0):
        numOfChunks += 1

    #establish server
    ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ss.bind(('localhost', 7037))
    print('Server Initialized\n')
    
    while 1:
      
        data, addr = ss.recvfrom(MAX_UDP_PAYLOAD)
        f.seek(0)
        sections = ''

        if data.decode().strip() == "LIST":

            sections = f"{md5file(fileName)}\n"
 
            for x in range(numOfChunks):
                f.seek(SECTION_SIZE * x)
                if (x == (numOfChunks - 1)):
                    section = f.read(modulus)
                    sections += f"{x} {modulus} {md5(section)}\n"
                else:
                    section = f.read(SECTION_SIZE)
                    sections += f"{x} {SECTION_SIZE} {md5(section)}\n"
                
            ss.sendto(sections.encode(), addr)

        elif data.decode().strip()[:7] == 'SECTION':
            sectionNum = int(data.decode()[7:])
            f.seek(0)
            if sectionNum >= numOfChunks:
                print("Invalid Section Number")
            elif sectionNum == numOfChunks - 1:
                f.seek(SECTION_SIZE * (numOfChunks - 1))
                section = f.read(modulus)
                message = f"{md5(section)}"
            elif sectionNum == 0:
                section = f.read(SECTION_SIZE)
            else:
                f.seek(SECTION_SIZE * sectionNum)
                section = f.read(SECTION_SIZE)
            ss.sendto(section,addr)

        else:
            print("Invalid request requested, which is validly invalid.")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage(sys.argv[0])
    sys.exit(main(*sys.argv[1:]))

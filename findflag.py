#!/usr/bin/env python3

import string, binascii

def main():
	prefix = "CTF{"
	
	# ~ flag = "CTF{S1MDf0rM3!}\x00"
	flag = ["x" for x in range(15)]
	for i in range(4):
		flag[i] = prefix[i]
	flag += '\x00'
	
	while(1):
		print("Array: ",flag)
		shuffled = shuffle(flag)	
		print("Shuffled: ",shuffled)
		sum32 = add32(shuffled)
		print("Sum: ",hex(sum32))
		xorCheck = binascii.unhexlify(hex(xor(sum32))[2:])[::-1]
		print("XOR Check: ", xorCheck)
		tmp = xorCheck + b'\x00'
		if tmp == ''.join(map(str,flag)).encode():
			break
		else:
			for i in range(4, 15):
				if chr(xorCheck[i]) in string.printable:
					flag[i] = chr(xorCheck[i])
			print("New: ", flag)
		
	print("Found: ", "".join(map(str,flag)))	

def shuffle(flag):
	order = [0,13,12,10,8,4,15,3,14,9,11,5,1,7,6,2]
	shuffled = ""
	for	i in order:
		shuffled+=flag[i]
	return shuffled
	

def add32(shuffled):
	toBytes = int(binascii.hexlify(shuffled.encode('utf8')), 16)
	leet = 0x6763746613371337fee1deaddeadbeef
	multiple1 = wordify(toBytes)
	multiple2 = wordify(leet)
	
	sum32 = 0
	"""
	add and paddd instructions work differently
	Normal add is:
		dest = dest + src
	paddd however:
		dest[0:31] = dest[0:31] + src[0:31]
		dest[32:63] = dest[32:63] + src[32:63]
	If the result is too big (eg the sum of dest[0:31] and src[0:31] is bigger than 32 bits), the carry is ignored. In normal add, the carry is kept
	
	https://www.felixcloutier.com/x86/add
	https://www.felixcloutier.com/x86/paddb:paddw:paddd:paddq
	
	To get the sum, integers are broken into 32-bit word segments. Since each integer is composed of multiple 32-bit words, each can be broken up into 4 segments:
		0x6763746613371337fee1deaddeadbeef = 
			0x67637466000000000000000000000000 +
			0x133713370000000000000000 +
			0xfee1dead00000000 +
			0xdeadbeef
			
		or
														1		2			3		4
			0x6763746613371337fee1deaddeadbeef = 0x[67637466][13371337][fee1dead][deadbeef]
	
	Addition is done by pairs and getting only the low-order 32-bits:
		x = (0x67637466 + 0xffffffffff) & 0xffffffffff
		x = (0x10067637465) & 0xffffffffff # Sum is too big!
		x = 0x67637465 # Carry over bits were not included
	
	"""
	
	for m in range(4):
		sum32 += (multiple1[m] + multiple2[m]) << (96 - (32 * m)) & (0xffffffff << (96 - (32 * m)))	
	return sum32	
	
def xor(sum32):
	return 0xaaf986eb34f823d4385f1a8d49b45876 ^ sum32
	
# Break large int into 32-bit words
def wordify(largeInt):
	bits = 0xffffffff
	word1 = (largeInt >> 96) & bits
	word2 = (largeInt >> 64) & bits
	word3 = (largeInt >> 32) & bits
	word4 = largeInt & bits
	return [word1, word2, word3, word4]
	
if __name__ == "__main__":
	exit(main())

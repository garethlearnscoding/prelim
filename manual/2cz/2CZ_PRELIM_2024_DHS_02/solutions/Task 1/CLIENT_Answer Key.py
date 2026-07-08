def decompress(compressed_list, byte_rep , bytes_pattern):
    decompressed_bytes = []
    for byte in compressed_list:
        if byte == byte_rep: #going through every single byte
            num_of_bytes_to_insert = int(len(bytes_pattern)/2) #calculate how many bytes in the bytes pattern
            #print(num_of_bytes_to_insert)
            for i in range(num_of_bytes_to_insert): #inserting the bytes pattern in correctly
                decompressed_bytes.append(bytes_pattern[i*2: (i*2) + 2])
        else:
            decompressed_bytes.append(byte)
    return decompressed_bytes
	
	
	
#main program

import socket #1 mark for importing all the needed libraries

print("-------------------")
print("CLIENT OPEN")
print("-------------------")
print()

my_socket = socket.socket()
my_socket.connect(('127.0.0.1', 9999)) #1 mark for creating the socket with correct ip address and port number

compressed_data = my_socket.recv(1024).decode() #1 mark for receiving message from server program successfully + #1 mark for decoding the encrypted message (give marks if done for either compressed_data or key)
print(f"Raw compressed data received: {compressed_data}")
compressed_lst = [] 
for i in range(0, len(compressed_data), 2): #1 mark for converting the received data from string to list correctly
    compressed_lst.append(compressed_data[i:i+2])
#print(compressed_lst)

keys = my_socket.recv(1024).decode() #1 mark for receiving and decoding both messages
print(f"Key received: {keys}")

key_lst = keys.split(",")
#print(key_lst)
print()

decompressed_lst = compressed_lst
for i in range(0, len(key_lst), 2): #2 mark for calling decompress function completely (e.g. if 3 compressions done at server then must decompress 3 times) with the correct parameters
    decompressed_lst = decompress(decompressed_lst, key_lst[i], key_lst[i+1])
    #print(decompressed_lst)

print(f"Decompressed data: {decompressed_lst}")
                                  
my_socket.close() #1 mark for closing the socket

print("-------------------")
print("CLIENT CLOSED")
print("-------------------")

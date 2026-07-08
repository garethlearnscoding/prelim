def readfile(filename):
    infile = open(filename, "r")
    lines =  infile.readlines()

    bytes_lst = []
    for line in lines:
        bytes_lst.append(line.strip('\n'))

    infile.close()
    return bytes_lst
	
	
def compress(bytes_list, bytes_pattern, byte_rep):
    compressed_bytes = []
    num_of_bytes_in_pattern = int(len(bytes_pattern)/2) #to calculate how many bytes in the bytes pattern
    i = 0
    while i < len(bytes_list): #ensure going through every single byte to compare with the bytes pattern 
        compare_bytes = ""
        j = 0
        while j < num_of_bytes_in_pattern and (i+j) < len(bytes_list): #to form the compare_bytes of the same byte length to compare with bytes pattern but also to ensure do not go out of range of the list
            compare_bytes = compare_bytes + bytes_list[i + j]
            j = j + 1
        #print(compare_bytes)
        if compare_bytes == bytes_pattern: #for the processing when a byte_pattern is found
            compressed_bytes.append(byte_rep)
            i = i + num_of_bytes_in_pattern
        else: #if no byte pattern is found
            compressed_bytes.append(bytes_list[i])
            i = i + 1
    return compressed_bytes
	

	
#main program
import socket 

print("-------------------")
print("SERVER OPEN")
print("-------------------")
print()

listen_socket = socket.socket() 
listen_socket.bind(('127.0.0.1', 9999)) 
listen_socket.listen()

print("Waiting for client request")
print("---------------------------")
new_socket, addr = listen_socket.accept()

original_lst = readfile("Audio.txt")
print(f"original data: {original_lst}")
print()

compressed_data = original_lst
keys = ""
#at least one compression must be done
while True:
        
    bytes_pattern = input("Enter the bytes pattern to be replaced: ") #636485, 6F2A6F, followed by 8385868788
    byte_rep = input("Enter the value to replace the above bytes pattern: ") #C0, C1 followed by C2
    compressed_data = compress(compressed_data, bytes_pattern, byte_rep)
    keys = keys + byte_rep + "," + bytes_pattern

    continue_input = input("Do you want to continue compressing? [Y/N]: ") 
    print()
    if continue_input == "N":
        break
    else:
        keys = keys + ","

print(f"compressed_data: {compressed_data}")
string_compressed_data = ''.join(compressed_data) #This is to convert the data from a list into a single string
encoded_compressed_data = string_compressed_data.encode() 
new_socket.sendall(encoded_compressed_data)
print(f"Compressed Data (String): {string_compressed_data}")
print("Compressed Data sent to client successfully")
print()

encoded_keys = keys.encode()
new_socket.sendall(encoded_keys)
print(f"Key: {keys}")
print("Key sent to client successfully")
print()

new_socket.close()

listen_socket.close()

print("-------------------")
print("SERVER CLOSED")
print("-------------------")

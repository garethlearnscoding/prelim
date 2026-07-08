# Sample code for Task 2 - timeit module usage
# You will need to import the timeit module.
import timeit

# Record the start time before the start of the operation.
# timeit.default_timer() gives us the most accurate timestamp available.
start_time = timeit.default_timer()

# Place the code to be timed in this space.

# Record the end time immediately after the operation completes.
end_time = timeit.default_timer()

# Calculate the total execution time by finding the difference
# between the two timestamps. The result is expressed in seconds.
time_difference = end_time - start_time

#=======================================================================
# Sample code for Task 4 - hashlib module usage
# You will need to import the hashlib module to use SHA-3 hashing.
import hashlib

# Provide a string to be hashed.
string = "Computing"

# The following line of code computes the SHA-3 hash of the string and
# returns the hash as a hexadecimal string.
sha3_hash = hashlib.sha3_256(string.encode()).hexdigest()
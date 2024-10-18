import os
import hashlib
import gmpy2
import time
import sys

import sympy


def nums_gen():
    random_string = os.urandom(1).hex()
    sha256_hash = hashlib.sha256(random_string.encode()).hexdigest()
    binary_string = ''.join(f'{int(c, 16):04b}' for c in sha256_hash)
    chunks = [binary_string[i:i + 16] for i in range(0, len(binary_string), 16)]
    decimal_integers = [int(chunk, 2) for chunk in chunks]
    return decimal_integers

def int_to_binary_sequence(n):
    binary_string = bin(n)[2:]
    return binary_string
def CRT_AGGREGATE_and_DECODE(numbers):
    nums = []
    for i in numbers:
        nums.append(gmpy2.mpz(i))
    LPSeq=[]
    for i in numbers:
        LPSeq.append(gmpy2.mpz(sympy.nextprime(i)))
    #LPSeq = [gmpy2.mpz(66809),gmpy2.mpz(67261),gmpy2.mpz(68071),gmpy2.mpz(69011)]
    print(nums)
    S = gmpy2.mpz(0)
    Q = gmpy2.mpz(1)
    for i in LPSeq:
        Q = gmpy2.mul(i, Q)
    for i in range(len(nums)):
        temp1 = gmpy2.mpz(gmpy2.div(Q, LPSeq[i]))
        temp2 = gmpy2.invert(temp1, LPSeq[i])
        temp1 = gmpy2.mul(temp1, nums[i])
        temp1 = gmpy2.mul(temp1, temp2)
        S = gmpy2.add(S, temp1)
    S=gmpy2.mod(S,Q)
    ans = []
    for i in range(len(LPSeq)):
        ans.append(gmpy2.mpz(gmpy2.mod(S, LPSeq[i])))
    print(ans)
    return S,ans

t=0
for i in range(1000):
    a = nums_gen()
    j = 0
    while j + 4 <= len(a):
        numbers = a[j:j + 4]
        start = time.time()
        S,ans = CRT_AGGREGATE_and_DECODE(numbers)
        #print(len(int_to_binary_sequence(S)))
        end = time.time()
        t += end - start
        j += 4
print(f'The total time used is: ',t,' seconds.')



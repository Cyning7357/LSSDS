import gmpy2
import sympy
import sys
import hashlib
numbers=[13, 20, 9, 16, 35,24,18,22,21]
primes=[17, 53, 31, 41, 47,59,61,67,71]
nums=[]
for i in numbers:
    nums.append(gmpy2.mpz(i))
LPSeq=[]
for i in primes:
    LPSeq.append(gmpy2.mpz(i))
S=gmpy2.mpz(0)
Q=gmpy2.mpz(1)
for i in LPSeq:
    Q=gmpy2.mul(i,Q)
for i in range(len(nums)):
    temp1=gmpy2.mpz(gmpy2.div(Q,LPSeq[i]))
    temp2=gmpy2.invert(temp1,LPSeq[i])
    temp1=gmpy2.mul(temp1,nums[i])
    temp1=gmpy2.mul(temp1,temp2)
    S=gmpy2.add(S,temp1)
ans=[]
for i in range(len(LPSeq)):
    ans.append(gmpy2.mpz(gmpy2.mod(S,LPSeq[i])))
print('原数组为：')
print(nums)
print('聚合结果为：')
print(S)
print('解码结果为：')
print(ans)
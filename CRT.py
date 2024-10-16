from sympy import nextprime
def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    gcd, x, y = extended_gcd(b, a % b)
    return gcd, y, x - (a // b) * y
def inverse_modulo(x, p):
    gcd, inverse, _ = extended_gcd(x, p)
    if gcd != 1:
        raise ValueError("The inverse does not exist.")
    return inverse % p
def CRT_Aggregation (nums,n): #aggregate n numbers in nums
    LPSeq=[]
    S=0
    Q=1
    LPSeq.append(89)
    for i in range(n):
        LPSeq.append(nextprime(LPSeq[i]))
    for i in range(n):
        Q*=LPSeq[i]
    for i in range(n):
        temp = nums[i] * (Q/LPSeq[i]) * inverse_modulo(Q/LPSeq[i],LPSeq[i])
        S+=temp
    S %= Q
    return S,LPSeq

def CRT_inverse_operation (LPSeq,S,n):
    ans=[]
    for i in range(n):
        ans.append(S%LPSeq[i]-1)
    return ans

#testing
nums=[11,24,33,4,78,90,15]
S,LPSeq=CRT_Aggregation(nums,7)
print(S)
print(LPSeq)
print(nums)
print(CRT_inverse_operation(LPSeq,S,7))





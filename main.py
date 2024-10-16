from basicblockchains_ecc import elliptic_curve as EC
import hashlib
import random
from secrets import randbits
from datetime import datetime
from Crypto.Cipher import Salsa20

def str_xor(str1, str2):
    ans = ''
    for i in range(len(str1)):
        if str1[i] != str2[i]:
            ans += '1'
        else:
            ans += '0'
    return ans
#point to string
def pts (P):
    return str(P[0])+str(P[1])

#random message generation
def rmg(n):
    msg = ''
    for i in range(n):
        msg += random.choice(['0', '1'])
    return msg


class KGC(object):

    def __init__(self,n, m):
        self.parameters_gen(n, m)

    def parameters_gen(self, n, m):
        self.curve = EC.secp256r1()
        self.P = self.curve.generator
        self.q = self.curve.order
        self.__msk = randbits(256) % self.q
        self.P_pub = self.curve.scalar_multiplication(self.__msk, self.P)
        self.ID_length = n
        self.CT_length = m
        self.intervals=1440



    def H1(self, PID, point_1, point_2, point_3):
        h = hashlib.sha512()
        h.update(PID.encode() + pts(point_1).encode() + pts(point_2).encode() + pts(point_3).encode())
        return int(h.hexdigest(), 16) % self.q

    def H2(self, a, b, c, bits):
        h = hashlib.sha512()
        temp = a.encode() + b.encode() + c.encode()
        h.update(temp)
        val = int(h.hexdigest(), 16)
        binay_str = bin(val)
        return binay_str[2:bits + 2]

    def H3(self, a, b, c, d, e, f):
        h = hashlib.sha512()
        temp = a.encode() + b.encode() + c.encode() + d.encode() + e.encode() + f.encode()
        h.update(temp)
        val = int(h.hexdigest(), 16)
        val = val % self.q
        return val

    def H4(self, str, bits):
        h = hashlib.sha512()
        temp = str.encode()
        h.update(temp)
        val = int(h.hexdigest(), 16)
        binay_str = bin(val)
        return binay_str[2:bits + 2]

    def _partial_key_compute(self, RID, X):
        p_in = str(self.P_pub[0]) + str(self.P_pub[1])
        a = randbits(256) % self.q
        A = self.curve.scalar_multiplication(a, self.P)
        A_in = str(A[0]) + str(A[1])
        X_in = str(X[0]) + str(X[1])
        h_s_1 = self.H1(RID, X_in, A_in, p_in)
        y = a + self.__msk * h_s_1
        t = datetime.now()
        return (A, y, t)


class public_para(object):
    def __init__(self, KGC):
        self.sys = KGC

class User(object):
    def __init__(self, para):
        self.psk = randbits(256) % para.sys.q
        self.RID = rmg(para.sys.ID_length)
        self.ppk = para.sys.curve.scalar_multiplication(self.psk, para.sys.P)
        self.alpha=randbits(256)
        self.beta=randbits(256)

    def full_key_compute(self, para, partial_key):
        h_s_2 = para.sys.H1(partial_key[0], self.ppk, partial_key[2], para.sys.P_pub)
        left = para.sys.curve.scalar_multiplication(partial_key[3], para.sys.P)
        right = para.sys.curve.add_points(partial_key[2], para.sys.curve.scalar_multiplication(h_s_2, para.sys.P_pub))
        if left != right:
            print("ERROR: partial key incorrect")
            return
        self.fsk = (self.psk, partial_key[3])
        self.fpk = (self.ppk, partial_key[2])

    def one_to_one_signcryption(self, Msg, Receiver, para):
        u = randbits(256) % para.sys.q
        U = para.sys.curve.scalar_multiplication(u, para.sys.P)
        RID_r = Receiver.RID
        P_pub = para.sys.P_pub
        X_r = Receiver.fpk[0]
        A_r = Receiver.fpk[1]
        h_r_1 = para.sys.H1(RID_r, X_r, A_r, P_pub)
        temp = para.sys.curve.add_points(para.sys.curve.add_points(X_r, A_r),
                                         para.sys.curve.scalar_multiplication(h_r_1, P_pub))
        W_r = para.sys.curve.scalar_multiplication(u, temp)
        PID_r = Receiver.PID
        B_r = para.sys.H3(PID_r, U, W_r, len(Msg))
        c_r = str_xor(B_r, Msg)
        T = str(datetime.now())
        h_s = para.sys.H5(self.RID, self.fpk[0], self.fpk[1], Msg, U, T)
        val = u + h_s * (self.fsk[0] + self.fsk[1])
        return (self.RID, val, c_r, U, T)


    def one_to_many_unsigncrypt(self, Ciphertext, para, fpk):
        U = Ciphertext[3]
        W = para.sys.curve.scalar_multiplication((self.fsk[0] + self.fsk[1]), U)
        B = para.sys.H3(self.PID, U, W)
        s = ''
        for element in Ciphertext[2]:
            s += element
        h_s = para.sys.H5(Ciphertext[0], fpk[0], fpk[1], s, U, Ciphertext[4])
        h_2_s = para.sys.H2(Ciphertext[0], fpk[0], fpk[1], para.sys.P_pub)
        left = para.sys.curve.scalar_multiplication(Ciphertext[1], para.sys.P)
        right = para.sys.curve.add_points(para.sys.curve.add_points(fpk[0], fpk[1]),
                                          para.sys.curve.scalar_multiplication(h_2_s, para.sys.P_pub))
        temp1 = para.sys.curve.scalar_multiplication(h_s, right)
        right = para.sys.curve.add_points(temp1, U)
        if right != left:
            print("ERROR")
            return
        mark = para.sys.H4(B, U, W)
        c = ''
        for element in Ciphertext[2]:
            if mark == element[:para.sys.msg_length]:
                c = element[para.sys.msg_length:]
        m = str_xor(c, B)
        return m

    def EncryptionKG(self, para):
        lkset=[]
        rkset=[]
        DT= str(datetime.now().date())
        lk_start=para.sys.H4(str(self.alpha)+DT+'1')
        lkset.append(lk_start)
        for i in range(1,para.sys.intervals):
            lkset.append(para.sys.H4(lkset[i-1]))
        rk_end=para.sys.H4(str(self.beta)+DT+str(para.sys.intervals))
        rkset.append(rk_end)
        for i in range(1,para.sys.intervals):
            rkset.append(para.sys.H4(rkset[i-1]))
        rkset=rkset[::-1]
        encset=[]
        for i in range(len(rkset)):
            encset.append(str_xor(rkset[i],lkset[i]))
        return encset

    def Encryption(self,encset,msgset):
        ctset=[]
        for i in range(0,len(msgset)):
            assert len(encset[i]) == 64
            binary_data = int(encset[i], 2).to_bytes(32, byteorder='big')
            non = binary_data[:8]
            key = binary_data[8:]
            cipher = Salsa20.new(key=key,nonce=non)
            ct=non+cipher.encrypt(msgset[i])
            ctset.append(ct)
        return ctset

    def DecryptionKG(self,time_range,lk_start,rk_end,para):
        lkset = []
        rkset = []
        lkset.append(lk_start)
        for i in range(1,len(time_range)):
            lkset.append(para.sys.H4(lkset[i-1]))
        rkset.append(rk_end)
        for i in range(1,len(time_range)):
            rkset.append(para.sys.H4(rkset[i-1]))
        rkset = rkset[::-1]
        decset = []
        for i in range(len(rkset)):
            decset.append(str_xor(rkset[i], lkset[i]))
        return decset

    def Decryption(self,ctset,decset):
        msgset=[]
        for i in range(ctset):
            assert len(decset[i]) == 64
            binary_data = int(decset[i], 2).to_bytes(32, byteorder='big')
            nonce = binary_data[:8]
            key = binary_data[8:]
            decipher = Salsa20.new(key=key, nonce=nonce)
            decrypted_nonce = ctset[i][:8]
            encrypted_data = ctset[i][8:]
            decrypted_plaintext = decipher.decrypt(encrypted_data)
            msgset.append(decrypted_plaintext)
        return msgset
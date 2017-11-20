#223272c1-d591-4f07-afb5-cba7cfb05f34 <- this is a gaid

#8-4-4-4-12

from hashlib import md5
from numpy.random import random_integers

def rd_formatted_to_max(n):
    digits=len(str(n))
    format_str = '0'+str(digits)+'d'
    return format(random_integers(n),format_str)

def one_rd_gaid():
    #random 19 digit number, leading zeroes are legal
    rd = lambda : rd_formatted_to_max(2**62)    
    gaid_unsegmented = ez_md5(rd())
    gaid = str_to_gaid_format(gaid_unsegmented)

    return gaid

def ez_md5(xx):
    str_to_uni = lambda x: str(x).encode('utf-8','ignore')    
    md5_of_str = lambda y: md5(str_to_uni(y)).hexdigest()
    return md5_of_str(xx)    

def str_to_gaid_format(sss):
    sss = str(sss)
    sss = sss[:32] if len(sss) >= 32 else sss + (32-len(sss))*'a'        
    return sss[0:8]+'-'+sss[8:12]+'-'+sss[12:16]+'-'+sss[16:20]+'-'+sss[20:32]

def many_gaids(l):
    res = list(map(str_to_gaid_format,map(ez_md5,range(l))))
    #assert md5 was injective on this range:
    assert(len(res)==l)

    return list(map(str_to_gaid_format,map(ez_md5,range(l))))

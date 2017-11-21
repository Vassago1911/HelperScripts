#223272c1-d591-4f07-afb5-cba7cfb05f34 <- this is a gaid

#8-4-4-4-12

from hashlib import md5
from numpy.random import random_integers
import random
import pandas

import sqlalchemy
#import pymysql
#(host='10.0.26.75', port=3306, user='mcoins-read', passwd='VIohkOuZQNaQmThz0F0Apwvu3jaG4waI', db='mcoins')
#(host='10.10.1.90', port=3306, user='mcoins', passwd='pheereeth4pooph2eapheiyi0EeD5aeL', db='mcoins')

#engine = sqlalchemy.create_engine('mysql+pymysql://mcoins-read:VIohkOuZQNaQmThz0F0Apwvu3jaG4waI@10.0.26.250:3306')
#engine_beta = sqlalchemy.create_engine('mysql+pymysql://mcoins:pheereeth4pooph2eapheiyi0EeD5aeL@10.10.1.90:3306')

#connection = engine.connect(); connection_beta = engine_beta.connect()

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
    res = list(map(str_to_gaid_format,map(ez_md5,range(1024,l+1024))))
    #assert md5 was injective on this range:
    assert(len(res)==l)

    return res

def gen_timestamps(n, day = 5, mth = 3):
    import datetime
    return [str(datetime.datetime(2017,mth,day,21,int((x/n)*60),random_integers(59))) for x in range(n)]

def gaidxtimestamp(n, day = 5, mth = 3):
    return list(zip(random.sample(many_gaids(1024*(1+int(n/1024))),n),gen_timestamps(n, day, mth)))

def unknown_gaids(l):
    #generate gaids we don't know in AppLike_prod or _beta
    res = many_gaids(2*l)
    query_tuple = str(tuple(res))

    query = 'select ud.advertiserId gaid from UserDevice ud where ud.advertiserId in '+query_tuple +';'

    df = pandas.read_sql_query(query, connection)
    df2 = pandas.read_sql_query(query, connection_beta)

    d = pandas.concat([df,df2])

    res = [x for x in res if x not in list(d.gaid)]

    return res

def ins_a_list(l):
    return insert_rows(*l)

def insert_rows(nr, cid, cpi_value, cpi_currency, cpi_valueEur, day=5, mth=3):
    def reorder_tuples(ll):
        res = [tuple([l[0][0],l[1][1],l[1][0],l[0][1],l[0][2],l[0][3],l[0][4],l[1][0],l[0][5]]) for l in ll]
        return res

    gt = gaidxtimestamp(nr, day, mth)
    xs = nr*[[cid, cpi_value, cpi_currency, cpi_valueEur, 'a', 'android'],]
    
    res = reorder_tuples(zip(xs, gt))   

    return str(res).replace('[','').replace(']','')

def insert_list_of_rows(ll):
    #ll = [[nr, cid, cpi_value, cpi_currency, cpi_valueEur, (day, mth)] ..]
    res = map(ins_a_list, ll)
    zz = 'insert into CampaignAppsPostback (campaign_id, createdAt, mobileId, cpi_value, cpi_currency, cpi_valueEur, source, userAdvertiserId, platform) \n values \n'
    for x in res:
        zz = zz + x + ', '

    zz = zz.replace('), (', '),\n(')

    return zz[:-2]

def print_insert(ll):
    print(insert_list_of_rows(ll))

def k_tuples_lt_10(k,mx=10):
    if k==1:
        return [[i,] for i in range(0,mx+1)]
    else:
        return [(i,*l) for i in range(0,mx+1) for l in k_tuples_lt_10(k-1,mx)]


def solve_cpispbs_from_countrev(rev, cnt, cpis):
    cpis = cpis
    cpis.sort()

    k = len(cpis) - 1    

    candidates = k_tuples_lt_10(k,min(cnt,1))
    #generate only linear combinations with sum(comb) = cnt, then I only need to hit rev
    candidates = [(*z,cnt-sum(z)) for z in candidates if cnt-sum(z)>=0]

    for z in candidates:
        comb = zip(z,cpis)
        res = 0
        for c in comb:
            res += c[0]*c[1]
            if(res > rev):
                break
        if res==rev:
            res = list(filter(lambda x: x[0]!=0,list(zip(z, cpis))))
            return res
    
    print('no solution')     

#print(insert_list_of_rows([(3,313,2,'USD',1.78),(2,49202,3,'USD',2.65)]))

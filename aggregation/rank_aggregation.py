import math
# Cynthia Dwork, Ravi Kumar, Moni Naor, and D. Sivakumar.
# Rank aggregation methods for the Web.
# In Proceedings of the 10th international conference on World Wide Web (WWW '01).
# 2001.
def mc4(rankings: list[list[str]]) -> list[str]:
    idx2name:list[str] = rankings[0]
    n = len(idx2name)
    name2idx:dict[str,int] = { idx2name[i]:i for i in range(n)}
    M:list[list[float]] = [[]]*n
    for i in range(n):
        M[i] = [0.0] * n
    # fill the transition matrix
    for i in range(len(rankings)):
        for j in range(len(rankings[i])):
            jj = name2idx[rankings[i][j]]
            for k in range(j+1,len(rankings[i])):
                kk = name2idx[rankings[i][k]]
                M[jj][kk] = M[jj][kk] + 1.0
                M[kk][jj] = M[kk][jj] - 1.0
    for i in range(n):
        ii = 1.0
        for j in range(n):
            if M[i][j] < 0:
                M[i][j] = 1.0 / float(n)
                ii = ii - 1.0 / float(n)
            else:
                M[i][j] = 0.0
        M[i][i] = ii

    # x^TM^t
    e = [1.0]*n

    T = 10
    for t in range(T):
        ee = [0.0]*n
        for i in range(n):
            sum = 0.0
            for j in range(n):
                sum = sum + (e[j] * M[j][i])
            ee[i] = sum
        e = [i for i in ee]
    # rank by stationary distribution
    p=[]
    for i in range(n):
        p.append([e[i],idx2name[i]])
    p.sort(reverse=True)
    retval = [x[1] for x in p]
    return retval
#
# Borda Count
#

def borda(rankings: list[list[str]]) -> list[str]:
    counts = {}
    n = 0
    for i in range(len(rankings)): 
        if n == 0:
            n = len(rankings[i])
        for j in range(len(rankings[i])):
            name = rankings[i][j]
            count_ij = n-j
            if name not in counts:
                counts[name] = 0
            counts[name] = counts[name] + count_ij
    counts_vector = []
    for k,v in counts.items():
        counts_vector.append([v,k])
    counts_vector.sort(reverse=True)
    retval = [ x[1] for x in counts_vector ]
    return retval

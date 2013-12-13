""" Hamming related utilities.

"""


def distance(a, b):
    """ calculate Hamming distance between integers 'a' and 'b'.

    """

    _xor = a ^ b
    dist = 0
    while _xor:
        dist += 1
        _xor &= _xor - 1

    return dist



def hamming_neighbors(n, dist, numBits):
    """Returns list of numbers that are given hamming distance away                                                                        
    from an integer.                                                                                                                       
                                                                                                                                           
    n : an integer                                                                                                             
    dist : Hamming distance                                                                                                                
    bits : number of bits of neighbors                                                                                                     

    ## from python recipe 578423-hamming-neighbors
    ## PC I think there is a bug

    """

    if dist < 0:
        raise Exception, 'Invalid distance'
    onesMask = int('1'*numBits, 2)

    # Cur array maintains the invariant that for some dist d,                                                                                  
    # Cur[i] holds all numbers that that are d distance                                                                                    
    # away from lower i-bits of n                                                                                                          

    # dist == 0                                                                                                                            
    Cur = [[n % (1 <<  _)] for _ in range(numBits+1)]
    # dist > 0
    for d in range(1, dist+1):
        Prev = Cur
        Cur = [[] for _ in range(numBits+1)]
        for i in range(d, numBits+1):
            # n's i-th bit and its inversion                                                                                               
            iBit = n & (1<<i-1)
            iBitInv = iBit ^ (1<<i-1)
            Cur[i] = [iBitInv + x for x in Prev[i-1]] + \
                     [iBit + x for x in Cur[i-1]]
    return Cur[numBits]



def get_bit(byte, pos):
    """ return bit corresponding to position 'pos' in 'byte'

    """
    
    return (byte & (1 << pos)) >> pos



def count_set_bits(i):
    """ return count of bits that are set to 1.

    """

    c = 0
    while i:
        c += i & 1
        i = i >> 1

    return c



def hamming_code(w):

    """ takes a 4 bit integer and returns an 8 bit extended hamming
        code.

        This is going to be used to prepopulate a table so it does not
        need to be efficient.

    """

    w3 = get_bit(w, 3)
    w2 = get_bit(w, 2)
    w1 = get_bit(w, 1)
    w0 = get_bit(w, 0)
    p0 = w3 ^ w2 ^ w1
    p1 = w3 ^ w2 ^ w0
    p2 = w2 ^ w1 ^ w0
    p3 = w3 ^ w2 ^ w1 ^ w0 ^ p0 ^ p1 ^ p2 

    return (p0, p1, p2, p3)


def find_vectors():

    """ find a set of 16 8bit vectors which have hamming distance at
        least 3 and have as many bit transitions as possible.

    """

    v = [170, 85] # binary 10101010 and 01010101
    for i in range(256):
        s = count_set_bits(i)
        if s > 6 or s < 2:
            continue
        for j in v:
            h = distance(i, j) 
            if h < 3:
                break
        else:
            v.append(i)

    v.sort()
    out = v[:16]
    
    return out


def reverse_map():
    """ for each possible received 8bit word find closest vector from
        set of vectors calculated by find_vectors(). Set value to 16
        for vectors that do not have a single minimum closest match.

    """
    
    v = find_vectors()
    out = []
    for i in range(256):
        distances = [(distance(i, word), j) for (j, word) in enumerate(v)]
        distances.sort()
        min_d = distances[0]
        if min_d[0] == distances[1][0]:
            out.append(16)
        else:
            out.append(min_d[1])
    
    return out





if __name__ == '__main__':
    print "BASE VECTORS:"
    print find_vectors()
    print "REVERSE MAP:"
    print reverse_map()

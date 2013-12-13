""" 16 bit hash based on Linear Congruential Generator

    we will use 17 for both multiplier and constant (see Full-Period
    Theorem: Hull and Dobell, 1966).

    No claim is made on its statistical properties.

"""


def hash17(s):
    """ given a byte array s return a 16 bit hash. 
    
    """
    
    

    hash = 17
    div = 2**16
    for c in s:
        hash = (((hash << 4) + hash) ^ c) % div

    return hash

### D.J.B hash

def hash33(s):
    """ given a byte array 's' return a 32 bit hash. 
    
    """

    hash = 5381
    div = 2**32
    for c in s:
        hash = (((hash << 5) + hash) ^ c) % div

    return hash



def test():

    part = 'uietcasting'
    
    hashes = []
    for i in range(256):
        s = [i] + [ord(i) for i in part]
        h = hash17(s)
        if h in hashes:
            print 'Collision!'

        hashes.append(h)


if __name__ == '__main__':
    test()

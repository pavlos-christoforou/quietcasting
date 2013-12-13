""" provides a simple but insecure message authentication code HMAC
    which is good enough for protecting against the majority of
    attacks we envision.

"""


from quietcasting.lib.hash import hash17 as hash_function
from quietcasting.lib.utils import s_to_a
from quietcasting.lib.utils import a_to_s
import array




def hmac(key, challenge, message, as_array = False):

    """ 'key' is a 16 bytes shared secret key.

        'challenge' is a 4 bytes challenge code which must be used
        only once.

        'message' is the message to authenticate.

        returns a 2 byte hmac code.

    """

    inner_key = array.array('B', [54^ord(i) for i in key])    
    outer_key = array.array('B', [92^ord(i) for i in key])
    _hash = hash_function(inner_key + s_to_a(message))
    tmp = []
    for i in range(4):
        tmp.append(_hash % 256)
        _hash >>= 8
    tmp.reverse()
    inner_hash = array.array('B', tmp)
        
    hmac = hash_function(outer_key + inner_hash)

    if as_array:
        tmp = []
        for i in range(4):
            tmp.append(_hash % 256)
            _hash >>= 8
            tmp.reverse()
        hmac = array.array('B', tmp)
    
    return hmac
    


def test():

    part = 'uietcasting'
    
    hashes = []
    for i in range(256):
        msg = chr(i) + part
        out = hmac('secret key', str(1)*4, msg) 
        print out


if __name__ == '__main__':
    test()

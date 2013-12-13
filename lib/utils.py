""" Utilities.

"""

## must be a multiple of 8
MAX_LENGTH = 48

import array



def s_to_a(msg):
    """ convert 'msg' string to array.

    """

    return array.array('B', msg)


def a_to_s(msg):
    """ convert 'msg' array to string.

    """

    return ''.join([chr(i) for i in msg])



def pad(msg, max_length = (MAX_LENGTH-1)):

    """ given a 'msg':

        truncate if packet is longer than MAX_LENGTH - 1 bytes.

        if shorter than MAX_LENGTH - 1 bytes repeat message to reach
        length MAX_LENGTH -1 .

        prefix message with a single byte denoting the length.
        
        total returned length is MAX_LENGTH bytes

    """

    ## copy msg
    msg = msg[:]

    length = len(msg)
    _max = max_length
    length = min(_max, length)

    while len(msg) < _max:
        msg += msg

    msg = msg[:_max]
    msg.insert(0, length)
    return msg


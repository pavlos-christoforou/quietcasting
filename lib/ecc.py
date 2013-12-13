""" The QuietCasting error correcting code. Simple but effective.

    The encoding expands a 48 byte message to a 48x4 encoded message. 

    The encoding can correct:

     - a sequence/burst of up to 192 error bits occuring anywhere in
       the received message.
    
     - two sequences/bursts of up to 96 error bits each occuring
       anywhere in the received message.
       
     - any single error bit (and frequently 2 bit errors) occuring
       anywhere in a single received 8bit word.


    For use in low power CPU applications.

    All message/code inputs or output must be of type array.array('B')

"""

from quietcasting.utils import pad
from quietcasting.utils import s_to_a
from quietcasting.utils import a_to_s

import array

### globals
_debug  = 0

BASE_VECTORS = array.array('B', [3, 12, 22, 25, 37, 48, 63, 74, 85, 102, 105, 115, 124, 143, 170, 192])
REVERSE_MAP = array.array('B', [16, 0, 0, 0, 1, 4, 2, 0, 1, 3, 7, 0, 1, 1, 1, 13, 5, 3, 2, 0, 2, 8, 2, 2, 3, 3, 16, 3, 1, 3, 2, 6, 5, 4, 16, 0, 4, 4, 9, 4, 16, 10, 14, 16, 1, 4, 16, 6, 5, 5, 5, 11, 5, 4, 2, 6, 5, 3, 16, 6, 12, 6, 6, 6, 15, 16, 7, 0, 16, 8, 9, 16, 7, 10, 7, 7, 1, 16, 7, 16, 16, 8, 16, 11, 8, 8, 2, 8, 16, 3, 7, 16, 12, 8, 16, 16, 16, 10, 9, 11, 9, 4, 9, 9, 10, 10, 7, 10, 12, 10, 9, 16, 5, 11, 11, 11, 12, 8, 9, 11, 12, 10, 16, 11, 12, 12, 12, 6, 15, 16, 16, 0, 16, 16, 16, 13, 16, 16, 14, 13, 1, 13, 13, 13, 16, 3, 2, 0, 2, 8, 2, 16, 3, 3, 14, 16, 1, 16, 16, 13, 16, 4, 14, 16, 4, 4, 16, 16, 14, 16, 14, 14, 16, 16, 14, 13, 5, 5, 16, 11, 5, 4, 2, 6, 16, 3, 14, 16, 12, 6, 16, 6, 15, 15, 15, 16, 15, 16, 16, 13, 15, 16, 7, 16, 16, 13, 16, 13, 15, 16, 15, 11, 16, 8, 2, 8, 15, 3, 7, 16, 12, 8, 16, 13, 15, 16, 16, 11, 16, 4, 9, 9, 16, 10, 14, 16, 12, 10, 16, 13, 16, 11, 11, 11, 12, 8, 9, 11, 12, 10, 14, 11, 12, 12, 12, 6])


## must be a multiple of 8
MAX_LENGTH = 48




def bit_transpose(msg):

    """ transpose bits of 'msg'
    
    """

    length = MAX_LENGTH

    assert len(msg) == length

    div = length/8
    assert length % 8 == 0, "length must be a multiple of 8"
    out = array.array('B', [0] * length)
    
    for shift_i in range(8):
        shift = 128 >> shift_i
        for i in range(length):
            c = msg[i]
            pos = shift_i*div + (i/8)
            tmp = (c & shift) << 8
            out[pos] |= tmp >> ((i % 8) + 8 - shift_i)

    return out



def reverse_bit_transpose(msg):

    """ reverse transpose bits of 'msg'
    
    """

    length = MAX_LENGTH

    assert len(msg) == length

    div = length/8
    assert length % 8 == 0, "length must be a multiple of 8"
    out = array.array('B', [0] * length)

    for i in range(length):
        c = msg[i]
        for shift_i in range(8):
            shift = 128 >> shift_i
            pos = (i%6) * 8 + shift_i
            tmp = (c & shift) << 8
            out[pos] |= tmp >> ((i / 6) + 8 - shift_i)

    return out




def ecc_encode(msg, pad = False):

    """ encode message 'msg' which must be of length MAX_LENGTH:
          
          1. pad msg if 'pad' is True
    
          2. Map each 4bit word of 'msg' to one of the base vectors.

          3. Transpose and repeat message twice.

        The encoding attempts to map nicely to current physical low
        power devices which generally support packet handling and
        where packet lengths are generally limited to 255 bytes (TI:
        CC1101 and CC1120 etc, Freescale RF MCU, HopeRF RFM69W,
        Silicon Labs RF MCU etc). 

    """

    if pad:
        msg = pad(msg)

    length = MAX_LENGTH
    assert len(msg) == length

    div = length / 8

    enc_msg_high = []
    enc_msg_low = []
    for c in msg:
        enc_msg_high.append(BASE_VECTORS[c >> 4])
        enc_msg_low.append(BASE_VECTORS[c % 16])

    ## transpose
    tr_msg_high = bit_transpose(enc_msg_high)
    tr_msg_low = bit_transpose(enc_msg_low)

    ## duplicate
    out = []
    for i in range(8 * 2):
        _from = i * div
        _to = (i+1) * div
        out.extend(tr_msg_high[_from:_to])
        out.extend(tr_msg_high[_from:_to])
        out.extend(tr_msg_low[_from:_to])
        out.extend(tr_msg_low[_from:_to])
    
    return s_to_a(out)
            


def ecc_decode(received_code):

    """ decode 'received_code'.

        'received_code' is the set of MAX_LENGTH * 4 bytes making up
        the received packet.

        the optimal decoded message is the one maximizing the
        posterior probability given the received code using Bayes
        rule. An iterative algorithm may be appropriate here but to
        keep things simple we will follow a simpler scheme where we
        just use the reverse map to detect the most probable message
        word.

    """

    length = MAX_LENGTH * 4
    div = MAX_LENGTH / 8

    assert len(received_code) == length
    
    ## break duplicate data into 2 parts and each part into high bit
    ## and low pit parts

    code_1_high = []
    code_1_low = []
    code_2_high = []
    code_2_low = []
    while received_code:
        (head, received_code) = (received_code[:div], received_code[div:])
        code_1_high.extend(head)
        (head, received_code) = (received_code[:div], received_code[div:])
        code_2_high.extend(head)
        (head, received_code) = (received_code[:div], received_code[div:])
        code_1_low.extend(head)
        (head, received_code) = (received_code[:div], received_code[div:])
        code_2_low.extend(head)
    
    ## transpose
    tr_code_1_high = reverse_bit_transpose(code_1_high)
    tr_code_1_low = reverse_bit_transpose(code_1_low)
    tr_code_2_high = reverse_bit_transpose(code_2_high)
    tr_code_2_low = reverse_bit_transpose(code_2_low)

    
    # decode
    dec_code = []
    has_error = False
    for i in range(MAX_LENGTH):
        high1 = REVERSE_MAP[tr_code_1_high[i]] 
        low1 = REVERSE_MAP[tr_code_1_low[i]] 
        high2 = REVERSE_MAP[tr_code_2_high[i]] 
        low2 = REVERSE_MAP[tr_code_2_low[i]] 
        c = 0
        ## do high bits
        if high1 < 16 and high2 < 16:
            if high1 == high2:
                c = high1
            else:
                has_error = True

        elif high1 < 16 and high2 == 16:
            c = high1

        elif high1 == 16 and high2 < 16:
            c = high2
        
        else:
            has_error = True
        
        c <<= 4

        ## do low bits
        if low1 < 16 and low2 < 16:
            if low1 == low2:
                c |= low1
            else:
                has_error = True

        elif low1 < 16 and low2 == 16:
            c |= low1

        elif low1 == 16 and low2 < 16:
            c |= low2
        
        else:
            has_error = True
        
        dec_code.append(c)

    return (has_error, s_to_a(dec_code))
        






def test():
    import random

    msg = pad(s_to_a('Hello QuietCasting'))
    assert msg[0] == 18
    assert len(msg) == MAX_LENGTH

    tr_msg = bit_transpose(msg)
    assert reverse_bit_transpose(tr_msg) == msg

    print 'Encoding ...'
    enc = ecc_encode(msg)
    print enc

    print 'Corrupting message (random) ...'
    rec = []
    for c in enc:
        e = 0
        for i in range(8): 
            r = random.randint(0,999)
            if r < 5:
                e |= 1
            e <<= 1
        rec.append(c ^ e)
    
    total = 0
    for (i,j) in zip(rec, enc):
        if i!=j:
            total += 1
    print total, 'corrupted characters detected ...'
    print rec

    print 'Decoding ...'
    dec = ecc_decode(rec)
    print dec
    if dec[1] == msg:
        print 'Decoded succesfully!'
    else:
        print 'Errors detected'
        print dec
        print msg



    print 'Corrupting message (burst) ...'
    rec = array.array('B', [c^255 for c in enc[:24]]) + enc[24:]
    
    total = 0
    for (i,j) in zip(rec, enc):
        if i!=j:
            total += 1
    print total, 'corrupted characters detected ...'
    print rec

    print 'Decoding ...'
    dec = ecc_decode(rec)
    print dec
    if dec[1] == msg:
        print 'Decoded succesfully!'
    else:
        print 'Errors detected'
        print dec
        print msg




if __name__ == '__main__':
    test()


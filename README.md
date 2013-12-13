Quiet Casting
=============

QuietCasting is a low rate, low power, group chat or twitter style
telecommunication technology having no central control nodes.

A QuietCasting group is made of a number of QuietCasting nodes. Each
QuietCasting node typically corresponds to a single user operating
such node or to a single autonomous sensor node.

The size of a QuietCasting group corresponds to the size of a typical
chat/node physical group. It is unlikely such a group will exceed 30
nodes though the total number of nodes in transmission/reception range
can be considerably larger. It is unlikely that a single node will be
transmitting at rates higher than 100 messages (each message about 50
bytes long) per hour. In a chat group comprised of 30 users, each
transmitting at a rate of 100 messages per hour, each user will need
to read about one SMS style message per *second*!  Approximately the
same quantities apply to a typical home sensor network.

QuietCasting defines and implements a set of protocols targeting low
power MCUs and RF communication devices. The most important
requirement of the QuietCasting protocol is **simplicity**. Our design
will heavily rely on probalistic methods to improve link
quality. There would be no features requiring state management (mesh
routing tables, etc.) and there would be no support for
acknowledgement packets (ACKs) etc. If delivery warranties are
required they should be handled at the application layer.



#### Design Decisions

 - QuietCasting nodes are simple receivers. There is no requirement
   that receiving nodes must acknowledge anything or indeed transmit
   anything at all upon reception of a transmitted message (Similar to
   FM radio or TV teletext). 

 - QuietCasting nodes are also simple broadcasters, broadcasting a
   given data payload to any QuietCasting node in range. There is no
   support for node discovery, pairing of nodes or the requirment that
   anything at all is known about the network topology.

 - To achieve such simplicity, the design allows the possibility of
   lost messages (like FM Radio and TV teletext) but in a manner where
   the probability of message loss is controlled by the communication
   protocol (specifically the error correcting code (ECC) used) and can be
   made arbitrarily small (unlike FM Radio or TV teletext).

 - The QuietCasting Error Correcting Code (ECC) must:

   1. be effective in low signal to noise ratio environments.
 
   2. allow for extremely simple encoding and decoding algorithms.

   3. run on small 8bit CPUs with limited resources.

   4. be compatible with the hardware features prevalent in existing
      low power RF devices.

   Perhaps the most important feature of the design is a good ECC and
   thus we will focus our initial effort on coming up with a good ECC
   algorithm. Unfortunately state of the art convolutional based codes
   are too complex and in any case we are not aware of convolutional
   ECCs that work well in high noise environments. 

 - A good target for our design is the Moteino:

     http://lowpowerlab.com/



### Details

#### The ECC layer

[code under quietcasting/lib/ecc.py on github]

The first layer we will define is the error correcting layer (ECC). A
good ECC should offer a considerable increase in link quality allowing
greater range and/or reducing the need for restransmissions.

Let us assume for instance that for every bit transmitted there is a
probability [p] that the bit will be received corrupted. For a payload
of say 500 bits the probability the payload is received correctly is
(1-p)**500. For p equal to 0.005 the chance of receiving the payload
correctly is about 0.08. It will require a large number of ACKs to
ensure correct reception which will cause a huge amount of network
traffic. A good ECC on the other hand should have no problem
correcting a message with such error rates.

The Quietcasting ECC expands a 48 byte message to a 48x4 encoded
message. The encoding can correct:

  - a sequence/burst of up to 192 error bits occuring anywhere in the
    received message.
    
  - two sequences/bursts of up to 96 error bits each occuring anywhere
    in the received message.
       
  - any single error bit (and frequently 2 bit errors) occuring
    anywhere in a single received 8bit word.


##### The data frame

Very simply the data frame is structured as below (where numbers stand
for 'bytes'):

    | 48b payload x 4 for a total of 196b |

No node ids or network id will be defined at this level and indeed a
caller can just access this layer and transmit any sequence of 48
bytes. Richer structure will be instroduced at the higher levels.



##### Specific hardware considerations.

The target device, Moteino, uses the RFM69 RF module by HopeRF. In
order to make effective use of the ECC code the following steps must
be taken:

 - Disable encryption. Encryption *after* ECC cannot work
   unfortunately. Disabling encryption will aslo allow a packet size of 255
   bytes, compatible with the ECC data frame requirments.

 - CRC checks must be disabled. Again CRC *after* ECC cannot work.


 - Most RF modules use a preamble/sync word to detect a valid
   transmission. We will need to tweek it so it will detect a valid
   sync word even if errors are detected. According to the HopeRF data
   sheet there is such funtionality (error tolerance; SyncTol) and it
   should be set to the maximum value (7 bits) (the appropriate
   registers are defined in Table 28, page 76 of the datasheet).



### Security

[coming next ...]



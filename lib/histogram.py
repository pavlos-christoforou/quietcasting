""" ascii based histogram generator for quick inspection of
    distributions.

"""


## give it a function API so it is easy and quick to use.


class Histogram(object):

    CHAR = '*'
    BIN_COUNT = 70
    TICK_PRECISION = 2
    MAX_HEIGHT = 100

    
    def __init__(self,
                 data,
                 char = None,
                 bin_count = None,
                 tick_precision = None,
                 max_height = None,
                 ):

        data.sort()
        
        self.data = data
        self.char = char or self.CHAR
        self.bin_count = bin_count or self.BIN_COUNT
        self.tick_precision = tick_precision or self.TICK_PRECISION
        self.max_height = max_height or self.MAX_HEIGHT
        
        self.data_max = max(data)
        self.data_min = min(data)
        self.data_count = len(data)

        self.bin_bounds = self._create_bin_bounds()
        self.ticks = self._create_ticks(self.bin_bounds, self.data_min)

        self.histogram = self._histogram()


    def _create_bin_bounds(self, count = None):

        count = count or self.bin_count

        width = (self.data_max - self.data_min) /float(count)

        bin_bounds = [self.data_min + width * (i + 1) for i in xrange(count)]

        return bin_bounds


    def _create_ticks(self, bin_bounds, data_min):
        out = []
        last = data_min
        for v in bin_bounds:
            out.append((v + last)/2.0)
            last = v
        return out

    def _histogram(self):

        """ no optimizations for now.

        """
        
        bin_count = self.bin_count
        hist = [0] * bin_count
        data = self.data
        bin_bounds = self.bin_bounds

        for value in data:
            positions = [i for (i, bound) in enumerate(bin_bounds) if value < bound]
            if positions:
                hist[min(positions)] += 1

        ## normalize
        ratio = self.max_height / float(max(hist))

        norm_hist = [i * ratio for i in hist]

        return norm_hist


    def pprint(self):

        tick_precision = self.tick_precision
        
        tick_fill = max([len('%f' % round(v, tick_precision)) for v in self.ticks])

        lines = []
        for (_bin, _tick) in zip(self.histogram, self.ticks):
            
            line = '{0:{tick_fill},.{tick_precision}f}: {1:*>{bar_length}}'.format(
                _tick,
                '',
                tick_fill = tick_fill,
                tick_precision = tick_precision,
                bar_length = round(_bin, 0),
                )

            lines.append(line)

        print '\n'.join(lines)




def histogram(data, bin_count = None):

    hist = Histogram(data = data, bin_count = bin_count)
    hist.pprint()







def test():

    import random

    data = [random.gauss(3.3, 2) for i in range(10000)]
    histogram(data)
    print '\n\n'
    data = [random.lognormvariate(0, .7) for i in range(10000)]
    histogram(data)
    print '\n\n'
    data = [random.paretovariate(100) for i in range(10000)]
    histogram(data)
    print '\n\n'
    data = [int(random.gauss(0, 2)) for i in range(10000)]
    histogram(data)
    print '\n\n'
    

if __name__ == '__main__':
    test()

  
        

import time


def timeit(f):
    """A simple timing tool for function execution time

    :param f: function that is timed
    :return: function inputs/paramters
    """
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print("func:{} args:[{}, {}] t_delta: {:.4} sec".format(f.__name__, args, kw, te-ts))
        return result

    return timed


# distributor.py
# probability distributions

# binomial distribution
# given samples
# fill in blanks for no samples and low samples

# multinomial distribution

# library still works even though warning
#import scipy.stats as ss
import inspect
from scipy.stats import norm, skewnorm, loggamma, fit
from scipy._lib._finite_differences import _derivative
from scipy.stats import rv_continuous
from scipy import integrate
from math import inf
from numba import njit
import numpy as np
from numpy import asarray, array, logical_and, place, vectorize, nan, inf, mean, atleast_1d, broadcast_arrays, broadcast_to, promote_types
#import math # for pi to get prob of x in distrib
import time
# read from csv
# import pandas as pd

# display data
import matplotlib.pyplot as plt

# import sys
# print(sys.path)

#import infrastructure as di

import reader # read stat dict data
#import converter # round
from converter import round_half_up

# === SETTINGS ===
player = 'jordan clarkson' # bam adebayo



# Example
# show random binom pmf
def binom_pmf():
    # setting the values 
    # of n and p 
    n = 6
    p = 0.6
    # defining the list of r values 
    r_values = list(range(n + 1)) 
    # obtaining the mean and variance  
    mean, var = ss.binom.stats(n, p) 
    # list of pmf values 
    dist = [ss.binom.pmf(r, n, p) for r in r_values ] 
    # printing the table 
    print("r\tp(r)") 
    for i in range(n + 1): 
        print(str(r_values[i]) + "\t" + str(dist[i])) 
    # printing mean and variance 
    print("mean = "+str(mean)) 
    print("variance = "+str(var))

def multinom_pmf(data):
    dist = ss.multinomial

    bounds = [(0, 10)]

    res = fit(dist, data, bounds) 
    print("res = "+str(res))

    res.plot()
    plt.show()


#multinom_pmf(data)




def plot_cdf(data):
    print('\n===Plot CDF===\n')
    print('data: ' + str(data))

    datasort = sorted(data)

    dist = norm

    #calculate probability that random value is less than or equal to v=1.96 in normal CDF
    v = 1.96
    prob_equal_or_less = dist.cdf(v)
    print('prob_equal_or_less: ' + str(prob_equal_or_less))

    prob_more = 1 - prob_equal_or_less

    #define x and y values to use for CDF
    N = len(data)
    x = np.sort(data)#np.linspace(-4, 4, 1000)
    y = np.arange(N) / float(N)
    #norm_cdf = ss.norm.cdf(x) # y

    plt.figure()
    plt.plot(x, y)

    bounds = [(-100, 100), (-100, 100)]
    norm_fit = fit(dist, data, bounds) #dist.fit(data)
    cdf_fit = norm_fit.cdf(data)
    plt.figure()
    plt.xlabel('Data')
    plt.ylabel('CDF')
    plt.title('CDF of Fitted Normal Distribution')
    plt.plot(data, cdf_fit)

    # pdf normal distribution, prob of exact value
    #prob_x = math.exp(-(x-mu)**2 / 2 * sigma**2) / (sigma * math.sqrt(2 * math.pi))
    # command equiv to fmla
    loc, scale = dist.fit(datasort)
    prob_x = dist.pdf(x, loc, scale)



def fit_data(data):
    print('\n===Fit Data===\n')
    print('data: ' + str(data))

    # plt.figure()
    # plt.hist(data, bins=int(np.max(data)+1), density=True)

    # === Normal === 
    dist = norm

    #loc, scale = dist.fit(data)
    #print('normfit: ' + str(normfit))
    # binomfit = ss.binom.fit(data)
    # print(binomfit)

    
    # normal takes 2 params: mean and var
    bounds = [(-100, 100), (-100, 100)]#, (0, 200)]

    # === Binom === 
    #dist = ss.binom
    # binom takes 2 params: num trials and prob
    #bounds = [(0, 82), (0, 1)]

    # === Poisson === 
    #dist = ss.poisson
    # poisson takes 1 param: mean = var
    #bounds = [(-100, 100)]

    res = fit(dist, data, bounds) 
    print("res = "+str(res))
    #loc, scale = ss.fit(dist, data, bounds) 
    #print("res = "+str(res))

    # n = res.fi
    # print("n = "+str(n))
    # print("p = "+str(p))
    # print("loc = "+str(loc))

    # plt.figure()
    # res.plot()

    # find empirical cdf to get prob of each val
    # datasort = sorted(data)
    # ecdf_res = dist.cdf(datasort, loc, scale)
    # print("ecdf_res = "+str(ecdf_res))
    # plt.figure()
    # plt.plot(data, ecdf_res)

    # prob_x = res[10]
    # print("prob_x = "+str(prob_x))

    # #plt.show()

    

    

    # datasort = sorted(data)
    
    # plt.figure()
    # plt.hist(data, density=True)
    # plt.title('Normal')
    # plt.plot(datasort, ss.norm.pdf(datasort, *normfit))
    
    # plt.figure()
    # plt.hist(data, density=True)
    # plt.title('Binomial')
    # plt.plot(datasort, ss.binom.pmf(datasort, *binomfit))
    






# prob distrib
# given a val of interest
# AND the data with all vals
# FIT prob distrib to get parameters (eg mean and std dev)
# COMPUTE prob of x from fmla given params
def generate_prob_from_distrib(val, loc, dist):
    #print('\n===Generate Prob from Distrib: ' + str(val) + '===\n')
    #print('loc: ' + str(loc))
    # print('scale: ' + str(scale))
    #print('dist: ' + str(dist))

    prob = 0

    # ASSUME normal distrib for now bc most examples
    # THEN determine best fit distrib (see quantile charts and best fit libs)

    # bc nothing actually 100% or 0 and we dont need more accuracy than 1%
    # if normal, use pdf
    #prob = dist.pmf(val, loc)
    # if poisson, use pmf
    prob = round_half_up(dist.pmf(val, loc), 4)
    #print('prob: ' + str(prob))

    if prob > 0.99:
        prob = 0.99
    elif prob < 0.01:
        prob = 0.01
    else:
        prob = round_half_up(prob, 2)

    #print('prob: ' + str(prob))
    return prob

def generate_all_probs_from_distrib(data, dist):
    print('\n===Generate All Probs from Distrib===\n')
    print('data: ' + str(data))

    probs = [] # list all vals in range in order. or val:prob

    # if normal
    #loc, scale = dist.fit(data)
    # if poisson
    bounds = [(0, 100)]
    res = fit(dist, data, bounds)
    print('res: ' + str(res))
    loc = res.params.mu
    print('loc: ' + str(loc))
    #print('scale: ' + str(scale))

    # loop thru all vals, even those not directly hit but surpassed
    #highest_val = data[-1] bc sorted
    for val in range(data[-1]):
        prob = 0
        #if val not in probs.keys():
        # we get prob of exactly 0 and prob >= next val
        if val == 0:
            prob = generate_prob_from_distrib(val, loc, dist)
            probs.append(prob)

        prob = generate_prob_over_from_distrib(val, loc, dist)
        probs.append(prob)

    print('probs: ' + str(probs))
    return probs


def generate_player_prob_distribs(player):
    # get data from stat dict, which shows stat for each game in each condition
    print('Input: player_stat_dict = {year: {season part: {stat name: {condition: {game idx: stat val, ... = {\'2023\': {\'regular\': {\'pts\': {\'all\': {\'0\': 33, ... }, \'B Beal SG, D Gafford C, K Kuzma SF, K Porzingis C, M Morris PG starters\': {\'1\': 7, ...')
    
    player_prob_distribs = {} # mirrors stat probs but with probs from distribs instead of direct measurement and NA if not reached
    
    dist = ss.poisson
    #print('dist: ' + str(dist))

    # take data from a single condition to model fit that condition
    # get prob of each val in each condition
    player_stat_dict = reader.read_player_stat_dict(player)

    for year, year_stat_dict in player_stat_dict.items():
        #year = '2024'
        #year_stat_dict = player_stat_dict[year]
        part = 'regular'
        part_stat_dict = year_stat_dict[part]
        stat_name = 'pts'
        stat_dict = part_stat_dict[stat_name]
        condition = 'all'
        condition_stat_dict = stat_dict[condition]
        data = sorted(list(condition_stat_dict.values()))

        # fit_data(data)

        # plot_cdf(data)

        # list of probs for each val in data
        val_probs = generate_all_probs_from_distrib(data, dist)

        if year not in player_prob_distribs.keys():
            player_prob_distribs[year] = {}
        if part not in player_prob_distribs[year].keys():
            player_prob_distribs[year][part] = {}
        if stat_name not in player_prob_distribs[year][part].keys():
            player_prob_distribs[year][part][stat_name] = {}
        if condition not in player_prob_distribs[year][part][stat_name].keys():
            player_prob_distribs[year][part][stat_name][condition] = {}
        
        player_prob_distribs[year][part][stat_name][condition] = val_probs


    plt.show()

    print('player_prob_distribs: ' + str(player_prob_distribs))
    return player_prob_distribs


#player_prob_distribs = generate_player_prob_distribs(player)



    








# cumulative distribution
def generate_prob_over_from_distrib(val, dist, sample_fit_dict):
    # print('\n===Generate Prob Over from Distrib: ' + str(val+1) + '===\n')
    # print('Input: sample_fit_dict = {shape:a, loc:l, scale:s} or {mean:m, scale:s}...')

    prob_over = 0 # prob over includes val, just shorthand for over and equal bc we dont need strict over (prob greater would be strict over bc >)
        
    # CHANGE so we get prob cdf (<=) and then get 1-cdf_prev to get prob over (eg 5+)
    val += 0.499999 # <0.5

    

    prob_less_or_equal = 0

    sample_loc = sample_fit_dict['loc']
    sample_scale = sample_fit_dict['scale']

    shape_key = 'shape'
    shape_1_key = 'shape 1'
    shape_2_key = 'shape 2'
    shape_3_key = 'shape 3'
    #mean_key = 'mean'
    #sample_shape = ''
    #sample_mean = ''
    if shape_key in sample_fit_dict.keys():
        sample_shape = sample_fit_dict[shape_key]

        prob_less_or_equal = round_half_up(dist.cdf(val, sample_shape, sample_loc, sample_scale), 5)
    elif shape_3_key in sample_fit_dict.keys():
        sample_shape_1 = sample_fit_dict[shape_1_key]
        sample_shape_2 = sample_fit_dict[shape_2_key]
        sample_shape_3 = sample_fit_dict[shape_3_key]

        prob_less_or_equal = round_half_up(dist.cdf(val, sample_shape_1, sample_shape_2, sample_shape_3, sample_loc, sample_scale), 5)
    elif shape_1_key in sample_fit_dict.keys():
        sample_shape_1 = sample_fit_dict[shape_1_key]
        sample_shape_2 = sample_fit_dict[shape_2_key]

        prob_less_or_equal = round_half_up(dist.cdf(val, sample_shape_1, sample_shape_2, sample_loc, sample_scale), 5)
    else:
        #sample_mean = sample_fit_dict[mean_key] ???

        prob_less_or_equal = round_half_up(dist.cdf(val, sample_loc, sample_scale), 5)


    # see if P(1+)= P(1) + P(2+) = 1 - P(<0.5)?
    # NO bc P(1) should include P(>0.5)? 

    # ASSUME normal distrib for now bc most examples
    # THEN determine best fit distrib (see quantile charts and best fit libs)

    # if val=0 we get prob exactly 0
    # AND we also get the prob over for the next val
    # bc cdf returns <= but we want >=
    
    # we want prob over to include val
    # but cdf returns <= val so take 1-cdf to get over
    # if we take 1-cdf for val we get 
    
    #print('prob_less_or_equal: ' + str(prob_less_or_equal))
    # bc nothing actually 100% or 0 and we dont need more accuracy than 1%???
    # NO actually we need accuracy up to 0.1% to diff extremely likely vs very likely
    if prob_less_or_equal > 0.999:
        prob_less_or_equal = 0.999
    elif prob_less_or_equal < 0.001:
        prob_less_or_equal = 0.001
    else:
        prob_less_or_equal = round_half_up(prob_less_or_equal, 3)

    #print('prob_less_or_equal: ' + str(prob_less_or_equal))
    prob_over = round_half_up(1 - prob_less_or_equal, 3) # P(>val+1)
    #prob_over_or_equal_next_val = prob_strict_over

    #print('prob_over: ' + str(prob_over))
    return prob_over







parse_arg_template = """
def _parse_args(self, %(shape_arg_str)s %(locscale_in)s):
    return (%(shape_arg_str)s), %(locscale_out)s

def _parse_args_rvs(self, %(shape_arg_str)s %(locscale_in)s, size=None):
    return self._argcheck_rvs(%(shape_arg_str)s %(locscale_out)s, size=size)

def _parse_args_stats(self, %(shape_arg_str)s %(locscale_in)s, moments='mv'):
    return (%(shape_arg_str)s), %(locscale_out)s, moments
"""




# def generate_cdf_over(vals, dist, sample_fit_dict, model_name):
#     # print('\n===Generate CDF Over===\n')
#     # print('vals: ' + str(vals))
#     # print('dist: ' + str(dist))
#     # print('sample_fit_dict: ' + str(sample_fit_dict))

#     cdf_over = [] # prob over includes val, just shorthand for over and equal bc we dont need strict over (prob greater would be strict over bc >)
        
#     # CHANGE so we get prob cdf (<=) and then get 1-cdf_prev to get prob over (eg 5+)
#     vals = vals + 0.499999 # <0.5

    

#     prob_less_or_equal = 0

#     sample_loc = sample_fit_dict['loc']
#     sample_scale = sample_fit_dict['scale']

#     shape_key = 'shape'
#     shape_1_key = 'shape 1'
#     shape_2_key = 'shape 2'
#     shape_3_key = 'shape 3'
#     #mean_key = 'mean'
#     #sample_shape = ''
#     #sample_mean = ''
#     #print('\n===Inspect===\n')
#     if shape_key in sample_fit_dict.keys():
#         sample_shape = sample_fit_dict[shape_key]


#         prob_less_or_equal = dist.cdf(vals, sample_shape, sample_loc, sample_scale)
#         #print(inspect.getsource(dist.cdf))

#         # specific fcn call depends on dist
#         # so to speed up write fcns here and use jit
#         #if model_name == 'skewnorm':
#             # scipy.stats.norm.cdf()
#             # class norm_gen(rv_continuous):
#             # def _cdf(self, x):
#             #   return _norm_cdf(x)

#             # def _norm_cdf(x):
#             #     return sc.ndtr(x)
#             # import scipy.special as sc

#             #prob_less_or_equal = skewnorm_cdf(vals, sample_shape, sample_loc, sample_scale)
        





#     elif shape_3_key in sample_fit_dict.keys():
#         sample_shape_1 = sample_fit_dict[shape_1_key]
#         sample_shape_2 = sample_fit_dict[shape_2_key]
#         sample_shape_3 = sample_fit_dict[shape_3_key]

#         prob_less_or_equal = dist.cdf(vals, sample_shape_1, sample_shape_2, sample_shape_3, sample_loc, sample_scale)
#         #print(inspect.getsource(dist.cdf))
#     elif shape_1_key in sample_fit_dict.keys():
#         sample_shape_1 = sample_fit_dict[shape_1_key]
#         sample_shape_2 = sample_fit_dict[shape_2_key]

#         prob_less_or_equal = dist.cdf(vals, sample_shape_1, sample_shape_2, sample_loc, sample_scale)
#         #print(inspect.getsource(dist.cdf))
#     else:
#         #sample_mean = sample_fit_dict[mean_key] ???

#         prob_less_or_equal = dist.cdf(vals, sample_loc, sample_scale)
#         #print(inspect.getsource(dist.cdf))

#         #if model_name == 'norm':

#     #print('prob_less_or_equal: ' + str(prob_less_or_equal))
#     # see if P(1+)= P(1) + P(2+) = 1 - P(<0.5)?
#     # NO bc P(1) should include P(>0.5)? 

#     # ASSUME normal distrib for now bc most examples
#     # THEN determine best fit distrib (see quantile charts and best fit libs)

#     # if val=0 we get prob exactly 0
#     # AND we also get the prob over for the next val
#     # bc cdf returns <= but we want >=
    
#     # we want prob over to include val
#     # but cdf returns <= val so take 1-cdf to get over
#     # if we take 1-cdf for val we get 
    
#     #print('prob_less_or_equal: ' + str(prob_less_or_equal))
#     # bc nothing actually 100% or 0 and we dont need more accuracy than 1%???
#     # NO actually we need accuracy up to 0.1% to diff extremely likely vs very likely
#     # if prob_less_or_equal > 0.999:
#     #     prob_less_or_equal = 0.999
#     # elif prob_less_or_equal < 0.001:
#     #     prob_less_or_equal = 0.001
#     # else:
#     #     prob_less_or_equal = round_half_up(prob_less_or_equal, 3)

#     prob_less_or_equal[prob_less_or_equal > 0.999] = 0.999
#     prob_less_or_equal[prob_less_or_equal < 0.001] = 0.001
#     #print('prob_less_or_equal: ' + str(prob_less_or_equal))
    
#     cdf_over = 1 - prob_less_or_equal




#     # probs_less_or_equal = dist.cdf(vals, sample_loc, sample_scale)
#     # probs = 1 - probs_less_or_equal

#     #print('cdf_over: ' + str(cdf_over))
#     return cdf_over




def _pg_pdf(x, *args):
    print('\n===PG _PDF===\n')
    print('x: ' + str(x))
    print('args: ' + str(args))
    
    test_pdf = _derivative(_pg_cdf, x, dx=1e-5, args=args, order=5)
    
    print('test_pdf: ' + str(test_pdf))
    return test_pdf 

def _pg_cdf_single(x, *args):
    print('\n===PG _Test _CDF _Single===\n')
    print('x: ' + str(x))
    print('args: ' + str(args))
    _a, _b = pg_get_support(*args)
    #cdf_single = integrate.quad(rv_continuous._pdf, _a, x, args=args)[0]
    cdf_single = integrate.quad(_pg_pdf, _a, x, args=args)[0]
    print('cdf_single: ' + str(cdf_single))
    return cdf_single 

#pg_cdfvec = vectorize(_pg_cdf_single, otypes='d')
#pg_cdfvec.nin = len(args) + 1 #numargs + 1    
def _pg_cdf(x, pg_cdfvec, *args):
    print('\n===_PG _CDF===\n')
    print('x: ' + str(x))
    print('args: ' + str(args))

    
    _pg_cdf = pg_cdfvec(x, *args)
    print('_pg_cdf = pg_cdfvec(x, *args) = ' + str(_pg_cdf))
    return _pg_cdf

def pg_argsreduce(cond, *args):
    # print('\n===PG Argsreduce===\n')
    # print('cond: ' + str(cond))
    # print('args: ' + str(args))

    """Clean arguments to:

    1. Ensure all arguments are iterable (arrays of dimension at least one
    2. If cond != True and size > 1, ravel(args[i]) where ravel(condition) is
       True, in 1D.

    Return list of processed arguments.

    Examples
    --------
    >>> import numpy as np
    >>> from scipy.stats._distn_infrastructure import argsreduce
    >>> rng = np.random.default_rng()
    >>> A = rng.random((4, 5))
    >>> B = 2
    >>> C = rng.random((1, 5))
    >>> cond = np.ones(A.shape)
    >>> [A1, B1, C1] = argsreduce(cond, A, B, C)
    >>> A1.shape
    (4, 5)
    >>> B1.shape
    (1,)
    >>> C1.shape
    (1, 5)
    >>> cond[2,:] = 0
    >>> [A1, B1, C1] = argsreduce(cond, A, B, C)
    >>> A1.shape
    (15,)
    >>> B1.shape
    (1,)
    >>> C1.shape
    (15,)

    """
    # some distributions assume arguments are iterable.
    newargs = atleast_1d(*args)

    # np.atleast_1d returns an array if only one argument, or a list of arrays
    # if more than one argument.
    if not isinstance(newargs, (list, tuple)):
        newargs = (newargs,)

    if np.all(cond):
        # broadcast arrays with cond
        *newargs, cond = broadcast_arrays(*newargs, cond)
        argsreduce = [arg.ravel() for arg in newargs]
        #print('argsreduce = goodargs = ' + str(argsreduce)) 
        return argsreduce 

    s = cond.shape
    # np.extract returns flattened arrays, which are not broadcastable together
    # unless they are either the same size or size == 1.
    argsreduce = [(arg if np.size(arg) == 1
            else np.extract(cond, broadcast_to(arg, s)))
            for arg in newargs]
    
    #print('argsreduce = goodargs = ' + str(argsreduce)) 
    return argsreduce 

def pg_open_support_mask(x, *args):
    # print('\n===PG Open Support Mask===\n')
    # print('x: ' + str(x))
    # print('args: ' + str(args))

    a, b = pg_get_support(*args)

    with np.errstate(invalid='ignore'):
        open_support_mask = (a < x) & (x < b)
        #print('open_support_mask: ' + str(open_support_mask))
        return open_support_mask

# These are the methods you must define (standard form functions)
# NB: generic _pdf, _logpdf, _cdf are different for
# rv_continuous and rv_discrete hence are defined in there
def pg_argcheck(*args):
    # print('\n===PG Argcheck===\n')
    # print('args: ' + str(args))

    """Default check for correct values on args and keywords.

    Returns condition array of 1's where arguments are correct and
        0's where they are not.

    """
    cond = 1
    for arg in args:
        cond = logical_and(cond, (asarray(arg) > 0))

    #print('argcheck cond: ' + str(cond))
    return cond

def pg_get_support(*args, **kwargs):
    # print('\n===PG Get Support===\n')
    # print('args: ' + str(args))
    # print('kwargs: ' + str(kwargs))

    """Return the support of the (unscaled, unshifted) distribution.

    *Must* be overridden by distributions which have support dependent
    upon the shape parameters of the distribution.  Any such override
    *must not* set or change any of the class members, as these members
    are shared amongst all instances of the distribution.

    Parameters
    ----------
    arg1, arg2, ... : array_like
        The shape parameter(s) for the distribution (see docstring of the
        instance object for more information).

    Returns
    -------
    a, b : numeric (float, or int or +/-np.inf)
        end-points of the distribution's support for the specified
        shape parameters.
    """

    # based on dist???
    a = -inf
    b = inf

    # print('a: ' + str(a))
    # print('b: ' + str(b))
    return a, b

pg_cdfvec = vectorize(_pg_cdf_single, otypes='d')


# figure out how to use njit for strict types
# @njit = nopython=True
# cache=fastmath=parallel=True made no difference
#@njit(cache=True, fastmath=True, parallel=True)
# @jit()
def skewnorm_cdf(x, shape, loc, scale):
#def skewnorm_cdf(x, *args, **kwds):
    print('\n===PG Skewnorm CDF===\n')
    # print('x: ' + str(x))
    # print('shape: ' + str(shape))
    # print('loc: ' + str(loc))
    # print('scale: ' + str(scale))
    # print('x: ' + str(x))
    # args = (shape, loc, scale)
    # print('args: ' + str(args))
    # print('kwds: {}')

    """
    Cumulative distribution function of the given RV.

    Parameters
    ----------
    x : array_like
        quantiles
    arg1, arg2, arg3,... : array_like
        The shape parameter(s) for the distribution (see docstring of the
        instance object for more information)
    loc : array_like, optional
        location parameter (default=0)
    scale : array_like, optional
        scale parameter (default=1)

    Returns
    -------
    cdf : ndarray
        Cumulative distribution function evaluated at `x`

    """
    #args, loc, scale = _parse_args(*args, **kwds)
    args = (shape,)
    # print('\nparsed args: ' + str(args))
    # print('parsed loc: ' + str(loc))
    # print('parsed scale: ' + str(scale))

    x, loc, scale = map(asarray, (x, loc, scale))
    # print('mapped x: ' + str(x))
    # print('mapped loc: ' + str(loc))
    # print('mapped scale: ' + str(scale))

    args = tuple(map(asarray, args))
    #print('\nfinal args: ' + str(args))

    _a, _b = pg_get_support(*args)

    dtyp = promote_types(x.dtype, np.float64)
    x = asarray((x - loc)/scale, dtype=dtyp)
    #print('\nx: ' + str(x))
    
    cond0 = pg_argcheck(*args) & (scale > 0)
    #print('\ncond0: ' + str(cond0))

    cond1 = pg_open_support_mask(x, *args) & (scale > 0)
    #print('\ncond1: ' + str(cond1))

    cond2 = (x >= asarray(_b)) & cond0
    #print('\ncond2: ' + str(cond2))

    cond = cond0 & cond1
    #print('\ncond: ' + str(cond))

    output = np.zeros(np.shape(cond), dtyp)
    #print('\ninit output: ' + str(output))
    
    badvalue = nan # should this be fcn param?
    #print('\nself.badvalue: ' + str(badvalue))
    
    place(output, (1-cond0)+np.isnan(x), badvalue)
    place(output, cond2, 1.0)
    #print('\noutput: ' + str(output))

    pg_cdfvec = vectorize(_pg_cdf_single, otypes='d')
    pg_cdfvec.nin = len(args) + 1 #numargs + 1

    if np.any(cond):  # call only if at least 1 entry
        goodargs = pg_argsreduce(cond, *((x,)+args))
        place(output, cond, _pg_cdf(*goodargs))
    if output.ndim == 0:
        print('final output[()]: ' + str(output[()]))
        return output[()]
    
    print('final output: ' + str(output))
    return output

def norm_cdf(x, loc, scale):
    print('\n===PG Norm CDF===\n')
    # print('x: ' + str(x))
    # print('loc: ' + str(loc))
    # print('scale: ' + str(scale))
    # print('x: ' + str(x))
    # args = (loc, scale)
    # print('args: ' + str(args))
    # print('kwds: {}')

    """
    Cumulative distribution function of the given RV.

    Parameters
    ----------
    x : array_like
        quantiles
    arg1, arg2, arg3,... : array_like
        The shape parameter(s) for the distribution (see docstring of the
        instance object for more information)
    loc : array_like, optional
        location parameter (default=0)
    scale : array_like, optional
        scale parameter (default=1)

    Returns
    -------
    cdf : ndarray
        Cumulative distribution function evaluated at `x`

    """
    #args, loc, scale = _parse_args(*args, **kwds)
    args = ()
    # print('\nparsed args: ' + str(args))
    # print('parsed loc: ' + str(loc))
    # print('parsed scale: ' + str(scale))

    x, loc, scale = map(asarray, (x, loc, scale))
    # print('\nmapped x: ' + str(x))
    # print('mapped loc: ' + str(loc))
    # print('mapped scale: ' + str(scale))

    args = tuple(map(asarray, args))
    #print('\nfinal args: ' + str(args))

    _a, _b = pg_get_support(*args)

    dtyp = promote_types(x.dtype, np.float64)
    x = asarray((x - loc)/scale, dtype=dtyp)
    #print('\nx: ' + str(x))
    
    cond0 = pg_argcheck(*args) & (scale > 0)
    #print('\ncond0: ' + str(cond0))

    cond1 = pg_open_support_mask(x, *args) & (scale > 0)
    #print('\ncond1: ' + str(cond1))

    cond2 = (x >= asarray(_b)) & cond0
    #print('\ncond2: ' + str(cond2))

    cond = cond0 & cond1
    #print('\ncond: ' + str(cond))

    output = np.zeros(np.shape(cond), dtyp)
    #print('\ninit output: ' + str(output))
    
    badvalue = nan # should this be fcn param?
    #print('\nself.badvalue: ' + str(badvalue))
    
    place(output, (1-cond0)+np.isnan(x), badvalue)
    place(output, cond2, 1.0)
    #print('\noutput: ' + str(output))

    if np.any(cond):  # call only if at least 1 entry
        goodargs = pg_argsreduce(cond, *((x,)+args))
        place(output, cond, _pg_cdf(*goodargs))
    if output.ndim == 0:
        print('final output[()]: ' + str(output[()]))
        return output[()]
    
    print('final output: ' + str(output))
    return output

#@njit
def generate_cdf_over(vals, dist, sample_fit_params, model_name):
    # print('\n===Generate CDF Over===\n')
    # print('vals: ' + str(vals))
    # #print('dist: ' + str(dist))
    # print('model_name: ' + str(model_name))
    # print('sample_fit_params: ' + str(sample_fit_params))

    cdf_over = [] # prob over includes val, just shorthand for over and equal bc we dont need strict over (prob greater would be strict over bc >)
        
    # CHANGE so we get prob cdf (<=) and then get 1-cdf_prev to get prob over (eg 5+)
    vals = vals + 0.499999 # <0.5

    # test single val
    # val = 0
    # print('val: ' + str(val))

    prob_less_or_equal = 0

    sample_loc = sample_fit_params[0] #sample_fit_dict['loc']
    sample_scale = sample_fit_params[1] #sample_fit_dict['scale']


    if len(sample_fit_params) == 2:
        prob_less_or_equal = dist.cdf(vals, sample_loc, sample_scale)
        #print(inspect.getsource(dist.cdf))

        # if model_name == 'norm':
        #     prob_less_or_equal = norm_cdf(vals, sample_loc, sample_scale)
    
    elif len(sample_fit_params) == 3:
        sample_shape = sample_fit_params[2]

        prob_less_or_equal = dist.cdf(vals, sample_shape, sample_loc, sample_scale)
        #print(inspect.getsource(dist.cdf))

        # specific fcn call depends on dist
        # so to speed up write fcns here and use jit
        # if model_name == 'skewnorm':
        #     prob_less_or_equal = skewnorm_cdf(vals, sample_shape, sample_loc, sample_scale)
    
    else:
        print('Warning: Unknown dist! ' + model_name)


    
    #print('prob_less_or_equal: ' + str(prob_less_or_equal))
    
    prob_less_or_equal[prob_less_or_equal > 0.999] = 0.999
    prob_less_or_equal[prob_less_or_equal < 0.001] = 0.001
    #print('prob_less_or_equal: ' + str(prob_less_or_equal))
    
    cdf_over = 1 - prob_less_or_equal

    #print('cdf_over: ' + str(cdf_over))
    return cdf_over


def distribute_all_probs(cond_data, player_stat_model, player='', stat='', condition=''): # if normal dist, avg_scale, dist_name='normal'):
    # print('\n===Test Distribute All Probs===\n')
    # print('cond_data: ' + str(cond_data))
    # print('player: ' + str(player))
    # print('stat: ' + str(stat))
    # print('condition: ' + str(condition))
    # print('Input: player_stat_model = {model name, sim data, sim avg, sim max}')# = ' + str(player_stat_model)) # {name:pareto, data:sim_all_data, avg:a, max:m} = 
    # print('\nOutput: all_probs = [p1,...] = [0.92,...]\n')

    # time at start of dist all probs
    #start_dist_probs = time.time()

    probs = [] # 1 to N, list all vals in range in order. or val:prob


    if 'data' in player_stat_model.keys():
        sim_all_data = array(player_stat_model['data']) # np array or round???
        all_avg = player_stat_model['avg'] #sim_all_data.mean #np.mean(sim_all_data) # ??? should be = all avg but could change to actually = avg?
        #print('all_avg: ' + str(all_avg))

        cond_avg = mean(cond_data)#ss.fit(dist, data, bounds).params.mu
        #print('cond_avg: ' + str(cond_avg))

        # round 2-6?
        sample_data = sim_all_data * (cond_avg / all_avg)
        #round_half_up(, 2)

        #sample_avg = np.mean(sample_data)
        #print('sample_avg: ' + str(sample_avg))
        #print('cond_avg: ' + str(cond_avg))


        model_name = player_stat_model['name']#.keys()[0] #only 1 model per stat
        #dist_str = 'ss.' + model_name
        dist = eval(model_name)

        params_dict = {'skewnorm':'a',
                        'loggamma':'c'}
        
        # CONSIDER change back to 100 bounds bc worked that way
        # even tho all data bounds were set to 200 at the time
        # so the mismatched bounds shouldve cause errors
        # CONSIDER increase bounds to 250 bc noted pat bev bounds=200 so past limit

        bounds = [(-250, 250), (-250, 250)]
        if model_name != 'norm': # or in params dict
            bounds = [(-250, 250), (-250, 250), (-250, 250)]
        #print('bounds: ' + str(bounds))
            
        #before_fit = time.time()
        sample_fit_results = fit(dist, sample_data, bounds)
        #print(inspect.getsource(fit))
        # time after gen cdf over
        # after_fit = time.time()
        # duration = round(after_fit - before_fit, 5)
        # print('\nbefore fit -> after fit: ' + str(duration) + ' s')

        sample_fit_params = sample_fit_results.params
        #print('sample_fit_params: ' + str(sample_fit_params))

        #dist_param = ''
        #sample_fit_dict = {}
        final_sample_fit_params = ()

        #shape_models = ['skewnorm', 'loggamma'] # models with shape param
        # since only 3 valid models and 1 has no shape just check for model w/o shape
        if model_name == 'norm':
            final_sample_fit_params = (sample_fit_params.loc, sample_fit_params.scale)
        
        else:
            dist_param = params_dict[model_name]
            sample_shape_param = 'sample_fit_params.' + dist_param
            sample_shape = eval(sample_shape_param) #fit_params.c

            final_sample_fit_params = (sample_fit_params.loc, sample_fit_params.scale, sample_shape)
    
        

        # NEED highest val from all data
        # loop thru all vals, even those not directly hit but surpassed
        highest_val = round_half_up(player_stat_model['max']) #sim_all_data.max #data[-1] # bc sorted
        #print('highest_val: ' + str(highest_val))
        # start at 1 but P(1 or more) = 100 - P(0), where P(0) = P(<0.5)
        # include highest val
        # for val in range(highest_val):
        #     # dist_dict = {'model name':'', 'shape':'', 'loc':'', 'scale':''}
        #     prob = generate_prob_over_from_distrib(val, dist, sample_fit_dict)
        #     probs.append(prob)
        # print('single probs: ' + str(probs))

        vals = np.linspace(0, highest_val-1, highest_val, dtype=int)
        #print('vals: ' + str(vals))
        # probs_less_or_equal = round_half_up(dist.cdf(vals, sample_loc, sample_scale), 5)
        # probs = 1 - probs_less_or_equal

        # time before gen cdf over
        # before_gen_cdf_over = time.time()
        # duration = round(before_gen_cdf_over - start_dist_probs, 2)
        # print('start dist probs -> gen cdf over: ' + str(duration) + ' s')

        probs = generate_cdf_over(vals, dist, final_sample_fit_params, model_name).tolist()
        #probs = [generate_prob_over_from_distrib(val, dist, sample_fit_dict) for val in range(highest_val)]

        # time after gen cdf over
        # after_gen_cdf_over = time.time()
        # duration = round(after_gen_cdf_over - before_gen_cdf_over, 5)
        # print('before gen cdf over -> after gen cdf over: ' + str(duration) + ' s')

    #print('final probs: ' + str(probs))
    return probs


#@njit
def test_generate_cdf_over(vals, dist, sample_fit_params, model_name):
    # print('\n===Generate CDF Over===\n')
    # print('vals: ' + str(vals))
    # #print('dist: ' + str(dist))
    # print('model_name: ' + str(model_name))
    # print('sample_fit_params: ' + str(sample_fit_params))

    cdf_over = [] # prob over includes val, just shorthand for over and equal bc we dont need strict over (prob greater would be strict over bc >)
        
    # CHANGE so we get prob cdf (<=) and then get 1-cdf_prev to get prob over (eg 5+)
    vals = vals + 0.499999 # <0.5

    

    prob_less_or_equal = 0

    sample_loc = sample_fit_params[0] #sample_fit_dict['loc']
    sample_scale = sample_fit_params[1] #sample_fit_dict['scale']

    # shape_key = 'shape'
    # shape_1_key = 'shape 1'
    # shape_2_key = 'shape 2'
    # shape_3_key = 'shape 3'
    #mean_key = 'mean'
    #sample_shape = ''
    #sample_mean = ''
    #print('\n===Inspect===\n')
    # if shape_key in sample_fit_dict.keys():
    #     sample_shape = sample_fit_dict[shape_key]

    # if len(sample_fit_params) > 4:
    #     sample_shape_1 = sample_fit_params[2]
    #     sample_shape_2 = sample_fit_params[3]
    #     sample_shape_3 = sample_fit_params[4]

    #     prob_less_or_equal = dist.cdf(vals, sample_shape_1, sample_shape_2, sample_shape_3, sample_loc, sample_scale)
    #     #print(inspect.getsource(dist.cdf))


    if len(sample_fit_params) > 3:
        print('Warning: Unknown dist! ' + model_name)
    #     sample_shape_1 = sample_fit_params[2]
    #     sample_shape_2 = sample_fit_params[3]

    #     prob_less_or_equal = dist.cdf(vals, sample_shape_1, sample_shape_2, sample_loc, sample_scale)
        #print(inspect.getsource(dist.cdf))
    elif len(sample_fit_params) > 2:
        sample_shape = sample_fit_params[2]

        prob_less_or_equal = dist.cdf(vals, sample_shape, sample_loc, sample_scale)
        #print(inspect.getsource(dist.cdf))

        # specific fcn call depends on dist
        # so to speed up write fcns here and use jit
        # if model_name == 'skewnorm':
        #     prob_less_or_equal = skewnorm_cdf(vals, sample_shape, sample_loc, sample_scale)



            # scipy.stats.norm.cdf()
            # class norm_gen(rv_continuous):
            # def _cdf(self, x):
            #   return _norm_cdf(x)

            # def _norm_cdf(x):
            #     return sc.ndtr(x)
            # import scipy.special as sc

            #prob_less_or_equal = skewnorm_cdf(vals, sample_shape, sample_loc, sample_scale)
    
    else:
        #sample_mean = sample_fit_dict[mean_key] ???

        prob_less_or_equal = dist.cdf(vals, sample_loc, sample_scale)
        #print(inspect.getsource(dist.cdf))

        # if model_name == 'norm':
        #     prob_less_or_equal = norm_cdf(vals, sample_loc, sample_scale)

    #print('prob_less_or_equal: ' + str(prob_less_or_equal))
    # see if P(1+)= P(1) + P(2+) = 1 - P(<0.5)?
    # NO bc P(1) should include P(>0.5)? 

    # ASSUME normal distrib for now bc most examples
    # THEN determine best fit distrib (see quantile charts and best fit libs)

    # if val=0 we get prob exactly 0
    # AND we also get the prob over for the next val
    # bc cdf returns <= but we want >=
    
    # we want prob over to include val
    # but cdf returns <= val so take 1-cdf to get over
    # if we take 1-cdf for val we get 
    
    #print('prob_less_or_equal: ' + str(prob_less_or_equal))
    # bc nothing actually 100% or 0 and we dont need more accuracy than 1%???
    # NO actually we need accuracy up to 0.1% to diff extremely likely vs very likely
    # if prob_less_or_equal > 0.999:
    #     prob_less_or_equal = 0.999
    # elif prob_less_or_equal < 0.001:
    #     prob_less_or_equal = 0.001
    # else:
    #     prob_less_or_equal = round_half_up(prob_less_or_equal, 3)

    prob_less_or_equal[prob_less_or_equal > 0.999] = 0.999
    prob_less_or_equal[prob_less_or_equal < 0.001] = 0.001
    #print('prob_less_or_equal: ' + str(prob_less_or_equal))
    
    cdf_over = 1 - prob_less_or_equal




    # probs_less_or_equal = dist.cdf(vals, sample_loc, sample_scale)
    # probs = 1 - probs_less_or_equal

    #print('cdf_over: ' + str(cdf_over))
    return cdf_over


def test_distribute_all_probs(cond_data, player_stat_model, player='', stat='', condition=''): # if normal dist, avg_scale, dist_name='normal'):
    # print('\n===Distribute All Probs===\n')
    # print('cond_data: ' + str(cond_data))
    # print('player: ' + str(player))
    # print('stat: ' + str(stat))
    # print('condition: ' + str(condition))
    # print('Input: player_stat_model = {model name, sim data, sim avg, sim max}')# = ' + str(player_stat_model)) # {name:pareto, data:sim_all_data, avg:a, max:m} = 
    # print('\nOutput: all_probs = [p1,...]\n')

    probs = [] # 1 to N, list all vals in range in order. or val:prob


    if 'data' in player_stat_model.keys():
        sim_all_data = array(player_stat_model['data']) # np array or round???
        all_avg = player_stat_model['avg'] #sim_all_data.mean #np.mean(sim_all_data) # ??? should be = all avg but could change to actually = avg?
        #print('all_avg: ' + str(all_avg))

        cond_avg = mean(cond_data)#ss.fit(dist, data, bounds).params.mu
        #print('cond_avg: ' + str(cond_avg))

        # round 2-6?
        sample_data = sim_all_data * (cond_avg / all_avg)
        #round_half_up(, 2)

        #sample_avg = np.mean(sample_data)
        #print('sample_avg: ' + str(sample_avg))
        #print('cond_avg: ' + str(cond_avg))


        model_name = player_stat_model['name']#.keys()[0] #only 1 model per stat
        #dist_str = 'ss.' + model_name
        dist = eval(model_name)

        params_dict = {'gamma':'a',
                        'erlang':'a',
                        'powerlaw':'a',
                        'skewcauchy':'a', 
                        'skewnorm':'a', 
                        'pareto':'b', # problem with pareto
                        'exponpow':'b',
                        'rice':'b',
                        'loggamma':'c',
                        'genextreme':'c',
                        'powernorm':'c',
                        'dweibull':'c',
                        'exponnorm':'K',
                        'lognorm':'s',
                        't':'df',
                        'chi':'df',
                        'chi2':'df',
                        'recipinvgauss':'mu',
                        'pearson3':'skew'}
        
        two_params_dict = {'beta':['a', 'b'], 
                           'norminvgauss':['a', 'b'], 
                           'exponweib':['a', 'c'],
                           'burr':['c', 'd'],
                           'powerlognorm':['c', 's'],
                           'f':['dfn', 'dfd'],
                           'nct':['df', 'nc']} # takes extra long to load
                           #'ncx':['df', 'nc']}
        three_params_dict = {'ncf':['dfn','dfd','nc']}

        # CONSIDER change back to 100 bounds bc worked that way
        # even tho all data bounds were set to 200 at the time
        # so the mismatched bounds shouldve cause errors
        # CONSIDER increase bounds to 250 bc noted pat bev bounds=200 so past limit

        # bounds = [(-100, 100), (-100, 100)]
        # #bounds = [(-200, 200), (-200, 200)]
        # if model_name in params_dict.keys():
        #     bounds = [(-100, 100), (-100, 100), (-100, 100)]
        # elif model_name in two_params_dict.keys():
        #     bounds = [(-100, 100), (-100, 100), (-100, 100), (-100, 100)]
        # elif model_name in three_params_dict.keys():
        #     bounds = [(-100, 100), (-100, 100), (-100, 100), (-100, 100), (-100, 100)]
        bounds = [(-250, 250), (-250, 250)]
        if model_name in params_dict.keys():
            bounds = [(-250, 250), (-250, 250), (-250, 250)]
        elif model_name in two_params_dict.keys():
            bounds = [(-250, 250), (-250, 250), (-250, 250), (-250, 250)]
        elif model_name in three_params_dict.keys():
            bounds = [(-250, 250), (-250, 250), (-250, 250), (-250, 250), (-250, 250)]
        #print('bounds: ' + str(bounds))
        sample_fit_results = fit(dist, sample_data, bounds)
        sample_fit_params = sample_fit_results.params
        #print('sample_fit_params: ' + str(sample_fit_params))


        
        dist_param = ''
        #sample_fit_dict = {}
        final_sample_fit_params = ()
        if model_name in params_dict.keys():
            dist_param = params_dict[model_name]

            sample_shape_param = 'sample_fit_params.' + dist_param
            sample_shape = eval(sample_shape_param) #fit_params.c
            sample_loc = sample_fit_params.loc
            sample_scale = sample_fit_params.scale

            #sample_fit_dict = {'shape':sample_shape, 'loc':sample_loc, 'scale':sample_scale}
            final_sample_fit_params = (sample_loc, sample_scale, sample_shape)

        elif model_name in two_params_dict.keys():
            dist_params = two_params_dict[model_name]

            shape_param_1 = 'sample_fit_params.' + dist_params[0]
            shape_param_2 = 'sample_fit_params.' + dist_params[1]
            sample_shape_1 = eval(shape_param_1) #fit_params.c
            sample_shape_2 = eval(shape_param_2)
            sample_loc = sample_fit_params.loc
            sample_scale = sample_fit_params.scale

            #sample_fit_dict = {'shape 1':sample_shape_1, 'shape 2':sample_shape_2, 'loc':sample_loc, 'scale':sample_scale}
            final_sample_fit_params = (sample_loc, sample_scale, sample_shape_1, sample_shape_2)

        elif model_name in three_params_dict.keys():
            dist_params = three_params_dict[model_name]

            shape_param_1 = 'sample_fit_params.' + dist_params[0]
            shape_param_2 = 'sample_fit_params.' + dist_params[1]
            shape_param_3 = 'sample_fit_params.' + dist_params[2]
            sample_shape_1 = eval(shape_param_1) #fit_params.c
            sample_shape_2 = eval(shape_param_2)
            sample_shape_3 = eval(shape_param_3)
            sample_loc = sample_fit_params.loc
            sample_scale = sample_fit_params.scale

            #sample_fit_dict = {'shape 1':sample_shape_1, 'shape 2':sample_shape_2, 'shape 3':sample_shape_3, 'loc':sample_loc, 'scale':sample_scale}
            final_sample_fit_params = (sample_loc, sample_scale, sample_shape_1, sample_shape_2, sample_shape_3)

        elif model_name == 'poisson':
            sample_mu = sample_fit_params.mu
            sample_loc = sample_fit_params.loc

            #sample_fit_dict = {'mu':sample_mu, 'loc':sample_loc}
            final_sample_fit_params = (sample_loc, sample_mu)

        elif model_name == 'binom':
            sample_n = sample_fit_params.n
            sample_p = sample_fit_params.p
            sample_loc = sample_fit_params.loc

            #sample_fit_dict = {'n':sample_n, 'p':sample_p, 'loc':sample_loc}
            final_sample_fit_params = (sample_loc, sample_n, sample_p)
        else:
            sample_loc = sample_fit_params.loc
            sample_scale = sample_fit_params.scale

            #sample_fit_dict = {'loc':sample_loc, 'scale':sample_scale}
            final_sample_fit_params = (sample_loc, sample_scale)
        

        # NEED highest val from all data
        # loop thru all vals, even those not directly hit but surpassed
        highest_val = round_half_up(player_stat_model['max']) #sim_all_data.max #data[-1] # bc sorted
        #print('highest_val: ' + str(highest_val))
        # start at 1 but P(1 or more) = 100 - P(0), where P(0) = P(<0.5)
        # include highest val
        # for val in range(highest_val):
        #     # dist_dict = {'model name':'', 'shape':'', 'loc':'', 'scale':''}
        #     prob = generate_prob_over_from_distrib(val, dist, sample_fit_dict)
        #     probs.append(prob)
        # print('single probs: ' + str(probs))

        vals = np.linspace(0, highest_val-1, highest_val, dtype=int)
        #print('vals: ' + str(vals))
        # probs_less_or_equal = round_half_up(dist.cdf(vals, sample_loc, sample_scale), 5)
        # probs = 1 - probs_less_or_equal

        probs = test_generate_cdf_over(vals, dist, final_sample_fit_params, model_name).tolist()

        #probs = [generate_prob_over_from_distrib(val, dist, sample_fit_dict) for val in range(highest_val)]

    #print('final probs: ' + str(probs))
    return probs











    








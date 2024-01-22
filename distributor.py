# distributor.py
# probability distributions

# binomial distribution
# given samples
# fill in blanks for no samples and low samples

# multinomial distribution

# library still works even though warning
import scipy.stats as ss
import numpy as np
import math # for pi to get prob of x in distrib

# read from csv
# import pandas as pd

# display data
import matplotlib.pyplot as plt

# import sys
# print(sys.path)

import reader # read stat dict data
import converter # round

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

    res = ss.fit(dist, data, bounds) 
    print("res = "+str(res))

    res.plot()
    plt.show()


#multinom_pmf(data)




def plot_cdf(data):
    print('\n===Plot CDF===\n')
    print('data: ' + str(data))

    datasort = sorted(data)

    dist = ss.norm

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
    norm_fit = ss.fit(dist, data, bounds) #dist.fit(data)
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
    dist = ss.norm

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

    res = ss.fit(dist, data, bounds) 
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
    prob = round(dist.pmf(val, loc), 4)
    #print('prob: ' + str(prob))

    if prob > 0.99:
        prob = 0.99
    elif prob < 0.01:
        prob = 0.01
    else:
        prob = converter.round_half_up(prob, 2)

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
    res = ss.fit(dist, data, bounds)
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


player_prob_distribs = generate_player_prob_distribs(player)



    








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
    mean_key = 'mean'
    sample_shape = ''
    sample_mean = ''
    if shape_key in sample_fit_dict.keys():
        sample_shape = sample_fit_dict[shape_key]

        prob_less_or_equal = round(dist.cdf(val, sample_shape, sample_loc, sample_scale), 5)
    else:
        #sample_mean = sample_fit_dict[mean_key] ???

        prob_less_or_equal = round(dist.cdf(val, sample_loc, sample_scale), 5)


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
        prob_less_or_equal = converter.round_half_up(prob_less_or_equal, 3)

    #print('prob_less_or_equal: ' + str(prob_less_or_equal))
    prob_over = converter.round_half_up(1 - prob_less_or_equal, 3) # P(>val+1)
    #prob_over_or_equal_next_val = prob_strict_over

    #print('prob_over: ' + str(prob_over))
    return prob_over

def distribute_all_probs(cond_data, player_stat_model, player='', stat='', condition=''): # if normal dist, avg_scale, dist_name='normal'):
    print('\n===Distribute All Probs===\n')
    print('cond_data: ' + str(cond_data))
    print('player: ' + str(player))
    print('stat: ' + str(stat))
    print('condition: ' + str(condition))
    print('Input: player_stat_model = {model name, sim data, sim avg, sim max} = {name:pareto, data:sim_all_data, avg:a, max:m} = ' + str(player_stat_model))
    print('\nOutput: all_probs = [p1,...]\n')

    probs = [] # 1 to N, list all vals in range in order. or val:prob


    # if only 1 sample, use it as mean, 
    # and simulate 4 more samples to get at least 5 samples (consider 10)
    # get scale of data from other conditions with more samples. easiest to get from 'all' condition
    # use scale to get random samples with loc and scale of data
    # Generate a random dataset
    # if len(data) == 1:
    #     #data = np.random.normal(data[0], avg_scale, 100)
    #     loc = data[0]
    #     if loc == 0:
    #         loc = 0.1
    #     rng = np.random.default_rng()
    #     data = list(rng.poisson(loc, 100))
    #     #print('poisson_data: ' + str(data))
    #     # normal_data = list(rng.normal(data[0], avg_scale, 100))
    #     # print('normal_data: ' + str(normal_data))
    #     # data = normal_data
    
    # # if <5 samples, more accurate to simulate samples with same mean and extrapolated scale
    # # then why not do for all conditions even with >5 samples?
    # # bc scale not same for all conditions
    # elif len(data) < 5:
    #     loc = np.mean(data)
    #     if loc == 0:
    #         loc = 0.1
    #     #data = np.random.normal(loc, avg_scale, 100)
    #     rng = np.random.default_rng()
    #     # data = list(rng.poisson(loc, 100))
    #     # print('simulated data: ' + str(data))

    #     data = list(rng.poisson(loc, 100))
    #     #print('poisson_data: ' + str(data))
    #     # normal_data = list(rng.normal(loc, avg_scale, 100))
    #     # print('normal_data: ' + str(normal_data))
    #     # data = normal_data
    
    # # sort to get highest val and all vals below that
    # data = sorted(data)

    

    # {shape:a, loc:l, scale:s}
    #all_fit_params = player_stat_model.values()[0]
    # all_shape = player_stat_model['shape']
    # all_loc = player_stat_model['loc']
    # all_scale = player_stat_model['scale']



    sim_all_data = player_stat_model['data']
    all_avg = player_stat_model['avg'] #sim_all_data.mean #np.mean(sim_all_data) # ??? should be = all avg but could change to actually = avg?
    print('all_avg: ' + str(all_avg))

    cond_avg = np.mean(cond_data)#ss.fit(dist, data, bounds).params.mu
    print('cond_avg: ' + str(cond_avg))

    sample_data = sim_all_data * (cond_avg / all_avg)

    sample_avg = np.mean(sample_data)
    print('sample_avg: ' + str(sample_avg))
    #print('cond_avg: ' + str(cond_avg))


    model_name = player_stat_model['name']#.keys()[0] #only 1 model per stat
    dist_str = 'ss.' + model_name
    dist = eval(dist_str)

    params_dict = {'gamma':'a',
                    'pareto':'b',
                    'loggamma':'c',
                    'lognorm':'s',
                    't':'df'}

    bounds = [(-200, 200), (-200, 200)]
    if model_name in params_dict.keys():
        bounds = [(-200, 200), (-200, 200), (-200, 200)]
    #print('bounds: ' + str(bounds))
    sample_fit_results = ss.fit(dist, sample_data, bounds)
    sample_fit_params = sample_fit_results.params
    print('sample_fit_params: ' + str(sample_fit_params))


    
    dist_param = ''
    sample_fit_dict = {}
    if model_name in params_dict.keys():
        dist_param = params_dict[model_name]

        sample_shape_param = 'sample_fit_params.' + dist_param
        sample_shape = eval(sample_shape_param) #fit_params.c
        sample_loc = sample_fit_params.loc
        sample_scale = sample_fit_params.scale

        sample_fit_dict = {'shape':sample_shape, 'loc':sample_loc, 'scale':sample_scale}

    else:
        sample_loc = sample_fit_params.loc
        sample_scale = sample_fit_params.scale

        sample_fit_dict = {'loc':sample_loc, 'scale':sample_scale}
    

    # if normal
    #loc, scale = dist.fit(data)
    # if poisson
    #bounds = [(0, 100)]
    
    #print('scale: ' + str(scale))

    # NEED highest val from all data
    # loop thru all vals, even those not directly hit but surpassed
    highest_val = int(converter.round_half_up(player_stat_model['max'])) #sim_all_data.max #data[-1] # bc sorted
    #print('highest_val: ' + str(highest_val))
    # start at 1 but P(1 or more) = 100 - P(0), where P(0) = P(<0.5)
    # include highest val
    for val in range(highest_val):
        #prob = 0
        #if val not in probs.keys():
        # we get prob of exactly 0 and prob >= next val
        # if val == 0:
        #     prob = generate_prob_from_distrib(val, loc, dist)
        #     probs.append(prob)

        # dist_dict = {'model name':'', 'shape':'', 'loc':'', 'scale':''}
        prob = generate_prob_over_from_distrib(val, dist, sample_fit_dict)
        probs.append(prob)

    print('probs: ' + str(probs))
    return probs











    








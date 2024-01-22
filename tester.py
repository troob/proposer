
import scipy.stats as ss
import numpy as np

import tester_reader# import read_player_stat_dict

from distfit import distfit # find best fit

# display data
import matplotlib.pyplot as plt
import time, re, math

# === Helper Functions === 
def round_half_up(n, decimals=0):
    multiplier = 10**decimals
    return math.floor(n * multiplier + 0.5) / multiplier

# test prob distrib
# given small sample size (eg against opponent)
# see which distrib gives reasonable fit

small_data_dict = {'pts':[11, 12], 'reb':[11, 12], 'ast':[0, 1]} # eg rebounds in 2 games against opp
print('small_data_dict: ' + str(small_data_dict))
#dist = ss.lognorm

sample_size = 10000
stats_of_interest = ['pts']#, 'reb', 'ast']

# get scale from all samples
player = 'clint capela'
player_stat_dict = tester_reader.read_player_stat_dict(player)


# get data across multiple seasons to get enough samples to fit consistently
all_data_dict = {} # key by stat anme
for year, year_stat_dict in player_stat_dict.items():
    for part, part_stat_dict in year_stat_dict.items():
        
        for stat_name, stat_dict in part_stat_dict.items():

            if stat_name in stats_of_interest:
                #print('\nstat_name: ' + stat_name)

                condition = 'all'
                condition_stat_dict = stat_dict[condition]
                condition_stat_data = list(condition_stat_dict.values())

                if stat_name not in all_data_dict.keys():
                    all_data_dict[stat_name] = []

                all_data_dict[stat_name].extend(condition_stat_data)

print('all_data_dict: ' + str(all_data_dict))

#for year, year_stat_dict in player_stat_dict.items():
year = '2023' # last full season
year_stat_dict = player_stat_dict[year]
part = 'regular'
part_stat_dict = year_stat_dict[part]
for stat_name, stat_dict in part_stat_dict.items():

    #stat_name = 'reb'
    #stat_dict = part_stat_dict[stat_name]

    if stat_name in stats_of_interest:
        print('\nstat_name: ' + stat_name)

        small_data = small_data_dict[stat_name]
        small_avg = np.mean(small_data)
        print('small_avg: ' + str(small_avg))

        condition = 'all'
        condition_stat_dict = stat_dict[condition]
        all_data = np.sort(all_data_dict[stat_name])#np.sort(list(condition_stat_dict.values()))
        print('all_data: ' + str(all_data))
        num_samples = len(all_data)
        print('num_samples: ' + str(num_samples))
        all_avg = np.mean(all_data)
        #all_var = np.var(all_data)
        # print('all_loc: ' + str(all_loc))

        # # need std dev for normal distrib
        # scale = np.std(all_data) # eg 5 for rebounds
        # print('scale: ' + str(scale))


        #print('\n===Find Best Fit===\n')
        # Initialize
        dfit = distfit(distr=['gamma','loggamma', 'pareto', 't'])

        # Search for best theoretical fit on your empirical data
        # model_results: {'model': {'name': 'loggamma', 'score': 0.002701250960026347, 'loc': -789.9132427398613, 'scale': 120.10481575160037, 'arg': (794.0689856756094,), 'params': (794.0689856756094, -789.9132427398613, 120.10481575160037), ...
        model_results = dfit.fit_transform(all_data)
        print('model_results: ' + str(model_results))
        model = model_results['model']
        model_name = model['name']
        model_loc = model['loc']
        model_scale = model['scale']
        model_arg = model['arg']
        model_params = model['params']

        print('\n===Model Name: ' + str(model_name))

        #pdf_fit = dfit.pdf()

        # use model name to get dist code
        dist_str = 'ss.' + model_name
        dist = eval(dist_str)

        # now the params depend on the best fit distrib
        # if Poisson: param: lam = mean
        # if Normal: params: mu = mean, sigma = std dev
        # if Gamma: params: a = shape, scale = 1 / rate (b = rate)
        # if Pareto: param: b = shape
        # if Weibull: params: c = shape
        
        # see what happens if i set 3 bounds for optional params even for distribs that only take 1 param
        #bounds = [(0, 100), (0, 100), (0, 100)]#[(-100, 100), (-100, 100)]
        bounds = [(-200, 200), (-200, 200), (-200, 200)]
        # if re.search('log', model_name):
        #     bounds = [(-1000, 1000), (-1000, 1000), (-1000, 1000)]
        print('bounds: ' + str(bounds))

        # for single param distribs:
        # if model_name == 'dweibull' or model_name == 'pareto' or model_name == 'poisson':
        #     bounds = [(0, 100)]
        # # for 2 param distribs:
        # elif model_name == 'norm' or model_name == 'lognorm':
        #     bounds = [(0, 100), (0, 100)]
        
        # Before passing to fit fcn, 
        # For small sample sizes: simulate samples
        # by taking mean from small sampleset,
        # AND variance from large set
        #print('all_data: ' + str(all_data))
        all_fit_results = ss.fit(dist, all_data, bounds) #dist.fit(data)
        #small_fit_results = ss.fit(dist, small_data, bounds)
        
        plt.figure()
        all_fit_results.plot()
        # plt.figure()
        # small_fit_results.plot()

        all_fit_params = all_fit_results.params
        #print('all_fit_params: ' + str(all_fit_params))
        # small_fit_params = small_fit_results.params
        # print('small_fit_params: ' + str(small_fit_params))

        # gen data from combo of small and all data fit params
        rng = np.random.default_rng()
        

        # get prob of 0
        test_val = 3
        print('test_val: ' + str(test_val))

        # dists use shape param but different letters
        params_dict = {'gamma':'a',
                       'pareto':'b',
                       'loggamma':'c'}
        dist_param = ''
        all_shape = 0
        all_loc = 0
        all_scale = 1
        if model_name in params_dict.keys():
            dist_param = params_dict[model_name]

            shape_param = 'all_fit_params.' + dist_param
            all_shape = eval(shape_param) #fit_params.c
            all_loc = all_fit_params.loc
            all_scale = all_fit_params.scale
            all_prob = round(dist.pdf(test_val, all_shape, all_loc, all_scale), 4)
            all_prob_cdf = round(dist.cdf(test_val, all_shape, all_loc, all_scale), 4)

            #samples = []
            print('all_data: ' + str(all_data))

            print('all_avg: ' + str(all_avg))
            
            
            
            sim_all_data = np.sort(dist.rvs(all_shape, all_loc, all_scale, size=sample_size))
            sim_avg = np.mean(sim_all_data)
            print('sim_avg: ' + str(sim_avg))
            sim_fit_results = ss.fit(dist, sim_all_data, bounds)
            sim_fit_params = sim_fit_results.params
            sim_shape_param = 'sim_fit_params.' + dist_param
            sim_shape = eval(sim_shape_param) #fit_params.c
            sim_loc = sim_fit_params.loc
            sim_scale = sim_fit_params.scale
            sim_prob = round(dist.pdf(test_val, sim_shape, sim_loc, sim_scale), 4)
            sim_prob_cdf = round(dist.cdf(test_val, sim_shape, sim_loc, sim_scale), 4)
            plt.figure()
            sim_fit_results.plot()
            # for data_val in sim_all_data:
            #     sample_val = int(round_half_up(data_val * small_avg / all_avg))
            #     samples.append(sample_val)
            #samples = np.array(samples)
            
            sample_data = sim_all_data * (small_avg / all_avg)
            sample_avg = np.mean(sample_data)
            print('sample_avg: ' + str(sample_avg))
            print('small_avg: ' + str(small_avg))

            #print('\nsamples: ' + str(samples))

            sample_fit_results = ss.fit(dist, sample_data, bounds)
            sample_fit_params = sample_fit_results.params
            print('\nall_fit_params: ' + str(all_fit_params))
            print('sim_fit_params: ' + str(sim_fit_params))
            print('sample_fit_params: ' + str(sample_fit_params))

            sample_shape_param = 'sample_fit_params.' + dist_param
            sample_shape = eval(sample_shape_param) #fit_params.c
            sample_loc = sample_fit_params.loc
            sample_scale = sample_fit_params.scale
            sample_prob = round(dist.pdf(test_val, sample_shape, sample_loc, sample_scale), 4)
            sample_prob_cdf = round(dist.cdf(test_val, sample_shape, sample_loc, sample_scale), 4)


            print('all_prob: ' + str(all_prob))
            print('sim_prob: ' + str(sim_prob))
            print('sample_prob: ' + str(sample_prob))
            print('\nall_prob_cdf: ' + str(all_prob_cdf))
            print('sim_prob_cdf: ' + str(sim_prob_cdf))
            print('sample_prob_cdf: ' + str(sample_prob_cdf))

            plt.figure()
            sample_fit_results.plot()

            
            # small_shape_param = 'small_fit_params.' + dist_param
            # small_shape = eval(small_shape_param) #fit_params.c
            # small_loc = small_fit_params.loc
            # small_scale = small_fit_params.scale

            # sample_size = 100
            # # gen_dist_str = 'rng.' + model_name + '(all_shape, all_loc, all_scale, sample_size)'
            # # gen_data = list(eval(gen_dist_str))
            # altered_shape = 0
            # altered_loc = all_loc
            # altered_scale = 0
            # # If Gamma
            # # E = shape / scale, get mean from small set
            # # V = shape / scale^2, get variance from all set
            # if model_name == 'loggamma':
            #     altered_shape = small_avg**2 / all_var
            #     print('altered_shape: ' + str(altered_shape))
            #     altered_scale = small_avg / all_var
            #     print('altered_scale: ' + str(altered_scale))

            #R = dist.rvs(altered_shape, altered_loc, altered_scale, size=sample_size)  # r = loggamma.rvs(c, size=1000)
            
            
            
            # samples = []
            # # for rv in R:
            # #     if rv < 0:
            # #         rv = 0
            # #     samples.append(int(round_half_up(rv)))
            # # samples = np.sort(samples)
            # # print("Random Variates:\n", samples) 
            # print('all_data: ' + str(all_data))
            # print('small_avg: ' + str(small_avg))
            # print('all_avg: ' + str(all_avg))
            # for val in all_data:
            #     sample_val = int(round_half_up(val * small_avg / all_avg))
            #     samples.append(sample_val)

            # samples = np.array(samples)
            # print('samples: ' + str(samples))
            # min_val = min(samples)
            # print('min_val: ' + str(min_val))
            # max_val = max(samples)
            # print('max_val: ' + str(max_val))

            




            # now that we have shape of large sample size
            # simulate samples for small sample sizes
            # by using mean of small set and shape of large set
            # prob_small_cdf = 0
            # if model_name == 'dweibull':
            #     altered_loc = small_avg
            #     prob_small_cdf = round(dist.cdf(val, all_shape, altered_loc, all_scale), 4)

            # # compute scale param?
            # # altered_scale = small_avg * ( ( shape - 1 ) / shape )
            # # print('altered_scale: ' + str(altered_scale))
            
            # # compute proportional shift in loc by shift in mean
            # else:
            # print('small_avg: ' + str(small_avg))
            # print('all_avg: ' + str(all_avg))
            # print('all_loc: ' + str(all_loc))
            # altered_loc = all_loc * small_avg / all_avg
            # print('altered_loc: ' + str(altered_loc))
            # if re.search('log', model_name):
            #     altered_loc = math.exp(altered_loc)
            # # if all_loc < 0:
            # #     altered_loc *= -1
            #     print('altered_loc: ' + str(altered_loc))
            # prob_small_cdf = round(dist.cdf(val, all_shape, altered_loc, all_scale), 4)
            
        
        # if poisson, use pmf
        # elif model_name == 'poisson':
        #     lam = fit_params.lam
        #     prob = round(dist.pmf(val, lam), 4)

        # elif model_name == 'norm' or model_name == 'lognorm':
        #     mu = fit_params.mu
        #     sigma = fit_params.scale
        #     prob = round(dist.pdf(val, mu, sigma), 4)

        else:
            print('Unknown distrib: ' + model_name)
            # shape = fit_params.shape
            # loc = fit_params.loc
            # scale = fit_params.scale
            # prob = dist.pdf(val, shape, loc, scale)

        #prob = round(prob, 4)
        

        

        
        # pdf_fit = dist_fit.pdf(all_data)
        # plt.figure()
        # plt.xlabel('Data')
        # plt.ylabel('PDF')
        # plt.title('PDF of Fitted Normal Distribution')
        # plt.plot(all_data, pdf_fit)

        #cdf_fit = dist_fit.cdf(all_data)
        # plt.figure()
        # plt.xlabel('Data')
        # plt.ylabel('CDF')
        # plt.title('CDF of Fitted Normal Distribution')
        # plt.plot(all_data, cdf_fit)


plt.show()


# Plot
# dfit.plot()
# # Make plot
# dfit.plot_summary()

# Make prediction
# y = [0,1,2,3,4,5,6]
# predict_results = dfit.predict(y)
# print('predict_results:\n' + str(predict_results))
# print('predict_results[df]:\n' + str(predict_results['df']))

# Plot results with CII and predictions.
# plot_results = dfit.plot()
# print('plot_results: ' + str(plot_results))

# plt.figure()
# plt.plot(fig, ax)
# plt.show()






# sample_size = 100

# # logsample = ss.norm.rvs(loc=loc, scale=scale, size=sample_size)
# # print('logsample: ' + str(logsample))

# # restrict samples to bounds 
# # OR just adjust prob

# rng = np.random.default_rng()
# #data = list(rng.poisson(lam=loc, size=sample_size))
# # ===Normal Distribution===
# normal_data = list(rng.normal(loc=loc, scale=scale, size=sample_size))
# #print('normal data: ' + str(normal_data))
# min_val = min(normal_data)
# print('normal min_val: ' + str(min_val))
# max_val = max(normal_data)
# print('normal max_val: ' + str(max_val))

# # ===Lognormal Distribution===
# print('\n===Lognormal Distribution===\n')
# lognorm_sample = np.exp(normal_data)

# shape, loc, scale = ss.lognorm.fit(lognorm_sample, floc=0) # hold location to 0 while fitting
# print('lognorm shape: ' + str(shape))
# print('lognorm loc: ' + str(loc))
# print('lognorm scale: ' + str(scale))

# mu = np.log(scale)
# print('lognorm mu: ' + str(mu))
# sigma = shape
# print('lognorm sigma: ' + str(sigma))

# # ===Gamma Distribution===
# print('\n===Gamma Distribution===\n')
# dist = ss.gamma
# bounds = [(-100, 100), (0, 0), (-100, 100)]
# # shape = # of events modeling (eg 10 rebounds in a game). Is it like mean??? no bc rate is avg
# # scale = mean time bt events. 
# # rate = 1/scale = mean rate in 1 unit time (eg 10 reb per game avg)

# small_fit_1 = dist.fit(data, floc=0)
# print('small_fit 1: ' + str(small_fit_1))
# small_fit_2 = ss.fit(dist, data, bounds).params
# print('small_fit 2: ' + str(small_fit_2))
# all_fit_1 = dist.fit(all_data, floc=0)
# print('all_fit 1: ' + str(all_fit_1))
# all_fit_2 = ss.fit(dist, all_data, bounds).params
# print('all_fit 2: ' + str(all_fit_2))
# all_fit_2_rate = 1 / all_fit_2.scale
# print('all_fit 2 rate: ' + str(all_fit_2_rate))

# # using fit method 1
# gamma_data_1 = list(rng.gamma(shape=all_fit_1[0], scale=all_fit_1[2], size=sample_size))
# # using fit method 2
# gamma_data_2 = list(rng.gamma(shape=small_fit_2.a, scale=small_fit_2.scale, size=sample_size))
# final_gama_data = []
# for val in gamma_data_2:
#     val = round(val)
#     final_gama_data.append(val)
# print('gamma_data: ' + str(final_gama_data))
# min_val = min(final_gama_data)
# print('gamma min_val: ' + str(min_val))
# max_val = max(final_gama_data)
# print('gamma max_val: ' + str(max_val))

# print('upper_bound: ' + str(upper_bound))
# bounds = [(0, upper_bound), (0, upper_bound)]

# # If Log Normal:
# data = np.exp(data)
# res = ss.fit(dist, data, bounds).params#.mu
# print('res: ' + str(res))
# shape = res.s
# print('shape: ' + str(shape))
# loc = res.loc
# print('loc: ' + str(loc))
# scale = res.scale
# print('scale: ' + str(scale))




# get probs of each unique val in bounds
#high_val = max(all_data)
# upper bound depends on stat, based on expected maximum possible value
# we know based on human limits and all past samples of all players
#upper_bound = 20



# #high_sample_size = 10000
# rng = np.random.default_rng()
# data = dist.rvs(mu, sigma, sample_size)
# print('data: ' + str(data))

# val = 3
# prob_samples = round(dist.pdf(val, shape, loc, scale), 4)
# print('prob_samples: ' + str(prob_samples))




# If Poisson: just needs mean
#loc = np.mean(data)

# If Normal: needs mean and dev
# res = ss.fit(dist, data, bounds).params#.mu
# print('res: ' + str(res))
# loc = res.loc
# print('loc: ' + str(loc))
# scale = res.scale
# print('scale: ' + str(scale))



# If Poisson:
# loc = np.mean(data)
# print('loc: ' + str(loc))

# If Normal:
# res = ss.fit(dist, data, bounds).params#.mu
# print('res: ' + str(res))
# loc = res.loc
# print('loc: ' + str(loc))
# scale = res.scale
# print('scale: ' + str(scale))
# high_loc = np.mean(high_data)
# print('high_loc: ' + str(high_loc))



# prob_high_samples = round(dist.pmf(val, high_loc), 4)
# print('prob_high_samples: ' + str(prob_high_samples))
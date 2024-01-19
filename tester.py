
import scipy.stats as ss
import numpy as np

import tester_reader# import read_player_stat_dict

from distfit import distfit # find best fit

# display data
import matplotlib.pyplot as plt
import time

# test prob distrib
# given small sample size (eg against opponent)
# see which distrib gives reasonable fit

small_data = [11, 12] # eg rebounds in 2 games against opp
print('small_data: ' + str(small_data))
#dist = ss.lognorm

small_avg = np.mean(small_data)
print('small_avg: ' + str(small_avg))

# get scale from all samples
player = 'clint capela'
player_stat_dict = tester_reader.read_player_stat_dict(player)


#for year, year_stat_dict in player_stat_dict.items():
year = '2023' # last full season
year_stat_dict = player_stat_dict[year]
part = 'regular'
part_stat_dict = year_stat_dict[part]
stats_of_interest = ['pts', 'reb', 'ast']
for stat_name, stat_dict in part_stat_dict.items():
    print('\nstat_name: ' + stat_name)
    #stat_name = 'reb'
    #stat_dict = part_stat_dict[stat_name]
    if stat_name in stats_of_interest:
        condition = 'all'
        condition_stat_dict = stat_dict[condition]
        all_data = np.sort(list(condition_stat_dict.values()))
        # all_loc = np.mean(all_data)
        # print('all_loc: ' + str(all_loc))

        # # need std dev for normal distrib
        # scale = np.std(all_data) # eg 5 for rebounds
        # print('scale: ' + str(scale))


        #print('\n===Find Best Fit===\n')
        # Initialize
        dfit = distfit()

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
        print('model_name: ' + str(model_name))

        #pdf_fit = dfit.pdf()

        # use model name to get dist code
        dist_str = 'ss.' + model_name
        dist = eval(dist_str)

        # now the params depend on the best fit distrib
        # if Poisson: param: lam = mean
        # if Normal: params: mu = mean, sigma = std dev
        # if Gamma: params: a = shape, scale = 1 / rate (b = rate)
        bounds = [(-100, 100), (-100, 100)]
        
        # Before passing to fit fcn, 
        # For small sample sizes: simulate samples
        # by taking mean from small sampleset,
        # AND variance from large set
        dist_fit = ss.fit(dist, all_data, bounds) #dist.fit(data)
        
        pdf_fit = dist_fit.pdf(all_data)
        plt.figure()
        plt.xlabel('Data')
        plt.ylabel('PDF')
        plt.title('PDF of Fitted Normal Distribution')
        plt.plot(all_data, pdf_fit)

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
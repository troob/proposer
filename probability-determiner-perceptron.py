# probability-determiner-perceptron.py
# compute stats and learn from them

# import for linear regression
import matplotlib.pyplot as plt 
from scipy import stats
# import for polynomial regression
import numpy
# import for r squared in polynomial regress
from sklearn.metrics import r2_score

#x = ['wsh','wsh','chi','chi','chi'] # get list of player stats
# do we need to represent team as id number or can we use abbrev?
x = [1,1,2,2,2]
y = [10,10,3,4,5]

# mean, median, mode

# standard deviation, variance

# percentile

# scatter plot

# use basic regression for numerical data like game num in season, comparing bt seasons:
# linear regression
print('\n===Linear Regression===\n')
slope, intercept, r, p, std_err = stats.linregress(x, y)

def myfunc(x):
    return slope * x + intercept

mymodel = list(map(myfunc, x))

#plt.scatter(x, y)
#plt.plot(x, mymodel)
#plt.show()

print('coefficient of correlation: ' + str(r))

# predict assists based on opponent
team_num = 1
assists = myfunc(team_num)
print('assists against team ' + str(team_num) + ': ' + str(assists))

# then predict assists, based on each condition separately, and then array of conditions together



# polynomial regression
print('\n===Polynomial Regression===\n')
mymodel = numpy.poly1d(numpy.polyfit(x, y, 3))

myline = numpy.linspace(1, 2, 100)

# r squared
print('r2 score: ' + str(r2_score(y, mymodel(x))))

assists = mymodel(team_num)
print('assists against team ' + str(team_num) + ': ' + str(assists))

plt.scatter(x, y)
plt.plot(myline, mymodel(myline))
plt.show()



# multiple regression, so we can predict based on multiple variables



# todo: categorical data like opponent name

# todo: compare predicted value from regression based on conditions vs predicting next stat value in sequence given past stat vals
# see predicting next word in text for similarity with predicting sequence
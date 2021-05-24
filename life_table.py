# 2017 CDC life tables, most recent
# life tables

'''
in order to use, note that life_table[x] gives the probability of dying
between ages x and x+1
'''

import general_functions as gf

life_table = [
    0.005777,
    0.000382,
    0.000248,
    0.000193,
    0.000149,
    0.000141,
    0.000126,
    0.000114,
    0.000104,
    0.000095,
    0.000093,
    0.000103,
    0.000133,
    0.000186,
    0.000258,
    0.000338,
    0.000421,
    0.000510,
    0.000603,
    0.000698,
    0.000795,
    0.000889,
    0.000970,
    0.001032,
    0.001080,
    0.001123,
    0.001165,
    0.001207,
    0.001252,
    0.001300,
    0.001351,
    0.001402,
    0.001454,
    0.001506,
    0.001556,
    0.001615,
    0.001679,
    0.001740,
    0.001798,
    0.001860,
    0.001936,
    0.002036,
    0.002160,
    0.002306,
    0.002470,
    0.002647,
    0.002846,
    0.003079,
    0.003357,
    0.003682,
    0.004030,
    0.004401,
    0.004820,
    0.005285,
    0.005778,
    0.006284,
    0.006794,
    0.007319,
    0.007869,
    0.008456,
    0.009093,
    0.009768,
    0.010467,
    0.011181,
    0.011922,
    0.012710,
    0.013621,
    0.014620,
    0.015770,
    0.017100,
    0.018428,
    0.020317,
    0.022102,
    0.024194,
    0.026342,
    0.029042,
    0.032001,
    0.035443,
    0.039257,
    0.043393,
    0.048163,
    0.053216,
    0.059240,
    0.066564,
    0.074045,
    0.081954,
    0.090879,
    0.101938,
    0.114075,
    0.127331,
    0.141733,
    0.157289,
    0.173986,
    0.191788,
    0.210633,
    0.230432,
    0.251066,
    0.272395,
    0.294253,
    0.316456,
    1.000000]

def get_monthly_death_probability(age_in_MONTHS):
    # age in years will be mod 12, so 23 months of age is age 1
    # this will be the index that we use for the list as well
    assert(age_in_MONTHS < (12*100))
    index_years = age_in_MONTHS//12
    prob_annual = life_table[index_years]
    prob_monthly = gf.annual_prob_to_monthly(prob_annual) 
    print(prob_monthly)
    return prob_monthly


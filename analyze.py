import json
import csv
import re
import numpy, math

#from pprint import pprint

"""
Means, standard deviations of the estimated rates of progress by condition
"""

def conf_interval(samp_size, mean, std, conf_level):
    SE = std/(math.sqrt(samp_size))
    alpha = 1 - conf_level/100
    p = 1 - alpha/2
    df = samp_size - 1
    print '\t standard error: ' + str(SE) + ' prob is: ' + str(p) + ' df: ' + str(df)

with open('resources/OptimismControlExperiment.csv') as data_file:
    datareader = csv.reader(data_file)
    first = True

    means = {'optimism':[0,0], 'pessimism': [0,0], 'realism': [0,0]}
    stds = {'optimism':[[],[]], 'pessimism': [[],[]], 'realism': [[],[]]}
    counter = 0

    re_float = re.compile(r'\d*\.?\d+')

    for row in datareader:
        if first:   #skips first line
            first = False
            continue
        first_sec, second_sec  = row[10], row[-2]
        parsed_first = json.loads(first_sec)
        parsed_second = json.loads(second_sec)
        responses = json.loads(parsed_second['responses'])
        condition = parsed_first['condition']
        true_rate = float(parsed_first['bin_p']) * 100
        q0 = responses['Q0']
        q1 = responses['Q1']

        ans1 = re.findall(re_float, q0)
        if len(ans1)>0: ans1 = ans1[0]
        ans2 = re.findall(re_float, q1)
        if len(ans2)>0: ans2 = ans2[0]

        try:
            if (0 <= int(ans1) <= 100) and (0 <= int(ans2) <= 100):
                #print 'estimated is ' + ans1 + ' and true is ' + str(true_rate)
                means[condition][0] += (float(ans1) - true_rate)
                means[condition][1] += (float(ans2) - 0)
                counter+=1
                stds[condition][0].append(int(ans1))
                stds[condition][1].append(int(ans2))
        except:
            pass
    for i in means.keys():
        first_mean = means[i][0]/counter
        second_mean = means[i][1]/counter
        print 'Mean difference for q1 (' + i + '): ' + str(first_mean) + ' and q2: ' + str(second_mean)
        first_std = 0
        second_std = 0
        for j in stds[i][0]:
             first_std += (j - first_mean)**2
        for j in stds[i][1]:
            second_std += (j - second_mean)**2
        first_std = math.sqrt(first_std/counter)
        second_std = math.sqrt(second_std/counter)
        print '\tstd for q1: ' + str(first_std) + ' and q2: ' + str(second_std)
        conf_interval(counter, first_mean, first_std, 95)
        conf_interval(counter, second_mean, second_std, 95)


#confidence interval using sample error, not mean

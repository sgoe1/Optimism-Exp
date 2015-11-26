import json
import csv
import re
import numpy, math

#from pprint import pprint

"""
Means, standard deviations of the estimated rates of progress by condition
"""

#CONF_INTERVAL
tscore = 1.997 #using online calculator-  CHANGE if confidence interval desired also changes OR
               #degrees of freedom changes, WHICH IT DOES for different sized n

def median(lst):
    return numpy.median(numpy.array(lst))

def conf_interval(samp_size, mean, std, conf_level):
    SE = float(std/(math.sqrt(samp_size)))
    alpha = 1 - float(conf_level)/100
    p = 1 - alpha/2
    df = float(samp_size - 1)
    print '\t standard error: ' + str(SE) + ' prob is: ' + str(p) + ' df: ' + str(df)
    return SE

file_path = 'resources/DataOptimismCorrectedPilot3.csv'
with open(file_path, 'rU') as data_file:
    datareader = csv.reader(data_file)
    first = True

    # maybe go back and simplify this redundancy with horizons
    # means = {'optimism':[0,0], 'pessimism': [0,0], 'realism': [0,0]}
    # stds = {'optimism':[[],[]], 'pessimism': [[],[]], 'realism': [[],[]]}
    # counter = {'optimism': 0, 'pessimism': 0, 'realism': 0}
    means = {'realism': [0,0]}
    stds = {'realism': [[],[]]}
    counter = {'realism': 0}

    means_horzn = {}
    counter_horzn = {}
    total_time_elapsed = []

    re_float = re.compile(r'\d*\.\d+|\d+')

    for row in datareader:
        if first:   #skips first line
            first = False
            continue
        first_sec, second_sec  = row[10], row[-1]
        participant = row[4]
        parsed_first = json.loads(first_sec)
        parsed_second = json.loads(second_sec)
        responses = json.loads(parsed_second['responses'])
        condition = parsed_first['condition']
        condition_probs = parsed_first['condition_probs']
        true_rate = float(parsed_first['bin_p']) * 100
        time_horizon = int(parsed_first['goal_timestep'])
        q0 = responses['Q0']
        q1 = responses['Q1']
        time_elapsed = float(parsed_second['time_elapsed'])

        ans1 = re.findall(re_float, q0)
        if len(ans1)>0: ans1 = ans1[0]
        ans2 = re.findall(re_float, q1)
        if len(ans2)>0: ans2 = ans2[0]

        try:
            if (0 <= int(ans1) <= 100) and (0 <= int(ans2) <= 100):
                # ans1, ans2, true_rate parsed correctly - !! fix parsing of decimal answers
                # print 'ans1 is ' + ans1 + ' ans2 is ' + ans2 + 'and true rate is ' + str(true_rate)
                means[condition][0] += float(ans1)
                means[condition][1] += float(ans2)
                counter[condition]+=1
                stds[condition][0].append(float(ans1))
                stds[condition][1].append(float(ans2))

                total_time_elapsed.append(time_elapsed)

                m = (condition, time_horizon, true_rate, condition_probs[condition])
                if m not in means_horzn:
                    means_horzn[m] = float(ans1)
                    counter_horzn[m] = 1
                else:
                    means_horzn[m] += float(ans1)
                    counter_horzn[m] += 1

            else:
                print 'Skipped ' + q0  + ' and ' + q1
        except:
            print 'Skipped ' + q0  + ' and ' + q1
            #pass
    print "RESULTS FOR: " + file_path
    for i in means.keys():
        means[i][0] = first_mean = means[i][0]/counter[i]
        means[i][1] = second_mean = means[i][1]/counter[i]
        print 'Mean difference for (' + i + ') q1: ' + str(first_mean) + ' and q2: ' + str(second_mean)
        first_std = 0
        second_std = 0
        for j in stds[i][0]:
             first_std += (j - first_mean)**2
        for j in stds[i][1]:
            second_std += (j - second_mean)**2
        first_std = math.sqrt(first_std/counter[i])
        second_std = math.sqrt(second_std/counter[i])
        stds[i] = (first_std, second_std)
        print '\tstd for q1: ' + str(first_std) + ' and q2: ' + str(second_std)
        se1 = conf_interval(counter[i], first_mean, first_std, 95)
        se2 = conf_interval(counter[i], second_mean, second_std, 95)
        margin_of_error1 = tscore * se1
        margin_of_error2 = tscore * se2
        print '\t Error margin  q1= '+ str(tscore) + ' * ' + str(se1) + ": " + str(margin_of_error1)
        print '\t Error margin q2= '+ str(tscore) + ' * ' + str(se2) + ": " + str(margin_of_error2)
        print "Q1 has interval [" + str(first_mean - margin_of_error1) +  "," + str(first_mean + margin_of_error1) + "] and Q2 has interval[" + str(second_mean - margin_of_error2) + "," + str(second_mean + margin_of_error2)   + "]"
        print "================================="
    #confidence interval using sample error, not mean
    #T - TEST stuff
    #no loops because need to hardcode some stuff
    print 'Median of time elapsed (in milliseconds):' + str(median(total_time_elapsed))

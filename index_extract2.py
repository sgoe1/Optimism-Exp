import json
import csv
import re
import numpy, math

#from pprint import pprint

inputfilename='../Data/MainExperiment2.csv'
outputfilename='../Data/MainExperiment2KeyVariables.csv'

with open(outputfilename, 'w', newline='') as csvfile:
    cleanedwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
    cleanedwriter.writerow(['Participant', 'Assignment ID', 'Completion Time (Min)', 'Condition', 'Time Horizon', 'Number of investments','Final Rate of Dev.', 'Money at end of game', 'Est. rate of dev. for investing', 'Est. rate of dev. for marketing', 'Bonus ($)'])

    with open(inputfilename, 'rU') as data_file:
        datareader = csv.reader(data_file)
        first = True

        # maybe go back and simplify this redundancy with horizons
        means = {'optimism':[0,0], 'pessimism': [0,0], 'realism': [0,0]}
        stds = {'optimism':[[],[]], 'pessimism': [[],[]], 'realism': [[],[]]}
        counter = {'optimism': 0, 'pessimism': 0, 'realism': 0}

        means_horzn = {}
        counter_horzn = {}

        re_float = re.compile(r'\d*\.\d+|\d+')
        r=0
        for row in datareader:
            r+=1
            if first:   #skips first line
                first = False
                continue
            first_sec = row[10]
            for i in range(len(row)):
                if row[i] == '':
                    second_sec = row[i-1]
                    last_index = i-1
                    break
            num_invest = 0
            for i in range(8, last_index):
                parsed = json.loads(row[i])
                try:
                    if parsed['type'] == 'real_experiment' and parsed['action'] == 'invest':
                        num_invest += 1
                except:
                    pass
            participant = row[4]
            assignment_id = row[3]
            parsed_first = json.loads(first_sec)
            parsed_second = json.loads(second_sec)
            responses = json.loads(parsed_second['responses'])
            condition = parsed_first['condition']
            init_money = int(parsed_first['init_money'])
            goal_timestep = parsed_first['goal_timestep']
            invest_mean = parsed_first['invest_mean']
            market_mean = parsed_first['big_mean']
            condition_probs = parsed_first['condition_probs']
            true_rate = float(parsed_first['bin_p']) * 100
            time_horizon = int(parsed_first['goal_timestep'])
            completion_time = round(float(parsed_second['time_elapsed'])/(1000 * 60), 2)
            last_trial = json.loads(row[last_index - 2])
            final_rate_of_dev = int(last_trial['curr_stage'])
            money_at_end = int(last_trial['money'])
            bonus_dollars = min(1, (money_at_end - init_money)/(0.2*goal_timestep*market_mean + 0.8*goal_timestep*invest_mean))

            q0 = responses['Q0']
            q1 = responses['Q1']

            ans1 = re.findall(re_float, q0)
            if len(ans1)>0: ans1 = ans1[0]
            ans2 = re.findall(re_float, q1)
            if len(ans2)>0: ans2 = ans2[0]

            try:
                if (0 <= int(ans1) <= 100) and (0 <= int(ans2) <= 100):

                    cleanedwriter.writerow([participant, assignment_id, completion_time, condition, time_horizon, num_invest,
                                            final_rate_of_dev, money_at_end, q0, q1, bonus_dollars])
                else:
                    print('Skipped ' + q0  + ' and ' + q1)
            except:
                print('Skipped ' + q0  + ' and ' + q1)

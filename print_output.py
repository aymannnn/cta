from numpy import character
import cohort
import csv
from efficiency_frontier.efficiency_frontier import calculate_frontier
import copy

def print_counters(strategies_key, strategies):
    # strategy will be the row, and column will be the states
    empty = cohort.Cohort(s_strategy='printing', age=100) #placeholder for age
    empty_counters = empty.counters
    empty_counters['strategy'] = 'placeholder'
    fieldnames = empty_counters.keys()
    with open('results/counters.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key in strategies_key:
            # add on the strategy
            counters = strategies[key].counters
            counters['strategy'] = key
            writer.writerow(counters)
    return

def print_states(strategies_key, strategies):
    # strategy will be the' row, and column will be the states 
    empty = cohort.Cohort(s_strategy='printing', age = 100) # placeholder
    empty_states = empty.states
    empty_states['strategy'] = 'placeholder'
    fieldnames = empty_states.keys()
    with open('results/states.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key in strategies_key:
            # add on the strategy
            states = strategies[key].states
            states['strategy'] = key
            writer.writerow(states)
    return

def get_frontier_data(strategies):
    data = []
    for key in strategies:
        data.append([
            key, 
            strategies[key].counters['final.qaly.per.mult'],
            strategies[key].counters['final.cost.per.mult']
            ])
    return data

def print_base_case(strategies_key, strategies):
    print_counters(strategies_key, strategies)
    print_states(strategies_key, strategies)
    data_for_frontier = get_frontier_data(strategies)
    calculate_frontier(
        data = data_for_frontier,
        print_original=True,
        path_to_print_original='results/original_strategies.csv',
        path_to_frontier_output= 'results/frontier_strategies.csv',
        path_to_graph='results/graph'
    )
    return

def get_sa_data(strategies_key, strategies, optimal, val = None, psa = False):
    '''
    had to redo everything to get the strategies key so that it is 
    in the right order every single time
    '''
    if (val == None) and (psa == False):
        print("ERROR, SA/PSA but no value or psa defined")
        return
    if psa == False:
        sa_data = [val]
    else:
        sa_data = []
    for key in strategies_key:
        sa_data.append(
            strategies[key].counters['final.qaly.per.mult']
        )
        sa_data.append(
            strategies[key].counters['final.cost.per.mult']
        )
    if psa == True:
        sa_data += optimal # optimal is a list in this case
    else:
        sa_data.append(optimal)
    return sa_data

def get_sa_header(strategies_key, psa = False):
    if psa == True:
        header = []
    else:
        header = ['value']
    for key in strategies_key:
        header.append(key + '_cost')
        header.append(key + '_qaly')
    if psa == True:
        # dividing up 200,000 into increments of 10,000
        # sorry for magic numbers
        for i in range(1, 21):
            threshold = i*10000
            threshold_string = str(threshold)
            header.append('WTP threshold: ' + threshold_string)
    else:
        header.append('optimal')
    return header

def print_single_sa_run(strategies_key, strategies, val = None, psa = False):
    data = get_frontier_data(strategies)
    if psa == True:
        optimal = []
        for i in range(1, 21):
            original_data_copy = copy.deepcopy(data)
            optimal_at_wtp = calculate_frontier(
                data = original_data_copy, 
                print_frontier_strategies=False,
                print_graph=False,
                get_optimal=True,
                threshold=i*10000
            )
            optimal.append(optimal_at_wtp)
    else: 
        optimal = calculate_frontier(
            data = data,
            print_frontier_strategies=False,
            print_graph=False,
            get_optimal=True
        )
    return get_sa_data(strategies_key, strategies, optimal, val,psa)

def print_all_sa_data(data, path):
    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in data:
            writer.writerow(row)




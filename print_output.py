import cohort
import csv
from efficiency_frontier.efficiency_frontier import calculate_frontier


def print_counters(strategies):
    # strategy will be the row, and column will be the states
    empty = cohort.Cohort(s_strategy='printing', age=100) #placeholder for age
    empty_counters = empty.counters
    empty_counters['strategy'] = 'placeholder'
    fieldnames = empty_counters.keys()
    with open('results/counters.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key in strategies:
            # add on the strategy
            counters = strategies[key].counters
            counters['strategy'] = key
            writer.writerow(counters)
    return

def print_states(strategies):
    # strategy will be the' row, and column will be the states 
    empty = cohort.Cohort(s_strategy='printing', age = 100) # placeholder
    empty_states = empty.states
    empty_states['strategy'] = 'placeholder'
    fieldnames = empty_states.keys()
    with open('results/states.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key in strategies:
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

def print_base_case(strategies):
    print_counters(strategies)
    print_states(strategies)
    data_for_frontier = get_frontier_data(strategies)
    calculate_frontier(
        data = data_for_frontier,
        path_to_frontier_output='results/frontier_strategies.csv',
        path_to_graph='results/graph'
    )
    return

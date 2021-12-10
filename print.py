import cohort
import csv

def print_counters(strategies):
    # strategy will be the row, and column will be the states
    empty_counters = cohort.Cohort.get_counters()
    fieldnames = ["strategy"] + empty_counters.keys()
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
    # strategy will be the row, and column will be the states 
    empty_states = cohort.Cohort.get_state_matrix()
    fieldnames = ["strategy"] + empty_states.keys()
    with open('results/states.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key in strategies:
            # add on the strategy
            states = strategies[key].states
            states['strategy'] = key
            writer.writerow(states)
    return

def print_base_case(strategies):
    print_counters(strategies)
    print_states(strategies)
    return

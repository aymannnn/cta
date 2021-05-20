## input variables for the cost model
import numpy
import numpy.random as rng
import variables
import cohort as c
import run_initial_cycle
import print_output

def run_strategy(s_strat, input_variables):
    cohort = c.Cohort(s_strat)
    cohort = run_initial_cycle.run_initial_event(
        cohort, 
        input_variables)
    ## have a for month in 12 or whatever and run a function for
    ## the monthly f/u model
    return cohort

# most likely will add configuration to the setup model here
def setup_model():

    # setup model will ideally be looped, where we run setup_model:
    # setup_model(input_variables), and go from there
    # counters and states should not be changing strategy to strategy, etc.
    input_variables = variables.get_input_variables()
    # get variables: this will likely need to be moved around later
    # as we do probabilistic sensitivity analyses and one-way, etc. etc.
    strategies = {
        # add results here
        'universal': None,
        'dc': None,
        'edc': None,
        'mc': None
    }

    for key in strategies:
        print('Running strategy:', key)
        strategies[key] = run_strategy(key, input_variables)
        print(key, 
        strategies[key].counters, 
        strategies[key].states,
        strategies[key].check_state_sum())
    
    print_output.print_base_case(strategies)

    return 

if __name__ == "__main__":
    setup_model()


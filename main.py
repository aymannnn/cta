## input variables for the cost model
import numpy
import numpy.random as rng
import variables
import cohort as c

g_debug = TRUE

def move_state(states, s_from, list_s_to, list_p):
    '''
    CAREFUL: length of list to the "to" states must be same as the 
    length of the list of probabilities

    need to be careful to each state that needs to be split all into
    all possible paths at once 
    '''
    initial_from = states[s_from]
    distance_from_initial = 0
    for state, p in zip(list_s_to, list_p):
        distance = p*initial_from
        distance_from_initial += distance
        states[state] = states[state]+distance
    states[s_from] = states[s_from] - distance_from_initial
    return states

def split_initial_states(cohort, input_variables):
    # initial to true BCVI
    p_i_tbcvi = input_variables['incidence.bcvi.blunt'].val
    cohort.states = move_state(
        cohort.states, 
        'initial', 
        ['true.bcvi', 'false.bcvi'], 
        [p_i_tbcvi, 1-p_i_tbcvi]
    )
    return cohort

def get_sens_spec(strategy, variables):
    sens = None
    spec = None
    if strategy == 'universal':
        sens = variables['cta.sens'].val
        spec = variables['cta.spec'].val
    else if strategy == 'dc':
        sens = variables['dc.sens'].val
        spec = variables['dc.spec'].val
    else if strategy == 'edc':
        sens = variables['edc.sens'].val
        spec = variables['edc.spec'].val
    else if strategy == 'mc':
        sens = variables['mc.sens'].val
        spec = variables['mc.spec'].val
    else:
        return sens, spec
    return sens, spec

def count_ctas_and_move_states(cohort):
    # note that this is only defined for patients that are NOT in the 
    # universal screening strategy
    assert(cohort.strategy != 'universal')

    # add the number of ct scans
    cohort.counters['ct.scan'] += cohort.states['TP']
    cohort.counters['ct.scan'] += cohort.states['FP']

    # move states

    cohort.states = move_states(
        'TP',
        'detected.bcvi',
        1
    )
    # FP and TN get moved into the no.bcvi category, since 
    # that's their actual state that matters for this point going forward
    # note that false positive means false positive to GET A CT, and does NOT
    # mean that a CT scan is positive
    cohort.states = move_states(
        'FP',
        'no.bcvi',
        1
    )
    cohort.states = move_states(
        'TN',
        'no.bcvi',
        1
    )
    cohort.states = move_states(
        'FN',
        'missed.bcvi',
        1
    )
    return cohort

def universal_cta(cohort):
    assert(cohort.strategy == 'universal')
    cohort.states = move_states(
        'true.bcvi',
        'detected.bcvi',
        1
        # probability is 1 because every1 is getting a ct scan and thus
        # everyone is detected
    )
    cohort.states = move_states(
        'false.bcvi',
        'no.bcvi',
        1
    )
    return cohort
        

def screening_test(cohort, input_variables):

    # NOTE: this is ONLY defined for patients in a NON-universal strategy,
    # screening refers to the CRITERIA to get a CT scan

    sens, spec = get_sens_spec(cohort.strategy, input_variables)
    
    # movement into screened and unscreened states
    # true state bcvi
    start_state = 'true.bcvi'
    end_states = ['TP', 'FN']
    probs = [sens, 1-sens]
    cohort.states = move_state(
        cohort.states,
        start_state,
        end_states,
        probs
    )

    # repeat for false state bcvi
    start_state = 'false.bcvi'
    end_states = ['FP', 'TN']
    probs = [1-spec, spec]
    cohort.states = move_state(
        cohort.states,
        start_state,
        end_states,
        probs
    )

    # count the number of CTAs
    cohort = count_ctas_and_move_states(cohort)

    if g_debug:
        print('After screening test (excluded in universal):', cohort.states)

    return cohort

def run_strategy(s_strat, input_variables):
    cohort = c.Cohort(s_strat)
    # now everyone is in true state bcvi or false.bcvi
    cohort = split_initial_states(cohort, input_variables)
    
    if g_debug:
        print('After initial split:', cohort.states)

    # splitting into three main states: detected BCVI, missed, and none
    # will use sens and spec of tests, and then CTA in the next functions
    # universal is different obviously since sens and spec doesn't make as much
    # sense and will break the CTA and move function
    
    if cohort.strategy == 'universal':
        cohort = universal_cta(cohort)
    else:
        cohort = screening_test(cohort, input_variables)

    if g_debug:
        print('After CTA counting:', cohort.states)


    print(cohort.states)
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
    return 

if __name__ == "__main__":
    setup_model()


## input variables for the cost model
import numpy
import numpy.random as rng
import variables
import cohort as c
import run_initial_cycle
import print_output
import followup

def run_single_strategy(s_strat, input_variables):
    cohort = c.Cohort(
        s_strat, input_variables['starting.age'].val)
    cohort = run_initial_cycle.run_initial_event(
        cohort, 
        input_variables)
    cohort = followup.run_monthly_followup(cohort, input_variables)
    return cohort

def run_single_analysis(
    input_variables, 
    strategies_key, 
    sa_or_psa = False,
    sa_val = None,
    psa = False):

    # set up the strategies
    strategies = dict.fromkeys(strategies_key)

    for key in strategies:
        strategies[key] = run_single_strategy(key, input_variables)

    if sa_or_psa == True:
        return print_output.print_single_sa_run(
            strategies_key, 
            strategies,
            sa_val,
            psa
            )
    else:
        return print_output.print_base_case(strategies_key, strategies)

# most likely will add configuration to the setup model here
def setup_model():
    strategies_key = [
        'none',
        'universal',
        'dc',
        'edc',
        'mc'
    ]

    input_variables = variables.get_input_variables()

    if input_variables['run.base.case']:
        print('Running base case')
        run_single_analysis(
            input_variables,
            strategies_key)

    if input_variables['run.psa'] == True:
        print('Running probabilistic sensitivity analysis')
    
        results = []

        results.append(
            print_output.get_sa_header(
                strategies_key=strategies_key,
                psa=True))

        for i in range(input_variables['psa.iterations']):
            # all variables updated to current iteration
            # on initiation of input variables, the random values are all
            # generated, hopefully
            if (i%1000 == 0):
                print('Running simulation: ', i)
            input_variables['current.psa.iteration'] = i
            variables.update_psa_variables(input_variables)

            # return a list of [val, strat1 qaly, strat1 life, ... optimal]
            results.append(
                run_single_analysis(
                    input_variables, 
                    strategies_key,
                    sa_or_psa=True,
                    psa=True))

        print_output.print_all_sa_data(
            results,
            path = 'results/' + 'PSA' + '.csv'
            )



    if input_variables['run.sensitivity'] == True:
        ## adding in a setting to do the sensitivity analysis
        # reset 

        sa_variable = input_variables['sa_variable']

        print('Running sensitivity analyses on the variable:', sa_variable)
        input_variables[sa_variable].print_bounds()
        results = []
        
        results.append(
            print_output.get_sa_header(strategies_key=strategies_key))

        for val in input_variables[sa_variable].values_sa:
            input_variables[sa_variable].val = val
            # return a list of [val, strat1 qaly, strat1 life, ... optimal]
            results.append(
                run_single_analysis(
                    input_variables, 
                    strategies_key,
                    sa_or_psa=True,
                    sa_val=val))

        print_output.print_all_sa_data(
            results,
            path = 'results/' + sa_variable + '.csv'
            )



if __name__ == "__main__":
    setup_model()
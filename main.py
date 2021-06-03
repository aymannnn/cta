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
    sa = False,
    sa_val = None):

    # set up the strategies
    strategies = dict.fromkeys(strategies_key)

    for key in strategies:
        strategies[key] = run_single_strategy(key, input_variables)

    if sa == True:
        return print_output.print_single_sa_run(
            strategies_key, 
            strategies,
            sa_val
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

    ## adding in a setting to do the sensitivity analysis
    input_variables = variables.get_input_variables()

    if input_variables['run.sensitivity'] == True:
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
                    sa=True,
                    sa_val=val))

        print_output.print_all_sa_data(
            results,
            path = 'results/' + sa_variable + '.csv'
            )

    ## reset for base case analysis
    input_variables = variables.get_input_variables()
    if input_variables['run.base.case']:
        print('Running base case')
        run_single_analysis(
            input_variables,
            strategies_key, 
            sa =False)

if __name__ == "__main__":
    setup_model()
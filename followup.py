import general_functions as gf
import life_table


def update_cost_qaly(cohort, input_variables):
    # QALY
    
    cycle = 1/12

    # lt = longterm
    cost_stroke_lt = input_variables['monthly.cost.stroke.long.term'].val
    
    cohort.counters['cost.this.cycle'] += (
        cost_stroke_lt*cohort.states['fu.stroke'])

    qaly_trauma = input_variables['utility.trauma.long.term'].val
    qaly_stroke = input_variables['utility.stroke.long.term'].val

    qaly_stroke_all = cycle*qaly_stroke*qaly_trauma
    qaly_trauma_all = cycle*qaly_trauma

    cohort.counters['qaly.this.cycle'] += (
        qaly_stroke_all*cohort.states['fu.stroke'])
    cohort.counters['qaly.this.cycle'] += (
        qaly_trauma_all*cohort.states['fu.regular'])

    
    # print('QALY this cycle:    ', cohort.counters['qaly.this.cycle'])
    # print('COST this cycle      ', cohort.counters['cost.this.cycle'])
    # print('number in followup stroke         ', cohort.states['fu.stroke'])
    # print('number in regular followup         ', cohort.states['fu.regular'])
    # print('QALY stroke         ', qaly_stroke_all)
    # print('QALY trauma          ', qaly_trauma_all)

    return cohort

def update(cohort, input_variables):
    # assume that if they die, they die at the start of the month
    # print('########')

    prob_death_baseline = life_table.get_monthly_death_probability(
        cohort.counters['current.age']
    )
    prob_death_post_stroke = gf.adjust_for_relative_risk(
        input_variables['RR.mortality.stroke'].val, prob_death_baseline
    )

    starting_mortality = cohort.states['fu.dead']

    # print('starting dead:    ', starting_mortality)
    # print('starting fu/regular      ', cohort.states['fu.regular'])
    # print('starting fu/stroke          ', cohort.states['fu.stroke'])
    # print('prob dead baseline          ', prob_death_baseline)
    # print('prob dead stroke          ', prob_death_post_stroke)
    
    
    cohort = gf.move_state(
        cohort,
        'fu.regular',
        ['fu.dead', 'fu.regular'],
        [prob_death_baseline, 1-prob_death_baseline]
    )

    cohort = gf.move_state(
        cohort,
        'fu.stroke',
        ['fu.dead', 'fu.stroke'],
        [prob_death_post_stroke, 1-prob_death_post_stroke]
    )

    # a little roundabout instead of just calculating the whole mortality,
    # but the problem is that in the above functions we move states
    # we will adjust the total mortality later

    cohort.counters['mortality.this.cycle'] = (
        cohort.states['fu.dead'] - starting_mortality)

    # print('mortality this cycle     ', cohort.counters['mortality.this.cycle'])
    # print('ending dead:    ', cohort.states['fu.dead'])
    # print('ending fu/regular      ', cohort.states['fu.regular'])
    # print('ending fu/stroke          ', cohort.states['fu.stroke'])

    # finally, we just need to add in the quality of life
    cohort = update_cost_qaly(cohort, input_variables)

    return cohort

def run_monthly_followup(cohort, input_variables):
    while(
        cohort.counters['current.age'] < input_variables['stopping.age'].val):
        cohort = update(cohort, input_variables)
        cohort = gf.reset_counters(cohort)
    return cohort





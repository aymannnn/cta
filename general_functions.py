def move_state(cohort, s_from, list_s_to, list_p):
    '''
    CAREFUL: length of list to the "to" states must be same as the 
    length of the list of probabilities

    need to be careful to each state that needs to be split all into
    all possible paths at once 

    "list" variables MUST be lists (not just integers)
    '''
    
    # sum of the probabilities should be 1 or else we will have issues
    assert sum(list_p)==1, list_p

    starting_x = cohort.states[s_from]
    # the probabilities should all add up to come, and we have ending state
    # amounts. therefore, just wipe out the starting point
    cohort.states[s_from] = 0.0
    ending_state_additions = [starting_x * p for p in list_p]
    
    for index, state in enumerate(list_s_to):
        cohort.states[state] += ending_state_additions[index]

    assert cohort.check_state_sum(), cohort.states

    return cohort

def probability_to_odds(prob):
    odds = prob/(1-prob)
    return odds

def odds_to_probability(odds):
    prob = odds/(1+odds)
    return prob

def annual_prob_to_monthly(prob):
    odds = probability_to_odds(prob)
    monthly_odds = (1/12.0)*odds
    adjusted_prob = odds_to_probability(monthly_odds)
    return adjusted_prob

def adjust_for_relative_risk(rr, prob):
        # prob to odds
    odds =  probability_to_odds(prob)
    scaled = odds*rr
    # odds to prob
    adjusted_prob = odds_to_probability(scaled)
    return adjusted_prob

def reset_counters(cohort):

    index = cohort.counters['index']

    previous_mortality = 0
    previous_qaly = 0
    previous_cost = 0
    
    if index != 0:
        previous_mortality = cohort.counters['monthly.mortality'][index-1]
        previous_qaly = cohort.counters['monthly.qaly.total'][index-1]
        previous_cost = cohort.counters['monthly.cost.total'][index-1]
    
    print('previous mortality, previous qaly, previous cost:', 
    previous_mortality, previous_qaly, previous_cost)
    print('current mortality, current qaly, current cost',
    cohort.counters['mortality.this.cycle'],
    cohort.counters['cost.this.cycle'],
    cohort.counters['qaly.this.cycle'])

    cohort.counters['monthly.mortality'].append(
        cohort.counters['mortality.this.cycle'] + previous_mortality
    )
    cohort.counters['monthly.cost.total'].append(
        cohort.counters['cost.this.cycle'] + previous_cost
    )
    cohort.counters['monthly.qaly.total'].append(
        cohort.counters['qaly.this.cycle'] + previous_qaly
    )
    
    cohort.counters['index'] += 1
    cohort.counters['current.age'] += 1

    cohort.counters['qaly.this.cycle'] = 0
    cohort.counters['mortality.this.cycle'] = 0
    cohort.counters['cost.this.cycle'] = 0
    
    return cohort
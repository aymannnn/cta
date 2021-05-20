def move_state(states, s_from, list_s_to, list_p):
    '''
    CAREFUL: length of list to the "to" states must be same as the 
    length of the list of probabilities

    need to be careful to each state that needs to be split all into
    all possible paths at once 

    "list" variables MUST be lists (not just integers)
    '''
    initial_from = states[s_from]
    distance_from_initial = 0
    for state, p in zip(list_s_to, list_p):
        distance = p*initial_from
        distance_from_initial += distance
        states[state] = states[state]+distance
    states[s_from] = states[s_from] - distance_from_initial
    return states
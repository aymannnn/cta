import variables
import cohort as c
import general_functions as gf

def split_initial_states(cohort, input_variables):
    # initial to true BCVI
    p_i_tbcvi = input_variables['incidence.bcvi.blunt'].val
    cohort = gf.move_state(
        cohort, 
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
    elif strategy == 'dc':
        sens = variables['dc.sens'].val
        spec = variables['dc.spec'].val
    elif strategy == 'edc':
        sens = variables['edc.sens'].val
        spec = variables['edc.spec'].val
    elif strategy == 'mc':
        sens = variables['mc.sens'].val
        spec = variables['mc.spec'].val
    else:
        return sens, spec
    return sens, spec

def count_ctas_and_move_states(cohort, input_variables):
    # note that this is only defined for patients that are NOT in the 
    # universal screening strategy
    assert(cohort.strategy != 'universal')

    # add the number of ct scans
    cohort.counters['ct.scan'] += cohort.states['TP']
    cohort.counters['ct.scan'] += cohort.states['FP']
    
    cohort.counters['cost.this.cycle'] += (
        cohort.counters['ct.scan']*
        input_variables['cost.cta'].val)

    # move states
    cohort = gf.move_state(
        cohort,
        'TP',
        ['detected.bcvi'],
        [1]
    )
    # FP and TN get moved into the no.bcvi category, since 
    # that's their actual state that matters for this point going forward
    # note that false positive means false positive to GET A CT, and does NOT
    # mean that a CT scan is positive
    cohort = gf.move_state(
        cohort,
        'FP',
        ['no.bcvi'],
        [1]
    )
    cohort = gf.move_state(
        cohort,
        'TN',
        ['no.bcvi'],
        [1]
    )
    cohort = gf.move_state(
        cohort,
        'FN',
        ['missed.bcvi'],
        [1]
    )
    return cohort

def universal_cta(cohort, input_variables):
    assert(cohort.strategy == 'universal')
    cohort = gf.move_state(
        cohort,
        'true.bcvi',
        ['detected.bcvi'],
        [1]
        # probability is 1 because every1 is getting a ct scan and thus
        # everyone is detected
    )
    cohort = gf.move_state(
        cohort,
        'false.bcvi',
        ['no.bcvi'],
        [1]
    )
    # count the CTAs
    cohort.counters['ct.scan'] += cohort.states['detected.bcvi']
    cohort.counters['ct.scan'] += cohort.states['no.bcvi']
    cohort.counters['cost.this.cycle'] += (
        cohort.counters['ct.scan']*input_variables['cost.cta'].val)

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
    cohort = gf.move_state(
        cohort,
        start_state,
        end_states,
        probs
    )

    # repeat for false state bcvi
    start_state = 'false.bcvi'
    end_states = ['FP', 'TN']
    probs = [1-spec, spec]
    cohort = gf.move_state(
        cohort,
        start_state,
        end_states,
        probs
    )

    # count the number of CTAs
    cohort = count_ctas_and_move_states(cohort, input_variables)

    return cohort

def no_screen(cohort, input_variables):
    assert(cohort.strategy == 'none')
    cohort = gf.move_state(
        cohort,
        'true.bcvi',
        ['missed.bcvi'],
        [1]
        # probability is 1 because nobody is getting a CT scan and therefore
        # nobody is detected
    )
    cohort = gf.move_state(
        cohort,
        'false.bcvi',
        ['no.bcvi'],
        [1]
    )
    # there is no need to count the CTAs when the net cost is 0
    return cohort

def run_screen_and_cta(cohort, input_variables):
    # will use sens and spec of tests, and then CTA in the next functions
    # universal is different obviously since sens and spec doesn't make as much
    # sense and will break the CTA and move function
    if cohort.strategy == 'universal':
        cohort = universal_cta(cohort, input_variables)
    elif cohort.strategy == 'none':
        cohort = no_screen(cohort, input_variables)
    else:
        cohort = screening_test(cohort, input_variables)
 
    # add in the cost of aspirin management now that we've 
    cohort.counters['cost.this.cycle'] += (
        input_variables['cost.aspirin'].val * cohort.states['detected.bcvi'])

    return cohort

def stroke(cohort, input_variables):
    
    # starting with a detected BCVI
    start_state = 'detected.bcvi'
    end_states = ['stroke.bcvi.caught', 'regular.trauma.fu.bcvi.caught']
    
    # 5/30/22: converted to odds ratio instead, way easier in manuscript
    # p_stroke_anticoagulated = input_variables['stroke.bcvi.therapy'].val
    
    rr_stroke_anticoagulated = gf.odds_ratio_to_relative_risk(
        input_variables['OR.stroke.bcvi.therapy'].val,
        input_variables['stroke.bcvi.no.therapy'].val # underlying prevalence
    )

    p_stroke_anticoagulated = gf.adjust_for_relative_risk(
        rr_stroke_anticoagulated, input_variables['stroke.bcvi.no.therapy'].val
    )

    probs = [p_stroke_anticoagulated, 1-p_stroke_anticoagulated]
    cohort = gf.move_state(
        cohort,
        start_state,
        end_states,
        probs
    )

    cohort.counters['cost.this.cycle'] += (
        cohort.states['stroke.bcvi.caught'] * input_variables['cost.stroke'].val)

    # starting with missed bcvi
    start_state = 'missed.bcvi'
    end_states = ['stroke.bcvi.missed', 'regular.trauma.fu.bcvi.missed']
    p_stroke = input_variables['stroke.bcvi.no.therapy'].val
    probs = [p_stroke, 1-p_stroke]
    cohort = gf.move_state(
        cohort,
        start_state,
        end_states,
        probs
    )

    cohort.counters['cost.this.cycle'] += (
        cohort.states['stroke.bcvi.missed'] * input_variables['cost.stroke'].val)

    # starting with baseline risk of stroke, should be close to 1% but
    # black in a email said 1, and youssif found 11.5%
    # need to go back and address this
    start_state = 'no.bcvi'
    end_states = ['stroke.no.bcvi', 'regular.trauma.fu.no.bcvi']
    p_stroke = input_variables['stroke.no.bcvi'].val
    probs = [p_stroke, 1-p_stroke]
    cohort = gf.move_state(
        cohort,
        start_state,
        end_states,
        probs
    )

    cohort.counters['cost.this.cycle'] += (
        cohort.states['stroke.no.bcvi'] * input_variables['cost.stroke'].val)

    return cohort

def initial_mortality(cohort, input_variables):

    # first the mortality among the detected BCVI patients
    # for now we're overestimating mortality slightly ...

    ## BCVI patients WITH anticoagulation/antiplatelet/tx

    p = input_variables['mortality.bcvi.therapy'].val
    p_stroke = gf.adjust_for_relative_risk(
        input_variables['RR.mortality.stroke'].val,
        p
    )

    start_state = 'regular.trauma.fu.bcvi.caught'
    end_states = ['dead.bcvi.caught', 'regular.trauma.fu.bcvi.caught']
    probs = [p, 1-p]
    cohort = gf.move_state(
        cohort,
        start_state,
        end_states,
        probs
    )

    start_state = 'stroke.bcvi.caught'
    end_states = ['dead.bcvi.caught', 'stroke.bcvi.caught']
    probs = [p_stroke, 1-p_stroke]
    cohort = gf.move_state(
        cohort,
        start_state,
        end_states,
        probs
    )

    ## BCVI patients WITHOUT anticoagulation

    p = input_variables['mortality.bcvi.no.therapy'].val
    p_stroke = gf.adjust_for_relative_risk(
        input_variables['RR.mortality.stroke'].val,
        p
    )

    start_state = 'regular.trauma.fu.bcvi.missed'
    end_states = ['dead.bcvi.missed', 'regular.trauma.fu.bcvi.missed']
    probs = [p, 1-p]
    cohort = gf.move_state(
        cohort,
        start_state,
        end_states,
        probs
    )

    start_state = 'stroke.bcvi.missed'
    end_states = ['dead.bcvi.missed', 'stroke.bcvi.missed']
    probs = [p_stroke, 1-p_stroke]
    cohort = gf.move_state(
        cohort,
        start_state,
        end_states,
        probs
    )

    ## regular patients, no BCVI

    p = input_variables['mortality.blunt.overall'].val
    p_stroke = gf.adjust_for_relative_risk(
        input_variables['RR.mortality.stroke'].val,
        p
    )

    start_state = 'regular.trauma.fu.no.bcvi'
    end_states = ['dead.no.bcvi', 'regular.trauma.fu.no.bcvi']
    probs = [p, 1-p]
    cohort = gf.move_state(
        cohort,
        start_state,
        end_states,
        probs
    )

    start_state = 'stroke.no.bcvi'
    end_states = ['dead.no.bcvi', 'stroke.no.bcvi']
    probs = [p_stroke, 1-p_stroke]
    cohort = gf.move_state(
        cohort,
        start_state,
        end_states,
        probs
    )

    return cohort

def add_quality_of_life(cohort, input_variables):
    ## really only need to add in two different quality of lifes:
    ## 1 is regular trauma 
    ## and 2 is stroke
    ## at this point, patients that had a stroke AND died during the acute
    ## event are assumed to have a life expectancy of 0, and thus no QALY gain
    
    counters = cohort.counters
    states = cohort.states
    cycle = 1/12
    qaly_trauma = input_variables['utility.trauma.acute'].val
    qaly_stroke = input_variables['utility.stroke.acute'].val

    qaly_stroke_all = cycle*qaly_stroke*qaly_trauma
    qaly_trauma_all = cycle*qaly_trauma

    counters['qaly.this.cycle'] += qaly_stroke_all*states['stroke.bcvi.caught']
    counters['qaly.this.cycle'] += qaly_stroke_all*states['stroke.bcvi.missed']
    counters['qaly.this.cycle'] += qaly_stroke_all*states['stroke.no.bcvi']
    
    counters['qaly.this.cycle'] += (
        qaly_trauma_all*states['regular.trauma.fu.bcvi.caught'])
    counters['qaly.this.cycle'] += (
        qaly_trauma_all*states['regular.trauma.fu.bcvi.missed'])
    counters['qaly.this.cycle'] += (
        qaly_trauma_all*states['regular.trauma.fu.no.bcvi'])

    cohort.counters = counters

    return cohort

def consolidate_states(cohort):

    stroke_states = [
        'stroke.bcvi.caught', 'stroke.bcvi.missed', 'stroke.no.bcvi']

    for state in stroke_states:
        cohort = gf.move_state(
            cohort,
            state,
            ['fu.stroke'],
            [1.0]
        )

    cohort.counters['initial.month.stroke'] += cohort.states['fu.stroke']


    regular_fu_states = [
        'regular.trauma.fu.bcvi.caught', 
        'regular.trauma.fu.bcvi.missed', 
        'regular.trauma.fu.no.bcvi']

    for state in regular_fu_states:
        cohort = gf.move_state(
            cohort,
            state,
            ['fu.regular'],
            [1.0]
        )

    dead_states = [
        'dead.bcvi.caught', 'dead.bcvi.missed', 'dead.no.bcvi'
    ]

    for state in dead_states:
        cohort = gf.move_state(
            cohort,
            state,
            ['fu.dead'],
            [1.0]
        )

    cohort.counters['initial.month.mortality'] += cohort.states['fu.dead']

    return cohort

def run_initial_event(cohort, input_variables):

    # everyone has the cost of trauma
    cohort.counters['cost.this.cycle'] = 1*input_variables['cost.blunt.base'].val

    # split into true state bcvi or false.bcvi
    cohort = split_initial_states(cohort, input_variables)

    # splitting into three main states: detected BCVI, missed, and none
    cohort = run_screen_and_cta(cohort, input_variables)

    # check stroke, THEN the mortality risk
    cohort = stroke(cohort, input_variables)
    cohort = initial_mortality(cohort, input_variables)
    
    cohort = add_quality_of_life(cohort, input_variables)

    cohort.initial_event_ran = True

    cohort.counters["current.age"] += 1

    cohort.counters['mortality.this.cycle'] = (
        cohort.states['dead.bcvi.caught']+
        cohort.states['dead.bcvi.missed']+
        cohort.states['dead.no.bcvi']
    )

    # cohort.counters['monthly.mortality'].append(
    #     cohort.counters['mortality.this.cycle']
    # )

    # cohort.counters['monthly.cost.total'].append(
    #     cohort.counters['cost.this.cycle']
    # )

    # cohort.counters['monthly.qaly.total'].append(
    #     cohort.counters['qaly.this.cycle']
    # )

    cohort = consolidate_states(cohort)

    gf.reset_counters(cohort)

    return cohort
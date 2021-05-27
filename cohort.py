class Cohort():
    '''
    initial setup, define patient base case scenarios
    '''
    def get_counters(self, age):
        # have a strategy string for printing
        counters = {
            'ct.scan': 0,
            'index': 0,

            'cost.this.cycle': 0,
            'mortality.this.cycle': 0,
            'qaly.this.cycle': 0,

            'QALY.post.stroke': 0,
            'QALY.post.trauma': 0,

            'current.age': age,

            'monthly.mortality': [],
            'monthly.cost.total': [],
            'monthly.qaly.total': [],

            'final.cost.per.mult':0,
            'final.qaly.per.mult':0
        }

        return counters

    def get_state_matrix(self):
        states = {
            'initial': 1.0,
            'true.bcvi': 0.0,
            'false.bcvi': 0.0,

            # subset of true bcvi
            # actually easier to label with TP, FP, etc. 
            'TP': 0.0,
            'FN': 0.0,

            # subset of false bcvi
            'FP': 0.0,
            'TN': 0.0,

            # after screening test
            'detected.bcvi': 0.0,
            'missed.bcvi': 0.0,
            'no.bcvi': 0.0,

            ## ONLY "need" to print these last states
            ## in the output tables, but can go ahead
            ## and print all

            # stroke states/mortality
            # need to stratify by state of BCVI
            'stroke.bcvi.caught': 0.0,
            'stroke.bcvi.missed': 0.0,
            'stroke.no.bcvi': 0.0,

            ## mortality and follow-up
            'regular.trauma.fu.bcvi.caught': 0.0,
            'regular.trauma.fu.bcvi.missed': 0.0,
            'regular.trauma.fu.no.bcvi': 0.0,
            
            ## mortality
            'dead.bcvi.caught': 0.0,
            'dead.bcvi.missed': 0.0,
            'dead.no.bcvi': 0.0,

            ## POST INITIAL CYCLE

            'fu.stroke': 0.0,
            'fu.regular': 0.0,
            'fu.dead': 0.0,

        }
        return states

    def close_to_one(self, val):
        ## acceptable error of 0.005, which is a 0.5% margin around 1
        ## may come back and reduce this
        return ((val > 0.995) & (val < 1.005))

    def check_state_sum(self):
        val = 0
        for key in self.states:
            state_amt = self.states[key]
            if (state_amt < 0) | (state_amt>1):
                print(key, state_amt)
                return False
            else:
                val += state_amt
        if self.close_to_one(val):
            return True
        else:
            print('failed check state sum', self.states, val)
            return False

    def __init__(self, s_strategy, age):
        self.strategy = s_strategy
        self.counters = self.get_counters(age)
        self.states = self.get_state_matrix()
        self.initial_event_ran = False
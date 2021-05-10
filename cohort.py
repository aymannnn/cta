class Cohort():
    '''
    initial setup, define patient base case scenarios
    '''
    def get_counters(self):
        counters = {
            'ct.scan': 0
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
            'no.bcvi': 0.0
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
        return self.close_to_one(val)

    def __init__(self, s_strategy):
        self.strategy = s_strategy
        self.counters = self.get_counters()
        self.states = self.get_state_matrix()

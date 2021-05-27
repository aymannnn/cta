import general_functions

class Variable():
    '''
    initial setup, always define a function to generate lower,
    upper, and random bounds
    '''
    ## for now just because it's a randomly chosen value for some of the
    ## parameters, we're going to just assume a uniform distribution and 
    ## kind of pick randomly between values
    def get_base(self):
        return self.__base

    def get_lower_bound(self):
        return self.lower

    def get_upper_bound(self):
        return self.upper

    def setup_sa(self, iterations):
        assert self.__lower < self.__upper, [self.__lower, self.__upper]
        assert self.__base > self.__lower and self.__base < self.__upper
        
        interval = (self.__upper - self.__lower) / iterations
        val = self.__lower

        for i in range(iterations):
            self.values_sa.append(val)
            val += interval
        #print(self.__lower, self.__upper, self.values_sa)
        return

    def print_bounds(self):
        print(
            'Bounds are:', 
            self.__lower, 
            'to', 
            self.__upper, 
            ', with a base case value of',
            self.__base)

    def __init__(
        self, 
        base,
        lower = None,
        upper = None,
        x = None, 
        n = None, 
        distribution = None):

        self.__lower = lower
        self.__upper = upper
        self.values_sa = []
        self.distribution = None
        self.__base = base
        ## update here if val is not base, i.e. base-case
        ## scenario
        self.val = self.__base

def get_input_variables():

    variables = {
        # some model setup things
        'run.base.case': True,
        'run.sensitivity': True,
        'sa_variable': 'incidence.bcvi.blunt',
        'sa.iterations': 200,

        ## starting cohort characteristics
        'multiplier': 1000, # to get results by per 1000

        # NOTE that AGE is in MONTHS
        'starting.age': Variable(600),
        'stopping.age': Variable(612),
        'iss': Variable(17),
        'blunt.trauma.usa': Variable(2405000),
        'incidence.bcvi.blunt': Variable(
            0.076,
            lower = 0.005,
            upper = 0.10
            ),

        ## screening test characteristics
        ## positive test given true state is sensitivity
        ## negative test given true state is 1-sensitivity
        ## negative test given negative state is specificity
        ## positive test given negative state is 1-specificity
        ## dc = denver, edc = expanded denver, mc = memphis
        
        'dc.sens': Variable(0.575),
        'dc.spec': Variable(0.791),
        'edc.sens': Variable(0.747),
        'edc.spec': Variable(0.615),
        'mc.sens': Variable(0.473),
        'mc.spec': Variable(0.839),
        'cta.sens': Variable(1), # assume gold standard
        'cta.spec': Variable(0), # specificity is 0 because
        # 

        ## stroke with and without thrombotic therapy
        'stroke.bcvi.no.therapy': Variable(0.3360),
        'stroke.bcvi.therapy': Variable(0.0980),
        ## TODO: come back and fix this value with the one that
        ## youssef got
        'stroke.no.bcvi': Variable(0.017), ## black in an email

        ## mortality with and without thrombotic therapy
        ## relative risk of mortality with stroke
        'RR.mortality.stroke': Variable(1.75), # ideally have one for long-term
        'mortality.bcvi.no.therapy': Variable(0.4030),
        'mortality.bcvi.therapy': Variable(0.1660),
        'mortality.blunt.overall': Variable(0.1610),
        ## hemorrhage? complications?
        
        ## costs?
        'cost.cta': Variable(708),
        # TODO: SHOULD BLUNT BASE TRAUMA COST BE INCLUDED? DOESN'T CHANGE DELTA
        # 'cost.blunt.base': Variable(23397), 
        'cost.blunt.base': Variable(0), 
        'cost.stroke': Variable(19248),
        'cost.aspirin': Variable(4),
    

        'cost.mortality.initial': Variable(0), ## TODO: SEE IF UPDATE?

        # long-term
        'monthly.cost.stroke.long.term': Variable((35089.49/12)),

        # utilites PLACEHOLDER

        'utility.stroke.acute': Variable(0.073),
        'utility.stroke.long.term': Variable(0.64),
        'utility.trauma.acute': Variable(0.85), # PLACEHOLDER?
        'utility.trauma.long.term': Variable(0.85)
    }

        # set up sensitivity analysis here
    
    sa_lower =  0.005,
    sa_upper = 0.01,

    if variables['run.sensitivity'] == True:
        variables[variables['sa_variable']].setup_sa(
            variables['sa.iterations']
        )
    return variables




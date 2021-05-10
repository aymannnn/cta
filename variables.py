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

    def __init__(self, base, x = None, n = None):
        self.lower = None
        self.upper = None
        self.distribution = None
        self.__base = base
        ## update here if val is not base, i.e. base-case
        ## scenario
        self.val = self.__base

def get_input_variables():
    variables = {
        ## starting cohort characteristics
        'age': Variable(65),
        'iss': Variable(17),
        'blunt.trauma.usa': Variable(2405000),
        'incidence.bcvi.blunt': Variable(0.076),

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
        'stroke.no.bcvi': Variable(0.017), ## black in an email

        ## mortality with and without thrombotic therapy
        'mortality.bcvi.no.therapy': Variable(0.4030),
        'mortality.bcvi.therapy': Variable(0.1660)
        ## hemorrhage? complications?
        
        ## costs?

    }
    return variables
    


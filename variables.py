from dis import dis
import general_functions
import numpy as np
import inspect
import csv

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
        '''
        SA will use essentially a uniform distribution, but with
        a predefined set of values in that interval instead of randomness 
        '''
        assert self.lower < self.upper, [self.lower, self.upper]
        assert self.__base > self.lower and self.__base < self.upper
        
        interval = (self.upper - self.lower) / iterations
        val = self.lower

        for i in range(iterations):
            self.values_sa.append(val)
            val += interval
        #print(self.__lower, self.__upper, self.values_sa)
        return

    def print_bounds(self):
        print(
            'Bounds are:', 
            self.lower, 
            'to', 
            self.upper, 
            ', with a base case value of',
            self.__base)

    def generate_x_n_beta(self, mean, variance):
        a = ((1-mean)/(variance*variance) - (1/mean))*mean*mean
        b = a*(1/mean - 1)
        # even though beta is defined with a and b, 
        # will be setting a+b as "n" since the others work like that
        self.x_beta = a
        self.n_beta = b+a

    def get_random_uniform(self):
        return(np.random.uniform(self.lower, self.upper))
    
    def get_random_beta(self):
        return(np.random.beta(self.x_beta, self.n_beta-self.x_beta))
    
    def get_random_gamma(self):
        x = np.random.gamma(self.shape_gamma, self.scale_gamma)
        if (x > self.strict_gamma_upper) or (
            x < self.strict_gamma_lower
        ):
            self.gamma_rerolls+=1
            self.get_random_gamma(self)
        ## debug
        if (self.gamma_rerolls > 0):
            print("GAMMA REROLLS", self.gamma_rerolls)
        return x

    def get_random_normal(self):
        return(np.random.normal(self.mean_normal, self.std_normal))

    def get_random_lognormal(self):
        ## using correction from https://pubmed.ncbi.nlm.nih.gov/19695002/
        med = self.lognormal_median
        se = self.lognormal_se
        corrected_med = np.exp(
            np.log(med) - 0.5*se*se)
        return np.random.lognormal(np.log(corrected_med), se)

    def repeat_base_case(self):
        return self.val

    def generate_random_variables(self, iterations):
        for i in range(iterations):
            self.values_psa.append(self.random_value_function())
        return

    def update_psa_value(self, iteration):
        self.val = self.values_psa[iteration]

    def __init__(
        ###
        self, 
        base,
        distribution = None,
        backcalculate_beta=False,
        mean_beta = None,
        variance_beta = None,
        lower = None,
        upper = None,
        x_beta = None, 
        n_beta = None,
        shape_gamma = None,
        scale_gamma = None,
        mean_normal = None,
        std_normal = None,
        lognormal_median = None,
        lognormal_se = None,
        strict_gamma_upper = np.inf,
        strict_gamma_lower = 0,
        gamma_rerolls=0,
        name = None
):
        self.distribution = distribution
        self.lower = lower
        self.upper = upper
        self.x_beta = x_beta
        self.n_beta = n_beta
        self.shape_gamma = shape_gamma
        self.scale_gamma = scale_gamma
        self.mean_normal = mean_normal
        self.std_normal = std_normal
        self.lognormal_median = lognormal_median
        self.lognormal_se = lognormal_se
        self.strict_gamma_upper = strict_gamma_upper
        self.strict_gamma_lower = strict_gamma_lower
        self.gamma_rerolls = gamma_rerolls
        self.values_sa = []
        self.values_psa = []
        self.__base = base
        self.val = self.__base

        if backcalculate_beta:
            self.generate_x_n_beta(mean_beta, variance_beta)

        self.random_value_function = None
        if self.distribution == 'uniform':
            self.random_value_function = self.get_random_uniform
        elif self.distribution == 'beta':
            self.random_value_function = self.get_random_beta
        elif self.distribution == 'gamma':
            self.random_value_function = self.get_random_gamma
        elif self.distribution == 'normal':
            self.random_value_function = self.get_random_normal
        elif self.distribution == 'lognormal':
            self.random_value_function = self.get_random_lognormal
        elif self.distribution == 'none':
            self.random_value_function = self.repeat_base_case
        else:
            print("Error, no distribution defined for variable.")

def get_input_variables():

    variables = {
        # some model setup things
        'run.base.case': True,
        'run.sensitivity': False,
        'run.psa': True,
        'sa_variable': 'incidence.bcvi.blunt',
        'sa.iterations': 200,
        'psa.iterations': 10000,
        'current.psa.iteration': None,
        'months_to_run': 60, # stopping age defined as starting + months

        ## starting cohort characteristics
        'multiplier': 1000, # to get results by per 1000

        ## PSA variables

        # NOTE that AGE is in MONTHS
        'starting.age': Variable(
            600, 
            distribution='uniform',
            lower = 480,
            upper = 720),

        'iss': Variable(
            17,
            distribution = 'gamma',
            shape_gamma = 17,
            scale_gamma = 1,
            strict_gamma_upper=75, # ISS is capped at 75, gamma distribution
            strict_gamma_lower=0),

        'blunt.trauma.usa': Variable(
            2405000,
            distribution='none'),

        'incidence.bcvi.blunt': Variable(
            0.076,
            distribution='uniform',
            lower = 0.005,
            upper = 0.10
            ),

        ## screening test characteristics
        ## positive test given true state is sensitivity
        ## negative test given true state is 1-sensitivity
        ## negative test given negative state is specificity
        ## positive test given negative state is 1-specificity
        ## dc = denver, edc = expanded denver, mc = memphis
        
        'dc.sens': Variable(
            0.575,
            distribution='beta',
            x_beta=271,
            n_beta=471
            ),
        'dc.spec': Variable(
            0.791,
            distribution = 'beta',
            x_beta=4600,
            n_beta=5816
            ),
        'edc.sens': Variable(
            0.747,
            distribution='beta',
            x_beta=352,
            n_beta=471
            ),
        'edc.spec': Variable(
            0.615,
            distribution='beta',
            x_beta=3577,
            n_beta=5816
            ),
        'mc.sens': Variable(
            0.473,
            distribution='beta',
            x_beta=233,
            n_beta=471
            ),
        'mc.spec': Variable(
            0.839,
            distribution='beta',
            x_beta=4880,
            n_beta=5816
            ),
        'cta.sens': Variable(
            1,
            distribution='none'
            ), # assume gold standard
        'cta.spec': Variable(
            0,
            distribution='none'), # specificity is 0 because
        # 

        ## stroke with and without thrombotic therapy
        'stroke.bcvi.no.therapy': Variable(
            0.3360,
            distribution='beta',
            n_beta=235,
            x_beta=79
            ),

        'stroke.bcvi.therapy': Variable(
            0.0980,
            lower=0.017,
            upper=0.3360,
            distribution='beta',
            x_beta=70,
            n_beta=713
            ),

        'stroke.no.bcvi': Variable(
            0.011,
            distribution='beta',
            x_beta=833,
            n_beta=75694
            ), ## using Weber 2017

        ## mortality with and without thrombotic therapy
        ## relative risk of mortality with stroke
        ## lognormal distribution calculated as the log of the RR 
        ## and the log of the standard error
        ## log(RR-2.5% bound) or log(97.5% bound - RR) divided by 1.96
        
        'RR.mortality.stroke': Variable(
            1.75,
            distribution='lognormal',
            lognormal_median=1.75,
            lognormal_se=np.log(3.48/1.75)/1.96,
            ), 

        'mortality.bcvi.no.therapy': Variable(
            0.4030,
            distribution = 'beta',
            x_beta=31,
            n_beta=77),

        'mortality.bcvi.therapy': Variable(
            0.1660,
            lower =0.1610,
            upper=0.4030,
            distribution='beta',
            x_beta=42,
            n_beta=253),

        'mortality.blunt.overall': Variable(
            0.1610,
            distribution='beta',
            x_beta=1639,
            n_beta=10183),

        ## hemorrhage? complications? TODO
        
        ## costs?
        'cost.cta': Variable(
            708,
            distribution='normal',
            mean_normal=708,
            std_normal=708*0.2
            ),
            
        # TODO: SHOULD BLUNT BASE TRAUMA COST BE INCLUDED? DOESN'T CHANGE DELTA
        # 'cost.blunt.base': Variable(23397), 
        'cost.blunt.base': Variable(
            0,
            distribution='none'), 

        'cost.stroke': Variable(
            19248,
            distribution='normal',
            mean_normal = 19248,
            std_normal = 19248*0.2),
        
        # no real point putting a distribution on aspirin cost
        'cost.aspirin': Variable(
            4, 
            distribution = 'none'),
    
        # also no point on this
        'cost.mortality.initial': Variable(
            0,
            distribution='none'), ## TODO: SEE IF UPDATE?

        # long-term
        'monthly.cost.stroke.long.term': Variable(
            (35089.49/12),
            distribution='normal',
            mean_normal=(35089.49/12),
            std_normal=(35089.49/12)*0.2),

        # utilites PLACEHOLDER
        
        ## post 2001 for both below
        ## assuming major stroke QOL is OK for ACUTE and long term is like minor
        ## this is conservative since long-term won't include major stroke
        ## longterm

        'utility.stroke.acute': Variable(
            0.50,
            distribution='beta',
            backcalculate_beta=True,
            name='utility.stroke.acute',
            mean_beta=0.30,
            variance_beta=0.30*0.1
            ),

        'utility.stroke.long.term': Variable(
            0.64,
            distribution='beta',
            backcalculate_beta=True,
            name = 'utility.stroke.long.term',
            mean_beta=0.64,
            variance_beta=(0.71-0.52)/(1.96*2)),
            
        ## TODO: This acute value is trash, will have to update
        'utility.trauma.acute': Variable(
            0.50,
            distribution='beta',
            backcalculate_beta=True,
            name='utility.trauma.acute',
            mean_beta=0.50,
            variance_beta=0.50*0.1), # PLACEHOLDER?

        'utility.trauma.long.term': Variable(
            #https://pubmed.ncbi.nlm.nih.gov/32315373/
            0.77,
            distribution='beta',
            backcalculate_beta=True,
            name='utility.trauma.long.term',
            mean_beta=0.77,
            variance_beta=0.26),
        
        'psa.data': []
    }

        # set up sensitivity analysis here
    
    sa_lower =  0.005,
    sa_upper = 0.01,

    if variables['run.sensitivity'] == True:
        variables[variables['sa_variable']].setup_sa(
            variables['sa.iterations']
        )

    if variables['run.psa'] == True:
        for item in variables:
            if isinstance(variables[item], Variable):
                variables[item].generate_random_variables(
                    variables['psa.iterations']
                )
                a = variables[item].values_psa.copy()
                a.insert(0, item)
                variables['psa.data'].append(a)

    with open('results/psa.values.csv', 'w', newline = '') as csvfile:
        writer = csv.writer(csvfile)
        for row in variables['psa.data']:
            writer.writerow(row)

    return variables


def update_psa_variables(input_variables):
    iteration = input_variables['current.psa.iteration']
    for item in input_variables:
        if isinstance(input_variables[item], Variable):
            input_variables[item].update_psa_value(iteration)



import input_data as data
import ParamUncertainty.model_classes_uncertainty as model
import ParamUncertainty.param_classes_uncertainty as param
import ParamUncertainty.support_uncertainty as support

N_COHORTS = 100  # number of cohorts
POP_SIZE = 500  # population size of each cohort

# create a multi-cohort to simulate under semaglutide therapy
multiCohortSema = model.MultiCohort(
    ids=range(N_COHORTS),
    pop_size=POP_SIZE,
    therapy=param.Therapies.SEMA
)

multiCohortSema.simulate(n_time_steps=data.SIM_TIME_STEPS)

# create a multi-cohort to simulate under tirzepatide therapy
multiCohortTirz = model.MultiCohort(
    ids=range(N_COHORTS),
    pop_size=POP_SIZE,
    therapy=param.Therapies.TIRZ
)

multiCohortTirz.simulate(n_time_steps=data.SIM_TIME_STEPS)

# print the estimates for the mean survival time and mean time to AIDS
support.print_outcomes(multi_cohort_outcomes=multiCohortSema.multiCohortOutcomes,
                       therapy_name=param.Therapies.SEMA)
support.print_outcomes(multi_cohort_outcomes=multiCohortTirz.multiCohortOutcomes,
                       therapy_name=param.Therapies.TIRZ)

# draw survival curves and histograms
# support.plot_survival_curves_and_histograms(multi_cohort_outcomes_sema=multiCohortSema.multiCohortOutcomes,
#                                             multi_cohort_outcomes_tirz=multiCohortTirz.multiCohortOutcomes)

# print comparative outcomes
support.print_comparative_outcomes(multi_cohort_outcomes_sema=multiCohortSema.multiCohortOutcomes,
                                   multi_cohort_outcomes_tirz=multiCohortTirz.multiCohortOutcomes)

# report the CEA results
support.report_CEA_CBA(multi_cohort_outcomes_sema=multiCohortSema.multiCohortOutcomes,
                       multi_cohort_outcomes_tirz=multiCohortTirz.multiCohortOutcomes)

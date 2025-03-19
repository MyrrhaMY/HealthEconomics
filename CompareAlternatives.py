# final project
import input_data as data
import model_classes as model
import param_classes as param
import support as support

# simulating mono therapy
# create a cohort
cohort_sema = model.Cohort(id=0,
                           pop_size=data.POP_SIZE,
                           parameters=param.Parameters(therapy=param.Therapies.SEMA))
# simulate the cohort
cohort_sema.simulate(n_time_steps=data.SIM_TIME_STEPS)

# simulating combination therapy
# create a cohort
cohort_tirz = model.Cohort(id=1,
                           pop_size=data.POP_SIZE,
                           parameters=param.Parameters(therapy=param.Therapies.TIRZ))
# simulate the cohort
cohort_tirz.simulate(n_time_steps=data.SIM_TIME_STEPS)

# print the estimates for the mean survival time and mean time to AIDS
support.print_outcomes(sim_outcomes=cohort_sema.cohortOutcomes,
                       therapy_name=param.Therapies.SEMA)
support.print_outcomes(sim_outcomes=cohort_tirz.cohortOutcomes,
                       therapy_name=param.Therapies.TIRZ)

# print comparative outcomes
support.print_comparative_outcomes(sim_outcomes_mono=cohort_sema.cohortOutcomes,
                                   sim_outcomes_combo=cohort_tirz.cohortOutcomes)

# report the CEA results
support.report_CEA_CBA(sim_outcomes_mono=cohort_sema.cohortOutcomes,
                       sim_outcomes_combo=cohort_tirz.cohortOutcomes)

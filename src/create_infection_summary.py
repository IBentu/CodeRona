import sys
import os
from functional import seq
import statistics
import pandas
from matplotlib import pyplot


def sort_runs(a, b):
    return short_name(a) > short_name(b)


def get_run_folders(root_dir):
    all_runs = [x for x in os.listdir(root_dir) if x[0] != "." and "csv" not in x and "svg" not in x]
    all_runs = seq(all_runs).sorted(short_name).list()
    return all_runs


def find_file_containing(root_dir, containing_string):
    file_name = [x for x in os.listdir(root_dir) if containing_string in x and "csv" in x]
    return file_name[0]


def calc_cumulative_stddev(means, stddevs, repetitions):
    for i in range(len(means)):
        a = stddevs[i]^2 * (repetitions -1) + repetitions*(sum(means)/len(means) - means[i])


def get_sample_line(root_path, sample, amit_graph_type, line, as_is=False):
    filename = f"{root_path}/sample_{sample}/amit_graph_{amit_graph_type}.csv"
    if os.path.isfile(filename):
        data = seq.csv(filename)
        print(f'get_sample_line() of {amit_graph_type}, sample {sample}, line start with {data[line][0]}')
        if as_is:
            return [float(x) for x in data[line][1:]]
        else:
            return [max(0, float(x)) for x in data[line][1:]]
    return None


def get_daily_info(root_path):
    infected_sum = []
    infected_max = []

    for i in range(1000):
        data = get_sample_line(root_path, i, "integral", 1)
        if data is not None:
            infected_sum.append(sum(data))
            infected_max.append(max(data))
        else:
            break

    # infected_sum = []
    # for i in range(1000):
    #     susceptible = get_sample_line(root_path, i, "daily", 3, as_is=True)
    #     immune = get_sample_line(root_path, i, "daily", 4, as_is=True)
    #     total_infected = []
    #     if susceptible is not None and immune is not None:
    #         for day in range(1, len(susceptible)):
    #             total_infected.append(-susceptible[day] - immune[day])
    #     if len(total_infected) > 0:
    #         infected_sum.append(sum(total_infected))
    #     else:
    #         break

    critical_sum = []
    critical_max = []

    for i in range(1000):
        data = get_sample_line(root_path, i, "integral", 2)
        if data is not None:
            critical_sum.append(sum(data))
            critical_max.append(max(data))
        else:
            break

    return statistics.mean(infected_sum), statistics.stdev(infected_sum), \
           statistics.mean(critical_sum), statistics.stdev(critical_sum), \
           statistics.mean(infected_max), statistics.stdev(infected_max), \
           statistics.mean(critical_max), statistics.stdev(critical_max)


def short_name(one_run):
    parameters = one_run.split('_')
    city = parameters[0]
    if "ASCENDING" in one_run:
        order = "ASCENDING"
    elif "DESCENDING" in one_run:
        order = "DESCENDING"
    else:
        order = "NONE"
    if "HOUSEHOLDS_ALL_AT_ONCE" in one_run:
        household = "HH_ALL_AT_ONCE"
    elif "HOUSEHOLD" in one_run:
        household = "HOUSEHOLD"
    else:
        household = "GENERAL"
    immune_per_day = 0
    for i in range(len(parameters)):
        if parameters[i] == 'day':
            immune_per_day = parameters[i+1]
    initial_infected = 0
    for i in range(len(parameters)):
        if parameters[i] == 'inf' and parameters[i+2] == "immune":
            initial_infected = parameters[i+1]
    return f"{city}\nINF={initial_infected}\nIMMUNE={immune_per_day}\n{household}\n{order}"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("ERROR! please provide one argument which is the date/time of the run")
        exit(-1)

    all_runs = get_run_folders(f"../outputs/{sys.argv[1]}")
    df = pandas.DataFrame(columns=["scenario", "immune_order", "total_infected", "std_infected", "total_critical", "std_critical",
                                   "max_infected", "std_max_infected", "max_critical", "std_max_critical"])
    for one_run in all_runs:
        # daily_csv_filename = find_file_containing(f"../outputs/{sys.argv[1]}/{one_run}", "amit_graph_daily")
        # daily_integral_filename = find_file_containing(f"../outputs/{sys.argv[1]}/{one_run}", "amit_graph_integral")

        daily = get_daily_info(f"../outputs/{sys.argv[1]}/{one_run}")
        df = df.append({"scenario": one_run, "immune_order": short_name(one_run),
                        "total_infected": daily[0], "std_infected": daily[1], "total_critical": daily[2], "std_critical": daily[3],
                       "max_infected": daily[4], "std_max_infected": daily[5], "max_critical": daily[6], "std_max_critical": daily[7]},
                       ignore_index=True)

        # daily_integral = seq.csv(f"../outputs/{sys.argv[1]}/{one_run}/{daily_integral_filename}")
        # infected = [float(x) for x in daily_integral[1][1:]]
        # max_infected = max(infected)
        # index_of_max_infected = infected.index(max_infected)
        # std_infected = daily_integral[3][1:][index_of_max_infected]



    df.to_csv(f"../outputs/{sys.argv[1]}/results.csv")


    fig, axs = pyplot.subplots(4, 1)
    fig.set_figwidth(20)
    fig.set_figheight(20)

    [ax.tick_params(axis='x', labelsize=6) for ax in axs]
    [ax.tick_params(axis='y', labelsize=6) for ax in axs]


    axs[0].bar(df["immune_order"], df["total_infected"], color="lightsteelblue")
    axs[0].errorbar(df["immune_order"], df["total_infected"], yerr=df["std_infected"], capsize=10, ecolor="cornflowerblue", fmt=".")
    axs[0].set_title("Total Infected")

    axs[1].bar(df["immune_order"], df["total_critical"], color="thistle")
    axs[1].errorbar(df["immune_order"], df["total_critical"], yerr=df["std_critical"], capsize=10, ecolor="slateblue", fmt=".")
    axs[1].set_title("Total Critical")

    axs[2].bar(df["immune_order"], df["max_infected"], color="lightsteelblue")
    axs[2].errorbar(df["immune_order"], df["max_infected"], yerr=df["std_max_infected"], capsize=10, ecolor="cornflowerblue", fmt=".")
    axs[2].set_title("Max Infected")

    axs[3].bar(df["immune_order"], df["max_critical"], color="thistle")
    axs[3].errorbar(df["immune_order"], df["max_critical"], yerr=df["std_max_critical"], capsize=10, ecolor="slateblue", fmt=".")
    axs[3].set_title("Max Critical")

    fig.suptitle(f'Analysis of simulation {sys.argv[1]}', fontsize=16)

    fig.tight_layout(pad=3.0)
    fig.savefig(f"../outputs/{sys.argv[1]}/results.svg")
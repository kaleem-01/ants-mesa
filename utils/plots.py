import pandas as pd
import matplotlib.pyplot as plt
import powerlaw
import numpy as np

def plot_mean_std(df_grouped, ax, column):
    mean = {}
    std = {}

    for name, group in df_grouped:
        mean[name] = group[column].mean()
        std[name] = group[column].std()

    ax.plot(mean.keys(), mean.values(), 'o')
    ax.fill_between(mean.keys(), [mean[k] - std[k] for k in mean.keys()], [mean[k] + std[k] for k in mean.keys()], alpha=0.2)
    # plt.errorbar(mean.keys(), mean.values(), yerr=std.values(), fmt='o')

    return mean, std


def load_and_prepare_data(file_path):
    """Loads dataset and extracts necessary columns."""
    df = pd.read_csv(file_path)

    # Convert entropy_log from string to list and extract last recorded entropy value
    if df["entropy_log"].dtype == "object":
        df["Final Entropy"] = df["entropy_log"].apply(lambda x: eval(x)[-1] if isinstance(x, str) else None)

    return df

def plot_variance_trends(df, ax=None, groupby="max_steps_without_food", column="Home 🏠", color="black"):
    """Plots variance of ant population to detect phase transitions."""
    variance_data = df.groupby(groupby)[column].std()
    print(variance_data)
    # plt.figure(figsize=(8, 5))
    ax.plot(variance_data.index, variance_data.values, marker='o', linestyle='-', color=color, label="Variance in Ant Population")
    # ax[0].legend()
    # ax[0].grid(True)
    # plt.show()

def plot_entropy_shifts(df, ax=None, groupby="max_steps_without_food", column="Final Entropy"):
    """Plots entropy shifts to analyze self-organization in the system."""
    entropy_data = df.groupby(groupby)[column].mean()

    # plt.figure(figsize=(8, 5))
    ax.plot(entropy_data.index, entropy_data.values, marker='s', linestyle='-', color="purple", label="Mean Entropy")
    ax.set_xlabel("Max Steps Without Food")
    ax.set_ylabel("Entropy")
    ax.set_title("Entropy Shifts: Detecting Self-Organization")
    # plt.legend()
    plt.grid(True)
    # plt.show()

def plot_phase_space(df, ax=None):
    """Plots phase space visualization of food collected vs. ant population."""
    ax.scatter(df["Ants 🐜"], df["Home 🏠"], alpha=0.5, s=10, color="green", label="Ant Population vs. Food Collected")
    ax.set_xlabel("Ant Population")
    ax.set_ylabel("Food Collected")
    ax.set_title("Phase Space: Food vs. Ant Population")
    # ax.legend()
    plt.grid(True)
    # plt.show()


def plot_powerlaw(data):
    """
    Plot the power law fit of the data

    Parameters:
    data (array): The data to fit

    Returns:
    None
    """
    results = powerlaw.Fit(data)

    plt.figure(figsize=(8, 6))
    results.plot_pdf(color='blue', linestyle='-', label='Empirical Data')
    results.power_law.plot_pdf(color='red', linestyle='--', label='Power Law Fit')

    alpha = results.power_law.alpha  # Exponent α
    xmin = results.power_law.xmin   # Lower bound x_min

    print(f"Alpha: {alpha}")
    print(f"Xmin: {xmin}")


    #     # Fit the data (set discrete=True if your data is integer-based)
    # fit = powerlaw.Fit(data, discrete=False, xmin=820.04)  # Use xmin=820.04 if known

    # # Plot the Complementary Cumulative Distribution Function (CCDF)
    # results.plot_ccdf(label='Empirical Data', color='blue', linewidth=2)
    # results.power_law.plot_ccdf(label='Power-Law Fit', linestyle='--', color='red', linewidth=2)

    # # Add axis labels and title
    # plt.xlabel('Value (x)', fontsize=12)
    # plt.ylabel('P(X ≥ x)', fontsize=12)  # Probability of X being greater than or equal to x
    # plt.title('Power-Law Fit to Data', fontsize=14)
    # plt.legend()

    R, p = results.distribution_compare('power_law', 'lognormal')
    print(f"R: {R}")
    print(f"p: {p}")
    # Print fitted parameters
    print(f"Fitted α (alpha): {results.power_law.alpha:.2f}")
    print(f"Fitted x_min: {results.power_law.xmin:.2f}")
    print(f"Standard error in α: {results.power_law.sigma:.2f}")
    # print(f"Goodness-of-fit p-value: {results.power_law:.3f}")

    # results.plot_ccdf(label='Data')
    # results.power_law.plot_ccdf(label='Fit', linestyle='--')
    # plt.show()
    # plt.title("Power Law fit of Food Collected vs Initial Ants")
    # plt.xlabel("Initial Ants")
    # plt.ylabel("Food Collected")

    


def main(filename, groupby):
    # filename = "max_steps_wo_food_large.csv"
    # groupby = "max_steps_without_food"
    # filename = "prob_random_large.csv"
    # groupby = "prob_random"
    # filename = "init_ants.csv"
    # groupby = "init_ants"
    # filename = "pheromone_evaporate.csv"
    # groupby = "evaporate"

    df = load_and_prepare_data(filename)
    df_grouped = df.groupby(groupby)
    fig, (ax1, ax3) = plt.subplots(2, 1, figsize=(8, 12))
    plot_variance_trends(df, ax1, groupby=groupby, column="Ants 🐜", color="red")
    # plot_variance_trends(df, ax2, groupby=groupby, column="dead_ants", color="blue")
    plot_variance_trends(df, ax3, groupby=groupby, column="Home 🏠", color="green")

    # ax1.set_xlabel("Probability of Random Move")
    # ax1.set_xlabel("Max Steps Without Food")
    ax1.set_ylabel(f"Variance in Ant Population")
    ax1.set_title("Variance Trends")

    # ax2.set_xlabel("Max Steps Without Food")
    # ax2.set_ylabel(f"Variance in the Number of Dead Ants")

    ax3.set_ylabel(f"Variance in Food Collected")
    ax3.set_xlabel("Pheromone Evaporation Rate")



    plt.tight_layout()
    # plt.savefig(f"plots/variance_trends {column}.png", dpi=600)
    plt.show()

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 12))

    plot_mean_std(df_grouped, ax1, 'Home 🏠')
    plot_mean_std(df_grouped, ax2, 'Ants 🐜')
    plot_mean_std(df_grouped, ax3, 'pheromone_ant_avg')

    ax1.set_title("Mean and Standard Deviation of Metrics")
    ax1.set_ylabel("Food Collected")
    ax2.set_ylabel("Ant Population")
    ax3.set_ylabel("Pheromone Ants Ratio")
    ax3.set_xlabel("Pheromone Evaporation Rate")

    plt.tight_layout()
    plt.show()
    # plt.savefig("plots/mean_std pe.png", dpi=600)   

    fig, (ax1) = plt.subplots(1, 1)

    plot_entropy_shifts(df, ax1, groupby=groupby)
    ax1.set_xlabel("Pheromone Evaporation Rate")
    ax1.set_ylabel("Entropy")
    ax1.set_title("Entropy Shifts: Detecting Self-Organization")

    plt.tight_layout()
    # plt.savefig("plots/entropy_shifts pe.png", dpi=600)
    plt.show()
    # plot_phase_space(df, ax2)
    # ax3.set_xlabel("")



    # ax2.set_title("Variance Trends")
    

    # filename_2 = "prob_random_large.csv"
    # filename_3 = "init_ants_large.csv"
    # file

    # print(df.head())

    # plot_variance_trends(df, ax1, groupby=groupby, column="Home 🏠")



    # plot_phase_space(df, ax3)
    # fig.legend()
    # plt.tight_layout()
    # plt.show()
    
    # plt.savefig(f"plots/mean_std max_steps.png", dpi=600)


if __name__ == '__main__':
    main()

    # filename = "prob_random_large.csv"
    # filename = "max_step_without_ant.csv"
    # filename = "init_ants_large.csv"

    # np.random.seed(0)
    # filename = "max_steps_wo_food_large.csv"
    # df = pd.read_csv(filename)
    # df_grouped = df.groupby("max_steps_without_food")



    # for name, group in df_grouped:
    #     print(group)
    #     break
    # df_grouped_init = df.groupby("prob_random")


    
    # Home
    # column = "dead_ants"
    # column = "Step"
    # column = "Home 🏠"


    # column = "pheromone_ant_avg"
    # column = "pheromone_ant_avg"
    # column = "dead_ants" # Alpha: 5.31 Xmin = 820
    # column = "ants_eaten"
    # column = "Step"
    # column = "Food 🍯"


    # df["Harvested"] = df['Food 🍯'][0] - df["Food 🍯"]
    # column = "Harvested" 
    # column = "dead_predators"   # noresults

    # print(df.columns)

    # plot_mean_std(df_grouped, 'Home 🏠')
#     wo_mean, wo_std = plot_mean_std(df_grouped, column=column)
#     plt.ylabel(column)
#     plt.xlabel("max_steps_wo_ants")
#     plt.show()

#     # plt.xlabel(filename)
#     # plt.ylabel(column)
#     plt.show()
#     # plt.clear()


#     print(wo_mean.values())
#     plot_powerlaw(list(wo_mean.values()))
#     plt.title(f"{column} vs Max Steps Without Food")
#     # plt.xlabel("Max Steps Without Food")
    


#     # plt.title(f"{column} vs Initial Ants")
#     # plt.xlabel(column)
#     # plt.ylabel(column)
    



# # init_mean, init_std = plot_mean_std(df_grouped_init, "Food 🍯")

#     plt.title("Food collected vs max steps without food")
#     plt.xlabel("Max steps without food")
#     plt.ylabel("Food collected")
#     plt.show()
    # plt.xlabel("Initial Ants")
    # plt.ylabel("Food Collected")
    # plt.show()
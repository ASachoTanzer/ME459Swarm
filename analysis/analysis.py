import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def aggregate_time_series(dfs):
    """Given list of DataFrames (with 'time' and metric columns),
    return DataFrame indexed by time with mean of each metric at each time (outer joined).
    """
    if not dfs:
        return pd.DataFrame()

    metrics = ['cvfm', 'mean_hbc', 'on_target']
    times = sorted({t for df in dfs for t in df['time'].tolist()})
    agg = pd.DataFrame(index=times)
    for i, df in enumerate(dfs):
        run = df.set_index('time')
        run = run.reindex(times)
        for m in metrics:
            agg[f'{m}_run_{i}'] = run[m].values

    result = pd.DataFrame(index=times)
    for m in metrics:
        cols = [c for c in agg.columns if c.startswith(f'{m}_run_')]
        result[m] = agg[cols].mean(axis=1)
    result.index.name = 'time'
    return result


def clean_data(dfs):
    # resample dfs to consistent timesteps
    dfs_aligned = []
    for df in dfs:
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df = df.resample(".1s", on="time").mean()
        df.reset_index(inplace=True)
        df["time"] = df["time"].astype("int64")/1e9
        dfs_aligned.append(df)
    return dfs_aligned
    


save_plots = False
show_plots = True

results_dir = "./results/"
plots_dir = "./plots/"

csv_paths = [f"{results_dir}/{f}" for f in os.listdir(results_dir) if f.endswith('.csv')]

decentralized_results = []
mothership_results = []

for path in csv_paths:
    df = pd.read_csv(path)
    df = df.rename(columns={'t': 'time'})
    if 'decentralized' in path.lower():
        decentralized_results.append(df)
    elif 'mothership' in path.lower():
        mothership_results.append(df)
    else:
        print(f"Warning: could not classify {path} as decentralized or mothership based on filename")

decentralized_results = clean_data(decentralized_results)
mothership_results = clean_data(mothership_results)


# Per-file plotting
fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(9, 10), sharex=True)
for idx, (results, kind) in enumerate([(decentralized_results, 'decentralized'), (mothership_results, 'mothership')]):
    for df in results:
        axes[idx, 0].plot(df['time'], df['cvfm'])
        axes[idx, 1].plot(df['time'], df['mean_hbc'])
        axes[idx, 2].plot(df['time'], df['on_target'])
    axes[idx, 0].set_xlabel('time')
    axes[idx, 0].set_ylabel('cvfm')
    axes[idx, 0].set_title(f'{kind} cvfm')
    axes[idx, 1].set_xlabel('time')
    axes[idx, 1].set_ylabel('mean_hbc')
    axes[idx, 1].set_title(f'{kind} mean_hbc')
    axes[idx, 2].set_xlabel('time')
    axes[idx, 2].set_ylabel('on_target')
    axes[idx, 2].set_title(f'{kind} on_target')

    
plt.tight_layout()
if save_plots:
    out = f"{plots_dir}individual_metrics.png"
    plt.savefig(out)
if show_plots:
    plt.show()
# plt.close()


# Plot averaged metrics in separate figure windows
fig_cvfm, ax_cvfm = plt.subplots(figsize=(6, 4))
fig_hbc, ax_hbc = plt.subplots(figsize=(6, 4))
fig_on, ax_on = plt.subplots(figsize=(6, 4))

for results, kind in [(decentralized_results, 'decentralized'), (mothership_results, 'mothership')]:
    avg_data = aggregate_time_series(results)
    # if not avg_data.empty:
    ax_cvfm.plot(avg_data.index, avg_data['cvfm'], label=kind)
    ax_hbc.plot(avg_data.index, avg_data['mean_hbc'], label=kind)
    ax_on.plot(avg_data.index, avg_data['on_target'], label=kind)

ax_cvfm.set_xlabel('time')
ax_cvfm.set_ylabel('cvfm')
ax_cvfm.set_title('cvfm')
ax_cvfm.grid()
ax_cvfm.legend()

ax_hbc.set_xlabel('time')
ax_hbc.set_ylabel('mean_hbc')
ax_hbc.set_title('mean_hbc')
ax_hbc.grid()
ax_hbc.legend()

ax_on.set_xlabel('time')
ax_on.set_ylabel('on_target')
ax_on.set_title('on_target')
ax_on.grid()
ax_on.legend()

plt.tight_layout()
if save_plots:
    fig_cvfm.savefig(f"{plots_dir}average_cvfm.png")
    fig_hbc.savefig(f"{plots_dir}average_mean_hbc.png")
    fig_on.savefig(f"{plots_dir}average_on_target.png")
if show_plots:
    # fig_cvfm.show()
    # fig_hbc.show()
    # fig_on.show()
    plt.show()


# Print summary statistics
print('\nSummary statistics:')
metrics = ['cvfm', 'mean_hbc', 'on_target']

for dfs, kind in [(decentralized_results, 'decentralized'), (mothership_results, 'mothership')]:
    if not dfs:
        print(f' - {kind}: no runs')
        continue


    # overall average value of each metric for this run type (average all data points)
    for m in metrics:
        all_vals = np.hstack([df[m].values.flatten() for df in dfs])
        mean_val = all_vals.mean()
        print(f' - {kind} {m}: overall mean = {mean_val:.4f}')

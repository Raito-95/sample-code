import re
import pandas as pd
import matplotlib.pyplot as plt

def extract_diff_values(file_path):
    pattern = re.compile(r'diff: ch(\d) = (-?\d+)')
    
    data = {f'ch{i}': [] for i in range(8)}
    index_data = {f'ch{i}': [] for i in range(8)}
    
    index_counter = 0
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            matches = pattern.findall(line)
            if matches:
                for ch, value in matches:
                    data[f'ch{ch}'].append(int(value))
                    index_data[f'ch{ch}'].append(index_counter)
                index_counter += 1
    
    dfs = {ch: pd.DataFrame({'Index': index_data[ch], 'Value': data[ch]}) for ch in data if data[ch]}
    
    return dfs

def plot_diff_values(dfs, sample_rate=1):
    fig, axes = plt.subplots(4, 2, figsize=(12, 8), sharex=True)
    
    for i, (ch, df) in enumerate(dfs.items()):
        row, col = divmod(i, 2)
        ax = axes[row, col]
        ax.plot(df['Index'][::sample_rate], df['Value'][::sample_rate])
        ax.set_ylabel('Diff Value')
        ax.set_title(f'Channel {ch}')
        ax.grid()
    
    plt.xlabel('Index')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    file_path = ""
    diff_dfs = extract_diff_values(file_path)
    plot_diff_values(diff_dfs, sample_rate=1)
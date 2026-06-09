import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    df = pd.read_csv('data/qb_2022.csv')

    numeric = df.select_dtypes(include='number')

    correlation = numeric.corr()

    print(correlation)

    plt.figure(figsize=(16, 12))
    sns.heatmap(
    correlation,
    annot=True,  # Show correlation numbers inside the blocks
    cmap="coolwarm",  # Diverging color palette (blue = negative, red = positive)
    vmin=-1,
    vmax=1,  # Set colorbar range limits
    fmt=".2f",  # Limit numeric text to 2 decimal places
    )

    plt.title("Correlation Matrix Heatmap")
    plt.tight_layout()
    plt.savefig('exploration/eda_figs/qb_correlation_matrix.png')

if __name__ == '__main__':
    main()
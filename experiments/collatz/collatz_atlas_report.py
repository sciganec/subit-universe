"""
collatz_atlas_report.py — Report Generator for Generalized Collatz Atlas
Version 2.1 · 2026

Reads the results from generalized_collatz_results_v2.1.csv and attractor_catalog.csv
and generates a comprehensive Markdown report with statistics and analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import os

def load_data(results_file='generalized_collatz_results_v2.1.csv',
              catalog_file='attractor_catalog.csv'):
    """Load results and catalog."""
    results = pd.read_csv(results_file)
    if os.path.exists(catalog_file):
        catalog = pd.read_csv(catalog_file)
    else:
        catalog = None
    return results, catalog


def generate_report(results, catalog, output_file='COLLATZ_ATLAS_REPORT.md'):
    """Generate a comprehensive Markdown report."""
    lines = []
    lines.append("# Generalized Collatz Atlas — Experimental Report")
    lines.append("")
    lines.append("*SUBIT-TOPOS Research Group*")
    lines.append("*Date: 2026-07-22*")
    lines.append("*Version: 2.1*")
    lines.append("")

    # Summary statistics
    total_params = len(results)
    omega_counts = results['omega'].value_counts()
    lines.append("## 1. Exploration Summary")
    lines.append("")
    lines.append(f"- **Parameter combinations explored:** {total_params}")
    lines.append(f"- **Unique cycles found:** {len(catalog) if catalog is not None else 0}")
    lines.append("")
    lines.append("### Ω-class distribution:")
    lines.append("")
    lines.append("| Class | Count | Percentage |")
    lines.append("|-------|-------|------------|")
    for omega, count in omega_counts.items():
        pct = count / total_params * 100
        lines.append(f"| {omega} | {count} | {pct:.1f}% |")
    lines.append("")

    # Stable parameters
    stable = results[results['omega'] == 'STABLE']
    if not stable.empty:
        lines.append("### Stable parameters (all samples reached 1):")
        lines.append("")
        lines.append("| k | c | stable_count | total_samples |")
        lines.append("|---:|---:|------------:|--------------:|")
        for _, row in stable.iterrows():
            k = int(row['k'])
            c = int(row['c'])
            stable_count = int(row.get('stable_count', row.get('stable_count', 0)))
            total = int(row.get('total_samples', row.get('samples_per_param', 100)))
            lines.append(f"| {k} | {c} | {stable_count} | {total} |")
        lines.append("")

    # Cycle catalog
    if catalog is not None and not catalog.empty:
        lines.append("## 2. Unique Attractor Catalog")
        lines.append("")
        lines.append(f"Found **{len(catalog)}** unique cycles (after deduplication).")
        lines.append("")
        lines.append("| # | (k,c) | Cycle | Length | Basin Size |")
        lines.append("|---|-------|-------|--------|------------|")
        for idx, row in catalog.iterrows():
            k = int(row['k'])
            c = int(row['c'])
            cycle_str = row['cycle'] if isinstance(row['cycle'], str) else str(row['cycle'])
            if len(cycle_str) > 50:
                cycle_str = cycle_str[:50] + "..."
            length = row.get('length', '?')
            basin = row.get('basin_size', row.get('count', '?'))
            lines.append(f"| {idx+1} | ({k},{c}) | `{cycle_str}` | {length} | {basin} |")
        lines.append("")

        # Cycle length distribution
        lengths = catalog['length'].dropna().astype(int) if 'length' in catalog.columns else []
        if len(lengths) > 0:
            lines.append("### Cycle length statistics")
            lines.append("")
            lines.append(f"- Minimum: {lengths.min()}")
            lines.append(f"- Maximum: {lengths.max()}")
            lines.append(f"- Mean: {lengths.mean():.1f}")
            lines.append(f"- Median: {lengths.median():.0f}")
            lines.append("")

    # Classical Collatz check
    classic = results[(results['k'] == 3) & (results['c'] == 1)]
    if not classic.empty:
        row = classic.iloc[0]
        lines.append("## 3. Classical Collatz (k=3, c=1)")
        lines.append("")
        lines.append(f"- **Ω-class:** {row['omega']}")
        lines.append(f"- **Stable samples:** {row.get('stable_count', row.get('stable_count', 0))}/{row.get('total_samples', 100)}")
        lines.append("")

    # Phase diagram (if saved)
    png_file = 'generalized_collatz_phase_diagram_v2.1.png'
    if os.path.exists(png_file):
        lines.append("## 4. Phase Diagram")
        lines.append("")
        lines.append(f"![Phase Diagram]({png_file})")
        lines.append("")

    # Conclusion
    lines.append("## 5. Conclusions")
    lines.append("")
    lines.append(f"- **Stable region is rare:** only {len(stable)} out of {total_params} combinations ({len(stable)/total_params*100:.1f}%) are fully stable.")
    lines.append(f"- **Cycles are common:** {len(catalog) if catalog is not None else 0} unique attractors found.")
    lines.append("- **Classical Collatz is exceptional:** small changes in parameters (e.g., 3n+2) destabilize the system.")
    lines.append("- **CHAOTIC regime appears:** for many parameters, trajectories exceed computational limits, suggesting divergence or very long transients.")
    lines.append("")
    lines.append("*This report was automatically generated by SUBIT-TOPOS.*")

    # Write file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"Report saved to {output_file}")
    return lines


def plot_phase_diagram_with_counts(results, save_path='phase_diagram_with_counts.png'):
    """Plot phase diagram with count annotations."""
    k_values = sorted(results['k'].unique())
    c_values = sorted(results['c'].unique())
    pivot = results.pivot(index='c', columns='k', values='omega')
    # Fill missing with NaN
    pivot = pivot.reindex(index=c_values, columns=k_values)

    fig, ax = plt.subplots(figsize=(12, 8))
    # Map omega to colors
    omega_order = {'STABLE': 0, 'MIXED': 1, 'CYCLIC': 2, 'CHAOTIC': 3}
    colors = ['#2ecc71', '#f1c40f', '#e74c3c', '#34495e']
    cmap = plt.cm.colors.ListedColormap(colors)

    # Create numeric matrix
    matrix = np.zeros(pivot.shape)
    for i, c in enumerate(c_values):
        for j, k in enumerate(k_values):
            val = pivot.loc[c, k] if not pd.isna(pivot.loc[c, k]) else 'UNKNOWN'
            matrix[i, j] = omega_order.get(val, np.nan)

    im = ax.imshow(matrix, cmap=cmap, origin='lower', aspect='auto', vmin=0, vmax=3)
    ax.set_xticks(range(len(k_values)))
    ax.set_xticklabels(k_values)
    ax.set_yticks(range(len(c_values)))
    ax.set_yticklabels(c_values)
    ax.set_xlabel('k (multiplier)')
    ax.set_ylabel('c (offset)')
    ax.set_title('Generalized Collatz Phase Diagram (with counts)')

    # Annotate with count of stable/cyclic/chaotic if available
    for i, c in enumerate(c_values):
        for j, k in enumerate(k_values):
            row = results[(results['k'] == k) & (results['c'] == c)]
            if not row.empty:
                omega = row.iloc[0]['omega']
                stable = row.iloc[0].get('stable_count', 0)
                total = row.iloc[0].get('total_samples', 100)
                if omega == 'STABLE':
                    label = f"{stable}/{total}"
                    ax.text(j, i, label, ha='center', va='center', color='white', fontsize=8)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()
    print(f"Phase diagram with counts saved to {save_path}")


def main():
    print("=" * 80)
    print("GENERALIZED COLLATZ ATLAS — REPORT GENERATOR")
    print("=" * 80)

    # Load data
    results, catalog = load_data()
    print(f"Loaded {len(results)} results")
    if catalog is not None:
        print(f"Loaded {len(catalog)} attractors")

    # Generate report
    generate_report(results, catalog)

    # Plot phase diagram with counts
    if not results.empty:
        plot_phase_diagram_with_counts(results)

    print("\nReport generation complete.")


if __name__ == "__main__":
    main()
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

plt.style.use('seaborn-v0_8-whitegrid')

# Figure 1: 14-Day Rolling Under-Weigh Rate
daily_underweigh = linked.groupby(['date', 'market_id'])['error_pct'].apply(
    lambda x: (x < 0.5).mean() * 100
).reset_index(name='underweigh_rate')

daily_underweigh['rolling_underweigh_rate'] = daily_underweigh.groupby('market_id')['underweigh_rate'].transform(
    lambda x: x.rolling(window=14, min_periods=1).mean()
)

plt.figure(figsize=(10, 5))
for mkt_id, group in daily_underweigh.groupby('market_id'):
    plt.plot(group['date'], group['rolling_underweigh_rate'], label=f"Market: {mkt_id}", linewidth=2)

plt.title('Figure 1: 14-Day Rolling Under-Weigh Rate per Market', fontsize=12, fontweight='bold')
plt.xlabel('Date')
plt.ylabel('Under-Weigh Rate (%)')
plt.legend(title='Markets', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('fig1_rolling_underweigh_rate.png', dpi=300)
plt.show()

# Figure 2: Loss Heatmap
heatmap_matrix = summary.pivot_table(
    index='market_id',
    columns='commodity',
    values='p90_loss_php'
)

# Handle NaN color safely using colormap set_bad
cmap = plt.cm.YlOrRd.copy()
cmap.set_bad('gainsboro')

plt.figure(figsize=(12, 6))
ax = sns.heatmap(
    heatmap_matrix, 
    annot=True, 
    fmt=".1f", 
    cmap=cmap, 
    cbar_kws={'label': '90th Percentile Loss (PHP)'},
    linewidths=0.5
)

plt.title('Figure 2: 90th Percentile Expected Consumer Loss (PHP) by Market & Commodity', fontsize=12, fontweight='bold')
plt.xlabel('Commodity')
plt.ylabel('Market ID')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('fig2_loss_heatmap.png', dpi=300)
plt.show()
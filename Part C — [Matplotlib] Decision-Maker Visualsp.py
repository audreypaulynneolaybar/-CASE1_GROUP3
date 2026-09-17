import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

plt.style.use('seaborn-v0_8-whitegrid')

# Figure 1: Drift Chart - 14-Day Rolling Under-Weigh Rate per Market
daily_underweigh = linked.groupby(['date', 'market_id'])['error_pct'].apply(
    lambda x: (x < -0.5).mean() * 100
).reset_index(name='underweigh_rate')

daily_underweigh['rolling_underweigh_rate'] = daily_underweigh.groupby('market_id')['underweigh_rate'].transform(
    lambda x: x.rolling(window=14, min_periods=1).mean()
)

plt.figure(figsize=(10, 5))
for mkt_id, group in daily_underweigh.groupby('market_id'):
    plt.plot(group['date'], group['rolling_underweigh_rate'], label=f"Market: {mkt_id}", linewidth=2)

plt.title('Figure 1: 14-Day Rolling Under-Weigh Rate per Market (Drift Chart)', fontsize=12, fontweight='bold')
plt.xlabel('Date')
plt.ylabel('Under-Weigh Rate (%)')
plt.legend(title='Markets', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('fig1_rolling_underweigh_rate.png', dpi=300)
plt.show()

# Figure 2: Loss Heatmap - Median Expected Loss (PHP) by Market x Commodity
# Recalculate median loss per market x commodity pair
median_loss_matrix = linked.groupby(['market_id', 'commodity'])['loss_php'].median().unstack()

cmap = plt.cm.YlOrRd.copy()
cmap.set_bad('gainsboro')

plt.figure(figsize=(12, 6))
ax = sns.heatmap(
    median_loss_matrix, 
    annot=True, 
    fmt=".1f", 
    cmap=cmap, 
    cbar_kws={'label': 'Median Expected Loss (PHP)'},
    linewidths=0.5
)

plt.title('Figure 2: Median Expected Consumer Loss (PHP) by Market & Commodity', fontsize=12, fontweight='bold')
plt.xlabel('Commodity')
plt.ylabel('Market ID')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('fig2_loss_heatmap.png', dpi=300)
plt.show()

# Figure 3: Before-After Small Multiples - Under-Weigh Distribution 30 Days Before vs After Calibration
mid_date = linked['date'].min() + pd.Timedelta(days=45)
linked['calibration_phase'] = np.where(linked['date'] < mid_date, '30 Days Before', '30 Days After')

g = sns.FacetGrid(
    linked, 
    col="market_id", 
    hue="calibration_phase", 
    palette="Set1", 
    col_wrap=3, 
    height=3, 
    aspect=1.3
)
g.map(sns.kdeplot, "error_pct", fill=True, alpha=0.4)
g.add_legend(title="Calibration Phase")
g.set_axis_labels("Scale Error (%)", "Density")
g.set_titles(col_template="Market: {col_name}")
g.fig.subplots_adjust(top=0.85)
g.fig.suptitle('Figure 3: Under-Weigh Distribution (30 Days Before vs After Calibration Drive)', fontsize=12, fontweight='bold')
plt.savefig('fig3_before_after_distribution.png', dpi=300)
plt.show()
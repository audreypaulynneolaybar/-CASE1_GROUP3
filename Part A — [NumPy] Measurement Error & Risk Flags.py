import numpy as np
import pandas as pd

#babasahin ung inspections.csv dataset (df-dataframe)
df = pd.read_csv("inspections.csv")

#kukunin yung specific columns sa inspections csv tapos pagsasamahin, gagawing numpy array'ed
nominal_weight = df["nominal_weight_g (test mass)"].to_numpy() #test mass
reading = df["reading_g (scale reading)"].to_numpy() #scale reading
market_id = df["market_id"].to_numpy() #id ng market'ed

#calculation for the error'ed's (scale error in grams and percent)
error_g = reading - nominal_weight
error_p = 100 * (error_g / nominal_weight)

#pandetect if underweight or overweight ung nasa scale
underweight= error_p < -0.5
overweight = error_p > 0.5
out_of_tolerance = underweight | overweight

#program itself
#magloloop sya sa market_ids (buong row) tapos kukunin yung mean, median, 95% CI and out of tolerance
#np.unique() hinahanap yung specific value sa numpy array na spinecify ko based sa code

unique_markets = np.unique(market_id)

for m in unique_markets:
  mask = market_id == m

  market_data = df[mask]
  m_error = error_p [mask]

  #mean median
  mean_error = np.mean(m_error)
  median_error = np.median(m_error)

  # 95% CI, (Large-N approximation - Mean +- 1.96 * standard error)
  #meaning'ed : ineestimate neto yung
  se = np.std(m_error, ddof = 1) / np.sqrt(len(m_error))
  ci_95 = (mean_error - 1.96 * se, mean_error + 1.96 * se)

  frac_out = np.mean(out_of_tolerance[mask])
  frac_under = np.mean(underweight[mask])

#priprint ung mga market from 1-5 (mean med, 95 ci)
  print(f"--- Market: {m} ---")
  print(f"Mean Error (%): {mean_error:.3f}%")
  print(f"Median Error (%): {median_error:.3f}%")
  print(f"95% CI: [{ci_95[0]:.3f}%, {ci_95[1]:.3f}%]")
  print(f"Fraction Out of Tolerance: {frac_out:.2%}")
  print(f"Consumer Risk (Under-weighing): {frac_under:.2%}\n")

"""
    Subject: Dual-Stage Attention Model for Prediction Asset
    
    Copyright (C) 2021 of Insight AI. All rights reserved.
    Licence: SK Holdings C&C, Insight AI
    
    Status: Development
    Version: 0.01
    
    Python Version: 3.6.0
    tensorflow Version: 1.14.0
"""



import pandas as pd
# import feather
import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['figure.figsize'] = (8,8)

from ordinal_tsf.model import MordredStrategy
from ordinal_tsf.dataset import Dataset, Quantiser, Standardiser, OrdinalPrediction


import os
os.environ["CUDA_VISIBLE_DEVICES"]="0"

import numpy as np
np.random.seed(1)



# In this notebook, we show how to use our pre-trained models to predict time series, even when there are few observations at hand.
# Our example predicts the quasi-seasonal component of the  CO$_2$ data from the $\href{https://www.esrl.noaa.gov/gmd/ccgg/trends/}{\text{Mauna Loa observatory}}$.
# This dataset only has about 500 training examples (excluding the validation and testing segments).
co2_pd = pd.read_csv('data/co2_mm_mlo.csv')
seasonal_ts = (co2_pd['interpolated'] - co2_pd['trend']).values[:, np.newaxis]

print('Dataset has {} unique values.'.format(np.unique(seasonal_ts).shape[0]))
plt.plot(seasonal_ts)
plt.title('Quasi-seasonal component of CO2 dataset.')
plt.show()


### We start by making our data zero-mean and unit variance and quantising it, as shown in our previous example notebook.
LOOKBACK = 20
HORIZON = 20
N_BINS = 150
frame_length = LOOKBACK + HORIZON + 1

stand = Standardiser()
x = Dataset(seasonal_ts, frame_length, preprocessing_steps=[stand])


quant = Quantiser(150)
quant.fit(x.train_ts[:, 0])
x_quant = Dataset(seasonal_ts, frame_length, preprocessing_steps=[stand, quant])

plt.plot(x_quant.train_ts.argmax(axis=-1))
plt.title('Quantised training dataset.')
plt.show()



# A MOrdReD model trained from scratch doesn't do well on this dataset
train_spec = {'epochs':100, 'batch_size': 64}
model_scratch = MordredStrategy(ordinal_bins=150, units=256, dropout_rate=0.35, 
                                lam=1e-5, lookback=LOOKBACK, horizon=HORIZON)
model_scratch.fit(x_quant.train_frames, **train_spec)

pred = model_scratch.predict(x_quant.val_ts[np.newaxis, :HORIZON+1], predictive_horizon=HORIZON)
pred['bins'] = quant.bins
ord_pred = OrdinalPrediction(**pred)
ax = plt.subplot()
ord_pred.plot_median_2std(ax, x.val_ts[LOOKBACK+1:2*LOOKBACK+1])
plt.show()



# But using one of our pre-trained models, we can achieve better performance
# Our pre-trained models can be found in the "pretrained" folder, and they are grouped into "short lookback" (20 samples) and "medium lookback" (50 samples). 
train_spec = {'epochs':100, 'batch_size': 64}
this_fname = 'pretrained/lookback20/gum_20_150_bins_256_hidden_0.5_dropout_1e-05_l2'
model = MordredStrategy.load(this_fname)
model.fit(x_quant.train_frames, **train_spec)

pred = model.predict(x_quant.val_ts[np.newaxis, :HORIZON+1], predictive_horizon=HORIZON)
pred['bins'] = quant.bins
ord_pred = OrdinalPrediction(**pred)

ax = plt.subplot()
ord_pred.plot_median_2std(ax, x.val_ts[LOOKBACK+1:2*LOOKBACK+1])
plt.show()

"""
.. _tut-make-fixed-length-epochs:

Creating epochs of equal length
========================

This tutorial shows how to create equal length epochs and briefly demonstrates
an example of their use in connectivity analysis.

First, we import necessary modules and read in a sample raw
data set. This data set contains brain activity that is event-related, i.e.
synchronized to the onset of auditory stimuli. However, rather than creating
epochs by segmenting the data around the onset of each stimulus, we will
create 30 second epochs that allow us to perform non-event-related analyses of
the signal.
"""

import os
import mne
import matplotlib.pyplot as plt
from mne.preprocessing import compute_proj_ecg
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np

picks = ['mag', 'grad']

sample_data_folder = mne.datasets.sample.data_path()
sample_data_raw_file = os.path.join(sample_data_folder, 'MEG', 'sample',
                                    'sample_audvis_raw.fif')

raw = mne.io.read_raw_fif(sample_data_raw_file)

# Remove heart artifact for cleanliness of data

ecg_proj, _ = compute_proj_ecg(raw, ch_name='MEG 0511')
ssp = raw.copy().apply_proj()

###############################################################################
# To create fixed length epochs, we simply call the function and provide it
# with the appropriate parameters indicating the desired duration of epochs in
# seconds, whether or not to preload data, whether or not to reject epochs that
# overlap with raw data segments annotated as bad, whether or not to include
# projectors, and finally whether or not to be verbose. Here, we choose a long
# epoch duration (10 seconds). To conserve memory, we set preload to
# False. We elect to reject segments of data marked as bad. In this case,
# the MEG sample data set includes SSP projectors that help control room noise
# in the data and will be left in for noise suppression.

epochs = mne.make_fixed_length_epochs(ssp, duration=30, preload=False,
                                      reject_by_annotation=True, proj=True,
                                      verbose=True)

###############################################################################
# Characteristics of Fixed Length Epochs
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# A key characteristic of fixed length epochs is that they are generally
# unsuitable for event-related analyses. Two quick visualizations will
# illustrate why. First, we create a time series butterfly plot grouping
# channels together by spatial region. Clear peaks of event-related activity
# corresponding to stimuli onsets are seen in each 10-second epoch, but peak
# timing is jittered across fixed-length epochs.

# Visualize the fixed length epochs

timeseries_plot = epochs.plot(n_epochs=8, picks=picks, group_by='selection',
                              butterfly=True)

###############################################################################
# Next, we pick a single channel and create an image map of our fixed length
# epochs. When the epochs are averaged, as seen at the bottom of the plot,
# misalignment between onsets of event-related activity results in noise.

event_related_plot = epochs.plot_image(picks=['MEG1142'])

###############################################################################
# For information about creating epochs for event-related analyses, please see
# PUT TUTORIAL REFERENCE HERE.

# Example Use Case for Fixed Length Epochs: Connectivity Analysis
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# Fixed lengths epochs are suitable for many types of analysis, including
# frequency or time-frequency analyses, connectivity analyses, or
# classification analyses. Here we briefly illustrate their utility in a sensor
# space connectivity analysis.
#
# The data from our epochs object has shape (n_epochs, n_sensors, n_times) and
# is therefore an appropriate basis for using MNE-Python's envelope correlation
# function to compute power-based connectivity in sensor space. The long
# duration of our fixed length epochs, 30 seconds, will help us reduce edge
# artifacts and achieve better frequency resolution when filtering must
# be applied after epoching.

# Let's examine the alpha band. We allow default values for filter parameters
# (for more information on filtering, please see PUT TUTORIAL REFERENCE HERE).

alpha = epochs.copy().load_data().filter(l_freq=8, h_freq=12)

# Compute envelope correlations in sensor space

epoch_data = epochs.get_data(picks=['mag', 'grad'])
corr_matrix = mne.connectivity.envelope_correlation(epoch_data, combine=None,
                                                    orthogonalize='pairwise',
                                                    log=False, absolute=True,
                                                    verbose=True)

###############################################################################
# If desired, separate correlation matrices for each epoch can be obtained.
# For envelope correlations, this is done by passing ``combine=None`` to the
# envelope correlations function.

# Plot correlation matrices from the first and last 30 second epochs of the
# recording
first_30 = corr_matrix[0]
last_30 = corr_matrix[-1]
c_matrices = [first_30, last_30]
titles = ['First 30 Seconds', 'Last 30 Seconds']

fig, axes = plt.subplots(nrows=1, ncols=2,
                         gridspec_kw=dict(width_ratios=[92, 100]), figsize=(8, 8))
fig.suptitle('Connectivity Matrices from First 30 Seconds and Last 30 Seconds')
for ci, c_matrix in enumerate(c_matrices):
    ax = axes[ci]
    low_lim, high_lim = np.percentile(c_matrix, [5, 95])
    mpbl = ax.imshow(c_matrix, clim=[low_lim, high_lim])
    ax.set_xlabel(titles[ci])
plt.subplots_adjust(right=0.92)
divider = make_axes_locatable(axes[1])
cax = divider.append_axes("right", size="5%", pad=0.1)
ticks = np.arange(0.05, 0.95, 0.1)
plt.colorbar(mpbl, cax=cax, ax=axes, ticks=ticks,
             label='Correlation Coefficient', )
plt.tight_layout()

This repository corresponds to "Enlightenment Ideals and Belief in Science in the Run-up to the Industrial Revolution: A Textual Analysis" by Ali Almelhem, Murat Iyigun, Austin Kennedy, and Jared Rubin

Global options are set in 'config.py'. Use these options to run the data trained on the full sample of volumes (main results) as well as data trained only on volumes published before 1750 (robustness).

The analysis can be run entirely via 'run_scripts.py'. It runs in the following order:

cross_topics.py --> categories.py --> shares.py --> topic_volume_weights.py --> volume_data.py --> volume_figures.py --> progress_econometrics.R --> industry_econometrics.R


Notes:
Plotly occasionally acts up when making ternary plots...it usually throws an error about 'kaleido' engine, on windows this is solved using 'pip install kaleido==0.1.0post1', on Mac this was solved simply by installing latest version of kaleido and plotly

If you get the following error running 'run_scripts.py': "The term 'Rscript' is not recognized as the name of a cmdlet, function,..." then you need to add your R installation to the PATH environmental variable on your machine.
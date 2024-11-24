# DV-HOPE
Data Visualization of Health Outcomes from social and environmental PrEdictors

# DESCRIPTION
DV-HOPE is a data visualization project aimed at exploring the relationships between
environmental/socioeconomic factors and health outcomes.

The main demonstration of this is a interactive choropleth map. You can visualize which states have worse predicted
health outcomes through the color intensity of each state, and click on each state to explore which industry sectors
are the top contributors to pollution.

Additionally, we include metrics on the model performance through Shapley Additive Explanations and other common metrics,
which might give additional insight into the interplay of the predicted variables. To view the performance of the model,
you can view the demo. To view all the machine learning experiments, check out the notebooks in CODE/model_evaluation.
To view some exploratory data analysis, checkout CODE/eda.

# INSTALLATION

No installation is needed to run the demo, just a web browser.
However, if you want to replicate data manipulation, modeling, and plot creation,
the main packages are included in CODE/requirements.txt:

1. Install Java 8 (required for H2O notebooks) and Conda
2. Run the below commands to install python requirements
```
conda create --name dvhope python==3.10
conda activate dvhope
pip install -r CODE/requirements.txt
```

# EXECUTION

The following steps run a webserver to view the html

1. Clone the repository and change the directory

```
git clone https://github.com/PaulEunKim/dvhope
cd dvhope
```

2. Run a local python server:

```
python -m http.server 8000
```

3. Open a browser and go to localhost:8000
4. Navigate to CODE/domestic and CODE/global.

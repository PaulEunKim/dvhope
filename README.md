# DV-HOPE
## <u>**D**</u>ata <u>**V**</u>isualization of <u>**H**</u>ealth <u>**O**</u>utcomes from Social and Environmental <u>**P**</u>r<u>**e**</u>dictors
<u>****</u>

# Description
DV-HOPE is a data visualization project aimed at exploring the relationships between environmental/socioeconomic factors and health outcomes. 

The main demonstration of this is a interactive choropleth map. You can visualize which states have worse predicted health outcomes through the color intensity of each state, and click on each state to explore which industry sectors are the top contributors to pollution.

Additionally, we include metrics on the model performance through Shapley Additive Explanations and other common metrics, which might give additional insight into the interplay of the predicted variables. To view the performance of the model the model, you can view the demo. To view all the machine learning experiments, check out the notebooks in CODE/model_evaluation. To view some exploratory data analysis, checkout CODE/eda.

# Installation

No installation is needed to run the demo. However, if you want to replicate data manipulation, modeling, and plot creation, the main packages are included in the requirements.txt.
```
conda create --name dvhope python==3.10
conda activate dvhope
pip install -r requirements.txt
```

There may be additional system requirements, such as having Java version 8 or newer installed in order to use H2O.

# Execution

After cloning the repository and changing the directory

```
git clone https://github.com/PaulEunKim/dvhope
cd dvhope
```

Run a local python server:

```
python -m http.server 8000
```

And then navigate to CODE/demo.
##


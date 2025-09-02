# 2D Monochalcogenide (2025)

### Bridging Text Mining and Quantum Simulations for the Design of 2D Monochalcogenide Materials

**Authors:** Mateus B. P. Querne, Marco Machado, Ronaldo Prati, Natan Moreira Regis, Matheus P. Lima, Juarez Da Silva  
**Status:** Submitted

---

## 📁 [Machine Learning Correlation Analysis](https://github.com/SabiM-UFSCar/projects/tree/1eb7f7bcce496b4b6e490bb2c309216b5dfd2ca0/2025-2D-Monochalcogenide/MachineLearningXAI)


### Contents

This folder contains the code and analysis related to Section 4 of the manuscript, "Bridging Text Mining and Quantum Simulations for the Design of 2D Monochalcogenide Materials.”,  and focuses on the machine learning portion of the study, where we analyze a comprehensive dataset of physicochemical properties to identify the most significant descriptors for material stability.

### About the Notebook:

The Jupyter notebook ML_correlation_analysis.ipynb performs a correlation analysis using a Random Forest model to predict energetic properties of 2D MQ compounds.

The key steps in the notebook are:
1. Data Loading: Imports the dataset of 34 system descriptors from System_Descriptors.xlsx.
2. Model Training: A RandomForestRegressor is trained to predict four key energetic properties:
 - Total energy
 - Relative energy
 - Formation enthalpy
 - Cohesive energy
3. Feature Importance Analysis: SHAP (SHapley Additive exPlanations) values are calculated to interpret the model's predictions and determine the importance of each physicochemical descriptor.
4. Visualization: The notebook generates several plots:
 - Joint plots comparing the DFT-calculated energies versus the ML-predicted energies.
 - Beeswarm plots to visualize the SHAP values and feature importance.

### Dependencies
To run the notebook, you will need the following Python libraries:
- pandas
- numpy
- matplotlib
- seaborn
- scikit-learn
- shap
- tqdm
- xgboost
- openpyxl (for reading .xlsx files)

You can install them using pip:
```
pip install pandas numpy matplotlib seaborn scikit-learn shap tqdm xgboost openpyxl
```

### Usage
Clone this repository to your local machine.
Ensure you have the required input file, System_Descriptors.xlsx, in the same directory as the notebook.
Open and run the ML_correlation_analysis.ipynb notebook in a Jupyter environment. The notebook will generate PDF files for the figures.

### Citation
If you use this code or the findings from our study in your research, please cite our manuscript:
M. B. P. Querne, M. A. M. T. Machado, R. C. Prati, N. M. Regis, M. P. Lima, and J. L. F. Da Silva, "Bridging Text Mining and Quantum Simulations for the Design of 2D Monochalcogenide Materials,"

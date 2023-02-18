import streamlit as st
import pandas as pd
from pulp import *
import matplotlib.pyplot as plt
import circlify
import random

st.title('The Restaurant Healthy Tool')
st.text('''
        McDonald's or other fast food isn't known for its healthy food, but I'm here to prove
        that it can be healthy!This tool uses linear programming to find 
        The best combination of food to hit your nutrition plan! Use the 
        left hand side to define constraints & watch your combo change 
        in the middle :)
        ''')

Data = pd.read_csv('Nutrition_Value_Dataset.csv')
Data = Data.dropna()
Data = Data.dropna(axis=1)


# Convert the item names to a list
MenuItems = Data.Product.tolist()
# Convert all of the macro nutrients fields to be dictionaries of the item names
Calories = Data.set_index('Product')['Energy (kCal)'].to_dict()
TotalFat = Data.set_index('Product')['Total Fat (g)'].to_dict()
SaturatedFat = Data.set_index('Product')['Saturated Fat (g)'].to_dict()
Carbohydrates = Data.set_index('Product')['Carbohydrates (g)'].to_dict()
Sugars = Data.set_index('Product')['Sugar (g)'].to_dict()
Protein = Data.set_index('Product')['Protein (g)'].to_dict()
Sodium = Data.set_index('Product')['Sodium (mg)'].to_dict()
Fiber = Data.set_index('Product')['Fiber (g)'].to_dict()

prob = LpProblem("McOptimization Problem", LpMinimize)

MenuItems_vars = LpVariable.dicts("MenuItems",MenuItems,lowBound=0,
   upBound=15,cat='Integer')



st.sidebar.write('Limits for Combo')
TotalFat_val = st.sidebar.number_input('Total Fat Max', value=70)
SatFat_val = st.sidebar.number_input('Saturated Fat Max', value=20)

SugarMin = st.sidebar.number_input('Suguar Min', value=80)
SugarMax = st.sidebar.number_input('Sugar Max', value=100)

CarbsMin = st.sidebar.number_input('Carbohydrates Min', value=260)

ProtienMin = st.sidebar.number_input('Protien Min', value=45)
ProtienMax = st.sidebar.number_input('Protien Max', value=85)

SodiumMax = st.sidebar.number_input('Sodium Max', value=10)




# First entry is the calorie calculation (this is our objective)
prob += lpSum([Calories[i]*MenuItems_vars[i] for i in MenuItems]), "Calories"
# Total Fat must be <= 70 g
prob += lpSum([TotalFat[i]*MenuItems_vars[i] for i in MenuItems]) <= TotalFat_val, "TotalFat"
# Saturated Fat is <= 20 g
prob += lpSum([SaturatedFat[i]*MenuItems_vars[i] for i in MenuItems]) <= SatFat_val, "Saturated Fat"
# Carbohydrates must be more than 260 g
prob += lpSum([Carbohydrates[i]*MenuItems_vars[i] for i in MenuItems]) >= CarbsMin, "Carbohydrates_lower"
# Sugar between 80-100 g
prob += lpSum([Sugars[i]*MenuItems_vars[i] for i in MenuItems]) >= SugarMin, "Sugars_lower"
prob += lpSum([Sugars[i]*MenuItems_vars[i] for i in MenuItems]) <= SugarMax, "Sugars_upper"
# Protein between 45-55g
prob += lpSum([Protein[i]*MenuItems_vars[i] for i in MenuItems]) >= ProtienMin, "Protein_lower"
prob += lpSum([Protein[i]*MenuItems_vars[i] for i in MenuItems]) <= ProtienMax, "Protein_upper"
# Sodium <= 6000 mg
prob += lpSum([Sodium[i]*MenuItems_vars[i] for i in MenuItems]) <= SodiumMax*1000, "Sodium"
   
   
prob.solve()


# Loop over the constraint set and get the final solution
results = {}

for constraint in prob.constraints:
    s = 0
    for var, coefficient in prob.constraints[constraint].items():
        s += var.varValue * coefficient
    results[prob.constraints[constraint].name.replace('_lower','')
        .replace('_upper','')] = s
    
    
objective_function_value = value(prob.objective)

varsdict = {}
for v in prob.variables():
    if v.varValue > 0:
        varsdict[v.name] = v.varValue
df_results = pd.DataFrame([varsdict])

        
st.header('Total Calories: ' + str(objective_function_value))



# Create just a figure and only one subplot
fig, ax = plt.subplots(figsize=(15,10))

# Title
ax.set_title('Request')

# Remove axes
ax.axis('off')

circles = circlify.circlify(
    varsdict.values(), 
    show_enclosure=False, 
    target_enclosure=circlify.Circle(x=0, y=0, r=1)
)

# Find axis boundaries
lim = max(
    max(
        abs(circle.x) + circle.r,
        abs(circle.y) + circle.r,
    )
    for circle in circles
)
plt.xlim(-lim, lim)
plt.ylim(-lim, lim)

# list of labels
labels = [i[10:] for i in varsdict.keys()]



# print circles
for circle, label in zip(circles, labels):
    x, y, r = circle
    ax.add_patch(plt.Circle((x, y), r*0.7, alpha=0.9, linewidth=2, facecolor="#%06x" % random.randint(0, 0xFFFFFF), edgecolor="black"))
    plt.annotate(label, (x,y ) ,va='center', ha='center', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round', pad=.5))
    value = circle.ex['datum']
    plt.annotate(value, (x,y-.1 ) ,va='center', ha='center', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round', pad=.5))


st.pyplot(fig)

st.subheader('Created by Luigi Mattera')
st.text('Part of his 30 Data Science Proejcts in 30 Days')
st.caption('Get the code [here](https://github.com/Luigimattera/30-Data-Science-Projects-in-30-Days)')
st.caption('Inspiration from [Kyle Pastor](https://towardsdatascience.com/making-mcdonalds-healthy-197f537f931d)')



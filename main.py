import pandas as pd

def clean_ms_forms_single(df, column_name, allowed_values):
    """
    Cleans an MS Forms single-choice column. Keeps the row if any of the
    allowed values are found as a substring within the column's text;
    otherwise, filters out the row.
    """
    def find_allowed_substring(val):
        # Handle potential NaN/null values in the original data
        if pd.isna(val):
            return None
       
        # Ensure we are checking against a string
        val_str = str(val)
       
        # Check if any allowed value exists as a substring
        for allowed in allowed_values:
            if allowed in val_str:
                return val  # Keep the original value (or return 'allowed' if you want to normalize it)
        return None

def clean_ms_forms_single_multiplexed(df, column_name, allowed_values_map):
    """
    Cleans an MS Forms single-choice column. Keeps the row if any of the keys 
    in allowed_values_map are found as a substring. Normalizes the value to the
    corresponding dictionary value.
    """
    def find_allowed_substring(val):
        if pd.isna(val):
            return None
        
        val_str = str(val)
        
        # Check if any key exists as a substring
        for substring, normalized_value in allowed_values_map.items():
            if substring in val_str:
                return normalized_value  # Returns the multiplexed/normalized value
        return None

    # 1. Apply the substring check and normalize the data
    df[column_name] = df[column_name].apply(find_allowed_substring)
    
    # 2. Drop rows where no match was found and reset index
    df = df[df[column_name].notnull()].reset_index(drop=True)
    
    return df

def years_experience(x: str):
    x_clean = x.strip()
    years_map = {
        "3 years or less": "<3 Yrs",
        "4-8 years": "4-8 Yrs",
        "8-12 years": "8-12 Yrs",
        "13 years or more": ">13 Yrs"
    }
    return years_map.get(x_clean, x_clean)

def subject_process(df):
    # Mapping dictionary: 
    # "Substrings to find" : "What it should be changed to"
    subject_map = {
        "Math": "Math",
        "Science": "Science",
        "Social": "Social",
        "Language": "Language",
        "English": "English",
        "ADST": "ADST",
        "Art": "Art",
        "ELL": "Language",  # Multiplexed
        "LSS": "Language"   # Multiplexed
    }
    
    # Note: Make sure to pass your actual column name instead of ""
    return clean_ms_forms_single_multiplexed(df, "subject", subject_map)
def grade(x:str):
    return int(x.strip().strip("Grade ")) # (int 8-12)

def view(x:str):
    return ["Against it",
    "Neutral",
    "In favour"].index(x)-1

def often(x:str):
    return ([
    "Rarely",
    "Sometimes",
    "Often",
    ].index(x.strip()))-1


def easy(x:str):
    return ([
    "Extremely difficult",
    "Somewhat difficult",
    "Neither easy nor difficult",
    "Somewhat easy",
    "Extremely easy"
    ].index(x.strip()))-2



df_student = pd.read_excel('mobilestudentold.xlsx', engine='openpyxl', converters={
    'grade': grade,
    'initv': view,
    'currv': view,
    })

df_teacher = pd.read_excel('mobileteacherold.xlsx', engine='openpyxl', converters={
    # 'grade': grade,
    'initv': view,
    'currv': view,
    'often': often,
    'easy': easy,
    'years':years_experience
    })

df_student = subject_process(df_student)
df_teacher = subject_process(df_teacher)

student_questions = {
    "grade": "What is your current grade?",
    "signif": "The new cell phone policy in the province does not allow students to use their phones in class at all unless the teacher says that they can. How significant to the school system was this new polic...",
    "change": "How much change have you witnessed with your in-school cell phone usage after the new cell phone policy?",
    "diff": "How much different is it in the classroom with this new cell phone policy?",
    "influ": "What kind of influence do you think the new cell phone policy has on our school?",
    "dominicS1": "Describe what you would use your cell phone for before the changes.",
    "prod": "How did the new policy affect your productivity in class?",
    "subject": "In which school subject areas have you seen the most change in after the new policy? (All inclusive, so ie. Math include precalculus)",
    "initv": "Initial view",
    "currv": "Current view",
    "support": "Do you support the new cell phone policy?",
    "source": "How did you find this survey?",
    "dominicS2": "Do you have any comments, suggestions or questions new cell phone policy?"
}

teacher_questions = {
    "years": "How many years of experience do you have teaching?",
    "signif": "The new cell phone policy in the province does not allow students to use their phones in class at all unless the teacher says that they can. How significant to the school system was this new polic...",
    "often": "How often do you notice the students in class comply with the new cell phone policy?",
    "easy": "How easy has the new cell phone policy been to enforce in your classes?",
    "diff": "How much different is it in the classroom with this new cell phone policy?",
    "influ": "What kind of influence do you think the new cell phone policy has on our school?",
    "prod": "How did the policy affect your productivity in your classes?",
    "subject": "In which school subject areas do you work in? (All inclusive, so ie. Math include precalculus)",
    "initv": "Initial view",
    "currv": "Current view",
    "support": "Do you support the new cell phone policy?",
    "dominicT": "Do you have any comments, suggestions, or questions about the new policy?",
}

# ALL COLUMNS IN BOTH TEACHER AND STUDENT THAT AARE NOT PROCESSED OR MENTIONED OUT SIDE THE QUESTION DICTIONARY THAT DO NOT START WITH DOMINIC ARE INTEGERS ON A SCALE FROM 0-10

years_val = {
"3 years or less",
"4-8 years",
"8-12 years",
"13 years or more"
}

source_val = {
    "Other people",
    "Online",
    "Posters",
}

print(df_student.index)
print(df_teacher.index)

import matplotlib.pyplot as plt
import seaborn as sns


# def plot_demographic_distribution(
#     df_student=None,
#     df_teacher=None,
#     column_to_plot=None,
#     split_students_by_grade=False,
#     split_teachers_by_experience=False,
#     save=None,
#     title=None,
# ):
#     """
#     Generates a grouped bar chart for a specified column, supporting student-only,
#     teacher-only, or combined student/teacher datasets with optional demographic splitting.
#     """
#     dfs_to_concat = []

#     # --- 1. Process Student Data if available and requested ---
#     if df_student is not None and column_to_plot in df_student.columns:
#         if split_students_by_grade and "grade" in df_student.columns:
#             # Group by Grade and target column, calculate percentages within each grade
#             s_counts = (
#                 df_student.groupby(["grade", column_to_plot])
#                 .size()
#                 .unstack(fill_value=0)
#             )
#             s_pct = s_counts.div(s_counts.sum(axis=1), axis=0) * 100
#             s_pct.index = [f"Grade {int(i)}" for i in s_pct.index]
#             dfs_to_concat.append(s_pct)
#         else:
#             # Clump all students together
#             s_counts = df_student.groupby(column_to_plot).size()
#             s_pct = (s_counts / s_counts.sum() * 100).to_frame().T
#             s_pct.index = ["All Students"]
#             dfs_to_concat.append(s_pct)

#     # --- 2. Process Teacher Data if available and requested ---
#     if df_teacher is not None and column_to_plot in df_teacher.columns:
#         if split_teachers_by_experience and "years" in df_teacher.columns:
#             # Group by Years of Experience and target column, calculate percentages within group
#             t_counts = (
#                 df_teacher.groupby(["years", column_to_plot])
#                 .size()
#                 .unstack(fill_value=0)
#             )
#             t_pct = t_counts.div(t_counts.sum(axis=1), axis=0) * 100
#             t_pct.index = [f"{i}" for i in t_pct.index]
#             dfs_to_concat.append(t_pct)
#         else:
#             # Clump all teachers together
#             t_counts = df_teacher.groupby(column_to_plot).size()
#             t_pct = (t_counts / t_counts.sum() * 100).to_frame().T
#             t_pct.index = ["All Teachers"]
#             dfs_to_concat.append(t_pct)

#     # --- 3. Combine DataFrames ---
#     if not dfs_to_concat:
#         print(f"Error: Column '{column_to_plot}' not found in provided data.")
#         return

#     df_plot = pd.concat(dfs_to_concat, axis=0).fillna(0)

#     # --- 4. Build Visual Asset ---
#     fig, ax = plt.subplots(figsize=(12, 6))

#     colors = plt.cm.tab10.colors
#     categories = df_plot.columns
#     groups = df_plot.index

#     num_groups = len(groups)
#     num_categories = len(categories)

#     width = 0.8 / num_categories
#     x = range(num_groups)

#     # Plot grouped bars
#     for i, category in enumerate(categories):
#         offset = (i - num_categories / 2) * width + width / 2
#         ax.bar(
#             [pos + offset for pos in x],
#             df_plot[category],
#             width,
#             label=str(category),
#             color=colors[i % len(colors)],
#         )

#     # Styling Configuration
#     chart_title = title if title else f"Distribution of '{column_to_plot}'"
#     ax.set_title(chart_title, fontsize=14, fontweight="bold", pad=15)
#     ax.set_xlabel("Grouping", fontsize=12, labelpad=10)
#     ax.set_ylabel("Proportion Percentage (%)", fontsize=12, labelpad=10)
#     ax.set_xticks(x)
#     ax.set_xticklabels(groups, rotation=15 if num_groups > 4 else 0)
#     ax.set_ylim(0, max(df_plot.values.max() + 5, 100))
#     ax.grid(axis="y", linestyle="--", alpha=0.7)
#     ax.set_axisbelow(True)

#     ax.legend(
#         title=column_to_plot.capitalize(),
#         bbox_to_anchor=(1.01, 1),
#         loc="upper left",
#     )

#     plt.tight_layout()
#     if save != None:
#         plt.savefig(f"./exports/{save}.png", dpi=300, bbox_inches="tight")
#     plt.show()

# plot_demographic_distribution(
#     df_student=df_student,
#     df_teacher=df_teacher,
#     column_to_plot="subject",
#     split_students_by_grade=False,
#     split_teachers_by_experience=False,
#     title="Subject Grouping",
#     save="subject_teacher_squish_student_squish",
# )
# plot_demographic_distribution(
#     df_student=df_student,
#     df_teacher=df_teacher,
#     column_to_plot="subject",
#     split_students_by_grade=True,
#     split_teachers_by_experience=True,
#     title="Subject Grouping",
#     save="subject_teacher_ind_student_ind",
# )
# plot_demographic_distribution(
#     df_student=df_student,
#     df_teacher=df_teacher,
#     column_to_plot="subject",
#     split_students_by_grade=False,
#     split_teachers_by_experience=True,
#     title="Subject Grouping",
#     save="subject_teacher_ind_student_squish",
# )
# plot_demographic_distribution(
#     df_student=df_student,
#     df_teacher=df_teacher,
#     column_to_plot="subject",
#     split_students_by_grade=True,
#     split_teachers_by_experience=False,
#     title="Subject Grouping",
#     save="subject_teacher_squish_student_ind",
# )


import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set global seaborn styling for better aesthetics
sns.set_theme(style="whitegrid", palette="Set2")

# Create a combined dataframe for shared metrics
df_student['Role'] = 'Student'
df_teacher['Role'] = 'Teacher'

# Extract only columns that are identical in meaning between both datasets
common_cols = ['signif', 'diff', 'influ', 'prod', 'subject', 'initv', 'currv', 'support', 'Role']
df_combined = pd.concat([
    df_student[[c for c in common_cols if c in df_student.columns]], 
    df_teacher[[c for c in common_cols if c in df_teacher.columns]]
], ignore_index=True)



#--------------------------------------------------------------------------------------------------------------------------



# Melt dataframe to stack all 0-10 metrics into a single column for a grouped boxplot
metrics_0_10 = ['signif', 'diff', 'influ', 'prod', 'support']
df_melted = df_combined.melt(id_vars=['Role'], value_vars=metrics_0_10, 
                             var_name='Metric', value_name='Score')

plt.figure(figsize=(12, 6))
sns.boxplot(data=df_melted, x='Metric', y='Score', hue='Role', palette='Set1')
plt.title('Student vs Teacher: Distributions of Common 0-10 Metrics', fontsize=14, fontweight='bold')
plt.ylabel('Score (0-10)')
plt.xlabel('Metric')
plt.legend(title='Role')
plt.tight_layout()
plt.show()





plt.figure(figsize=(10, 5))
sns.kdeplot(data=df_combined, x="support", hue="Role", fill=True, 
            common_norm=False, palette="crest", alpha=0.5, linewidth=2)
plt.title('Density Distribution of Policy Support (0-10)', fontsize=14, fontweight='bold')
plt.xlabel('Support Level')
plt.ylabel('Density')
plt.xlim(0, 10)
plt.show()



plt.figure(figsize=(12, 6))
sns.barplot(data=df_combined, x='subject', y='prod', hue='Role', 
            errorbar=('ci', 95), capsize=0.1, palette='magma')
plt.title('Average Productivity Impact by Subject Area', fontsize=14, fontweight='bold')
plt.xlabel('Subject')
plt.ylabel('Average Productivity Score (0-10)')
plt.legend(title='Role', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()





# Melt initial and current views
df_views = df_combined.melt(id_vars=['Role'], value_vars=['initv', 'currv'], 
                            var_name='Time', value_name='Viewpoint')

plt.figure(figsize=(8, 6))
sns.pointplot(data=df_views, x='Time', y='Viewpoint', hue='Role', 
              markers=["o", "s"], linestyles=["-", "--"], palette='Dark2')
plt.title('Shift in Viewpoint: Initial vs. Current', fontsize=14, fontweight='bold')
plt.xlabel('Time (initv = Initial, currv = Current)')
plt.ylabel('Average Viewpoint (-1: Against, 0: Neutral, 1: In Favour)')
plt.ylim(-1.1, 1.1)
plt.show()





plt.figure(figsize=(10, 6))
sns.lmplot(data=df_combined, x='influ', y='prod', hue='Role', 
           scatter_kws={'alpha':0.4}, height=6, aspect=1.5, palette='Set1')
plt.title('Correlation: Influence of Policy vs Productivity Impact', fontsize=14, fontweight='bold')
plt.xlabel('Influence on School (0-10)')
plt.ylabel('Productivity Score (0-10)')
plt.xlim(0, 10)
plt.ylim(0, 10)
plt.show()






student_num = df_student.select_dtypes(include=[np.number])

plt.figure(figsize=(10, 8))
sns.heatmap(student_num.corr(), annot=True, cmap='coolwarm', fmt=".2f", 
            linewidths=0.5, vmin=-1, vmax=1)
plt.title('Student Responses: Correlation Heatmap', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()






teacher_num = df_teacher.select_dtypes(include=[np.number])

plt.figure(figsize=(10, 8))
sns.heatmap(teacher_num.corr(), annot=True, cmap='coolwarm', fmt=".2f", 
            linewidths=0.5, vmin=-1, vmax=1)
plt.title('Teacher Responses: Correlation Heatmap', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()







plt.figure(figsize=(10, 6))
experience_order = ["<3 Yrs", "4-8 Yrs", "8-12 Yrs", ">13 Yrs"]
sns.violinplot(data=df_teacher, x='years', y='easy', order=experience_order, 
               palette='mako', inner="quartile")
plt.title('Ease of Enforcement across Years of Experience', fontsize=14, fontweight='bold')
plt.xlabel('Years of Experience')
plt.ylabel('Ease of Enforcement (-2 to 2)')
plt.tight_layout()
plt.show()









plt.figure(figsize=(10, 6))
sns.boxplot(data=df_student, x='grade', y='change', palette='pastel')
sns.stripplot(data=df_student, x='grade', y='change', color=".3", size=4, alpha=0.5)
plt.title('Witnessed Change (0-10) Distributed by Grade', fontsize=14, fontweight='bold')
plt.xlabel('Grade Level')
plt.ylabel('Perceived Change (0-10)')
plt.show()

#9done


plt.figure(figsize=(10, 6))
sns.countplot(data=df_student, x='grade', hue='source', palette='Set3', edgecolor='black')
plt.title('Information Source by Student Grade', fontsize=14, fontweight='bold')
plt.xlabel('Grade Level')
plt.ylabel('Count of Students')
plt.legend(title='Source', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

source_counts = df_student['source'].value_counts()

# 2. Plot the pie chart using pandas built-in plotting (which uses matplotlib)
source_counts.plot(
    kind='pie', 
    autopct='%1.1f%%', 
    startangle=140, 
    cmap='Set3', 
    wedgeprops={'edgecolor': 'black'}
)

# 3. Customize the chart aesthetics
plt.title('Distribution of Information Sources', fontsize=14, fontweight='bold')
plt.ylabel('')  # Hides the default 'source' column label on the y-axis
plt.tight_layout()

# 4. Display the chart
plt.show()


plt.figure(figsize=(8, 6))
sns.boxplot(data=df_teacher, x='often', y='support', color='white', fliersize=0)
sns.swarmplot(data=df_teacher, x='often', y='support', palette='dark:b', size=6, alpha=0.7)
plt.title('Policy Support vs. Student Compliance Frequency', fontsize=14, fontweight='bold')
plt.xlabel('Compliance Frequency (-1: Rarely, 0: Sometimes, 1: Often)')
plt.ylabel('Support for Policy (0-10)')
plt.show()


# Create a crosstab mapping Initial View to Current View
student_transition = pd.crosstab(df_student['initv'], df_student['currv'])
student_transition.index = ['Against (-1)', 'Neutral (0)', 'In Favour (1)']
student_transition.columns = ['Against (-1)', 'Neutral (0)', 'In Favour (1)']

plt.figure(figsize=(7, 5))
sns.heatmap(student_transition, annot=True, fmt='g', cmap='Blues', linewidths=1)
plt.title('Student View Transition (Initial to Current)', fontsize=14, fontweight='bold')
plt.xlabel('Current View')
plt.ylabel('Initial View')
plt.show()


teacher_transition = pd.crosstab(df_teacher['initv'], df_teacher['currv'])
# Fill missing with np.nan so Seaborn renders the square as empty/blank background
teacher_transition = teacher_transition.reindex(index=[-1, 0, 1], columns=[-1, 0, 1], fill_value=np.nan)
teacher_transition.index = ['Against (-1)', 'Neutral (0)', 'In Favour (1)']
teacher_transition.columns = ['Against (-1)', 'Neutral (0)', 'In Favour (1)']

plt.figure(figsize=(7, 5))
sns.heatmap(teacher_transition, annot=True, fmt='g', cmap='Oranges', linewidths=1)
plt.title('Teacher View Transition (Initial to Current)', fontsize=14, fontweight='bold')
plt.xlabel('Current View')
plt.ylabel('Initial View')
plt.show()



plt.figure(figsize=(10, 6))
sns.barplot(data=df_teacher, x='easy', y='influ', palette='viridis', 
            errorbar=('ci', 95), capsize=0.1)
plt.title('Perceived Influence vs. Ease of Enforcement (Teachers)', fontsize=14, fontweight='bold')
plt.xlabel('Ease of Enforcement (-2: Extremely Difficult to 2: Extremely Easy)')
plt.ylabel('Average Influence Score (0-10)')
plt.show()



# Calculate percentages for stacked bars
subject_view_counts = df_student.groupby(['subject', 'currv']).size().unstack(fill_value=0)
subject_view_pct = subject_view_counts.div(subject_view_counts.sum(axis=1), axis=0) * 100

# Rename columns for clarity
subject_view_pct.columns = ['Against (-1)', 'Neutral (0)', 'In Favour (1)']

subject_view_pct.plot(kind='bar', stacked=True, figsize=(12, 6), color=['#ef476f', '#ffd166', '#06d6a0'])
plt.title('Student Current View Breakdown by Subject', fontsize=14, fontweight='bold')
plt.xlabel('Subject Area')
plt.ylabel('Percentage (%)')
plt.legend(title='Current View', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()



# Calculate percentages for stacked bars
subject_view_counts = df_teacher.groupby(['subject', 'currv']).size().unstack(fill_value=0)
subject_view_pct = subject_view_counts.div(subject_view_counts.sum(axis=1), axis=0) * 100

# Rename columns for clarity
subject_view_pct.columns = ['Neutral (0)', 'In Favour (1)'] # HUMAN ME VERY IMPORTANT AGAINST IS LITERALLY NOT THERE IN A SINLGE RESPONESE

subject_view_pct.plot(kind='bar', stacked=True, figsize=(12, 6), color=["#4d47ef", "#be7500"])
plt.title('Teacher Current View Breakdown by Subject', fontsize=14, fontweight='bold')
plt.xlabel('Subject Area')
plt.ylabel('Percentage (%)')
plt.legend(title='Current View', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
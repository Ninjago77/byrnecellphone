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

# I hereby define a dominicoA graph as a graphs in the form: one variable (if shared between both student and teacher student surveys) plotted as a bar graph across the variables of each individual grade, and one extra column for teachers, make sure that the other variable is calculated based on the percent of students/ teacher who selected that option in that variable
# I hereby define a dominicoB graph as a graphs in the form: one variable (if shared between both student and teacher student surveys) plotted as a bar graph across the variables of each individual grade, and extra columns for teachers of different experience groups, make sure that the other variable is calculated based on the percent of students/ teacher who selected that option in that variable


# 1. Normalize and transform Student data into within-grade percentages
student_counts = df_student.groupby(['grade', 'subject']).size().unstack(fill_value=0)
student_pct = student_counts.div(student_counts.sum(axis=1), axis=0) * 100
# Reformat row index names for clear chart presentation
student_pct.index = [f"Grade {int(i)}" for i in student_pct.index]

# # 2. Normalize and transform Teacher data into a relative matching row
# teacher_counts = df_teacher.groupby('subject').size()
# teacher_pct = (teacher_counts / teacher_counts.sum() * 100).to_frame().T
# teacher_pct.index = ['Teachers']

teacher_counts = df_teacher.groupby(['years', 'subject']).size().unstack(fill_value=0)
teacher_pct = teacher_counts.div(teacher_counts.sum(axis=1), axis=0) * 100
# Reformat row index names for clear chart presentation
teacher_pct.index = [f"{i}" for i in teacher_pct.index]

df_dominico = pd.concat([student_pct, teacher_pct], axis=0).fillna(0)

# 4. Build visual assets using pure Matplotlib
fig, ax = plt.subplots(figsize=(12, 6))

# Define colors for the subjects to match a muted theme
colors = plt.cm.tab10.colors
subjects = df_dominico.columns
groups = df_dominico.index

num_groups = len(groups)
num_subjects = len(subjects)

# Calculate bar widths and positions
width = 0.8 / num_subjects
x = range(num_groups)

# Plot grouped bars
for i, subject in enumerate(subjects):
    offset = (i - num_subjects / 2) * width + width / 2
    ax.bar([pos + offset for pos in x], df_dominico[subject], width, label=subject, color=colors[i % len(colors)])

# Custom plot styling configuration
ax.set_title('Subject Distribution', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Student / Teacher Grouping', fontsize=12, labelpad=10)
ax.set_ylabel('Proportion Percentage (%)', fontsize=12, labelpad=10)
ax.set_xticks(x)
ax.set_xticklabels(groups)
ax.set_ylim(0, df_dominico.values.max() + 5)
ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.set_axisbelow(True)

ax.legend(title='Subject Matrix', bbox_to_anchor=(1.01, 1), loc='upper left')

plt.tight_layout()
plt.show()
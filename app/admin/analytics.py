import pandas as pd
import os

def get_stroke_analytics():
    try:
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'healthcare-dataset-stroke-data.csv')
        df = pd.read_csv(csv_path)
        
        # Age groups
        df['age_group'] = pd.cut(df['age'], bins=[0, 18, 35, 50, 65, 100], 
                                  labels=['0-18', '19-35', '36-50', '51-65', '65+'])
        age_stats = df[df['stroke'] == 1].groupby('age_group', observed=True).size().to_dict()
        age_stats = {str(k): int(v) for k, v in age_stats.items()}
        
        # Gender stats
        gender_stats = df['gender'].value_counts().to_dict()
        gender_stats = {str(k): int(v) for k, v in gender_stats.items()}
        
        # Hypertension stats
        hypertension_stats = df['hypertension'].value_counts().to_dict()
        hypertension_stats = {str(k): int(v) for k, v in hypertension_stats.items()}
        
        # Heart disease stats
        heart_disease_stats = df['heart_disease'].value_counts().to_dict()
        heart_disease_stats = {str(k): int(v) for k, v in heart_disease_stats.items()}
        
        # Work Type vs Stroke
        work_type_stroke = df[df['stroke'] == 1]['work_type'].value_counts().to_dict()
        work_type_no_stroke = df[df['stroke'] == 0]['work_type'].value_counts().to_dict()
        
        all_work_types = list(set(list(work_type_stroke.keys()) + list(work_type_no_stroke.keys())))
        
        work_type_data = {
            'labels': all_work_types,
            'stroke': [int(work_type_stroke.get(label, 0)) for label in all_work_types],
            'no_stroke': [int(work_type_no_stroke.get(label, 0)) for label in all_work_types]
        }
        
        # BMI groups
        df['bmi_group'] = pd.cut(df['bmi'].dropna(), bins=[0, 18.5, 25, 30, 100],
                                 labels=['Underweight', 'Normal', 'Overweight', 'Obese'])
        bmi_stroke = df[df['stroke'] == 1]['bmi_group'].value_counts().to_dict()
        bmi_no_stroke = df[df['stroke'] == 0]['bmi_group'].value_counts().to_dict()
        
        bmi_labels = ['Underweight', 'Normal', 'Overweight', 'Obese']
        bmi_stroke_data = {
            'labels': bmi_labels,
            'stroke': [int(bmi_stroke.get(label, 0)) for label in bmi_labels],
            'no_stroke': [int(bmi_no_stroke.get(label, 0)) for label in bmi_labels]
        }
        
        # Glucose levels
        df['glucose_group'] = pd.cut(df['avg_glucose_level'], 
                                     bins=[0, 100, 125, 200, 300],
                                     labels=['Normal', 'Prediabetes', 'Diabetes', 'High'])
        glucose_stroke = df[df['stroke'] == 1].groupby('glucose_group', observed=True).size().to_dict()
        glucose_no_stroke = df[df['stroke'] == 0].groupby('glucose_group', observed=True).size().to_dict()
        
        glucose_labels = ['Normal', 'Prediabetes', 'Diabetes', 'High']
        glucose_stroke_data = {
            'labels': glucose_labels,
            'stroke': [int(glucose_stroke.get(label, 0)) for label in glucose_labels],
            'no_stroke': [int(glucose_no_stroke.get(label, 0)) for label in glucose_labels]
        }
        
        return {
            'total_records': int(len(df)),
            'stroke_cases': int(len(df[df['stroke'] == 1])),
            'gender_stats': gender_stats,
            'age_stats': age_stats,
            'hypertension_stats': hypertension_stats,
            'heart_disease_stats': heart_disease_stats,
            'work_type_data': work_type_data,
            'bmi_stroke_data': bmi_stroke_data,
            'glucose_stroke_data': glucose_stroke_data
        }
    except Exception as e:
        print(f"Error loading analytics: {str(e)}")
        return {
            'total_records': 0,
            'stroke_cases': 0,
            'gender_stats': {},
            'age_stats': {},
            'hypertension_stats': {},
            'heart_disease_stats': {},
            'work_type_data': {'labels': [], 'stroke': [], 'no_stroke': []},
            'bmi_stroke_data': {'labels': [], 'stroke': [], 'no_stroke': []},
            'glucose_stroke_data': {'labels': [], 'stroke': [], 'no_stroke': []}
        }
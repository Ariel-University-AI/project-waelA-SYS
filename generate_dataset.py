import pandas as pd
import numpy as np
import random

def generate_agricultural_dataset(num_rows=600):
    np.random.seed(42)
    random.seed(42)
    
    structure_types = ['חממה', 'בית אריזה', 'מחסן חקלאי', 'סככת טרקטורים', 'לול', 'רפת']
    regions = ['צפון', 'מרכז', 'דרום', 'שרון', 'ערבה']
    
    data = []
    
    for i in range(1, num_rows + 1):
        app_id = f"APP-2024-{i:04d}"
        struct = random.choice(structure_types)
        region = random.choice(regions)
        
        # Area in sq meters
        if struct in ['חממה', 'רפת']:
            area = np.random.randint(500, 5000)
        else:
            area = np.random.randint(50, 1000)
            
        dist_road = round(np.random.uniform(5.0, 100.0), 1)
        dist_neighbors = round(np.random.uniform(10.0, 500.0), 1)
        has_solar_panels = random.choice([True, False])
        
        # Rules logic for approval
        status_prob = 1.0
        
        # Rule 1: High distance from road is good
        if dist_road < 10.0:
            status_prob -= 0.4
            
        # Rule 2: distance from neighbors
        if struct in ['לול', 'רפת'] and dist_neighbors < 100.0:
            status_prob -= 0.8  # Odor/noise problem
            
        if area > 3000:
            status_prob -= 0.2  # Requires more permits
            
        # Determine status
        is_approved = random.random() < status_prob
        
        if is_approved:
            status = 'מאושר'
        else:
            if status_prob < 0.2:
                status = 'נדחה'
            else:
                status = 'דרוש תיקון'
                
        data.append({
            'מזהה_בקשה': app_id,
            'סוג_מבנה': struct,
            'אזור': region,
            'שטח_מטר_רבוע': area,
            'מרחק_מכביש_ראשי_מטר': dist_road,
            'מרחק_ממגורים_מטר': dist_neighbors,
            'כולל_פנלים_סולאריים': has_solar_panels,
            'סטטוס_אישור': status
        })
        
    df = pd.DataFrame(data)
    df.to_csv("agricultural_permits_dataset.csv", index=False, encoding='utf-8-sig')
    print("Dataset created successfully with", num_rows, "rows.")

if __name__ == "__main__":
    generate_agricultural_dataset()

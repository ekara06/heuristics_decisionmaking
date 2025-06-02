import pandas as pd
import numpy as np

# CSV 
df_direction = pd.read_csv("qwen_direction.csv")
df_direction['condition'] = 'direction'

df_ranking = pd.read_csv("qwen_ranking.csv")
df_ranking['condition'] = 'ranking'

df_unknown = pd.read_csv("qwen_unknown.csv")
df_unknown['condition'] = 'unknown'

#stack these three dataframes
df = pd.concat([df_direction, df_ranking, df_unknown], ignore_index=True)

print(df)

# Sonuçları saklayacağımız liste
results = []

# Grouped by Feature 3 name and calculate correlations
for feature1, feature2, feature3, condition in df[['Feature 1 name', 'Feature 2 name', 'Feature 3 name', 'condition']].drop_duplicates().itertuples(index=False, name=None):
    subset = df[(df['Feature 1 name'] == feature1) & (df['Feature 2 name'] == feature2) & (df['Feature 3 name'] == feature3) & (df['condition'] == condition)]

    print(len(subset))
    if len(subset) == 10:
    
        # Combined feature values
        combined_feature1 = np.concatenate([subset['Object 1 Feature 1 value'].values, 
                                        subset['Object 2 Feature 1 value'].values])
        
        combined_feature2 = np.concatenate([subset['Object 1 Feature 2 value'].values, 
                                        subset['Object 2 Feature 2 value'].values])
        
        combined_feature3 = np.concatenate([subset['Object 1 Feature 3 value'].values, 
                                        subset['Object 2 Feature 3 value'].values])
        
        # Calculate correlations
        corr_1_3 = np.corrcoef(combined_feature1, combined_feature3)[0,1]
        corr_2_3 = np.corrcoef(combined_feature2, combined_feature3)[0,1]
        
        # Sonuçları listeye ekle
        results.append({
            'Feature_3 name': feature3,
            'corr_1_3': corr_1_3,
            'corr_2_3': corr_2_3
        })

# Sonuçları DataFrame'e çevir
result_df = pd.DataFrame(results)
result_df = result_df.round(2)

# CSV olarak kaydet
result_df.to_csv("combined_correlations.csv", index=False)


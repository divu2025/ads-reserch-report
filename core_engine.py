import pandas as pd
import numpy as np

class KeywordEngine:
    def __init__(self, cost_threshold=50.0):
        self.cost_threshold = cost_threshold

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize search terms and handle missing values."""
        # Normalize: lowercase, remove special characters
        df['search_term'] = df['search_term'].str.lower().str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
        
        # Fill missing values
        df['cost'] = df['cost'].fillna(0)
        df['clicks'] = df['clicks'].fillna(0)
        df['conversions'] = df['conversions'].fillna(0)
        
        return df

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate metrics like CPC and Conversion Rate."""
        df['cpc'] = df['cost'] / df['clicks'].replace(0, 1) # Avoid division by zero
        df['conversion_rate'] = (df['conversions'] / df['clicks'].replace(0, 1)) * 100
        
        # Rounding
        df['cpc'] = df['cpc'].round(2)
        df['conversion_rate'] = df['conversion_rate'].round(2)
        
        return df

    def apply_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply core decision rules based on metrics."""
        # Rule 1: High Spend, Zero Conversion
        df['decision'] = 'KEEP'
        df['reason'] = 'Pending AI Review'
        
        mask_waste = (df['cost'] > self.cost_threshold) & (df['conversions'] == 0)
        df.loc[mask_waste, 'decision'] = 'NEGATIVE'
        df.loc[mask_waste, 'reason'] = f'Waste: Cost > ${self.cost_threshold} with 0 conversions'
        
        # Rule 3: High Conversion Rate -> SCALE
        mask_scale = (df['conversion_rate'] > 5.0) & (df['conversions'] > 0)
        df.loc[mask_scale, 'decision'] = 'KEEP'
        df.loc[mask_scale, 'reason'] = 'Potential: High conversion rate'
        
        return df

    def calculate_scores(self, df: pd.DataFrame) -> dict:
        """Calculate efficiency and waste scores."""
        total_spend = df['cost'].sum()
        waste_spend = df[df['decision'] == 'NEGATIVE']['cost'].sum()
        
        total_terms = len(df)
        converting_terms = len(df[df['conversions'] > 0])
        
        efficiency_score = (converting_terms / total_terms * 100) if total_terms > 0 else 0
        waste_score = (waste_spend / total_spend * 100) if total_spend > 0 else 0
        
        return {
            "total_spend": float(total_spend),
            "waste_spend": float(waste_spend),
            "efficiency_score": float(efficiency_score),
            "waste_score": float(waste_score)
        }

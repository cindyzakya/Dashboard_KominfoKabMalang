"""
Analysis functions for dashboard insights
"""

import pandas as pd
import numpy as np
from scipy import stats

def analyze_trend(data, value_col, period_col):
    """Analyze trend in time series data"""
    if len(data) < 2:
        return "Data tidak cukup untuk analisis tren."
    
    data_sorted = data.sort_values(period_col)
    
    # Calculate trend using linear regression
    x = np.arange(len(data_sorted))
    y = data_sorted[value_col].values
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    # Determine trend direction
    if abs(slope) < 0.01:
        trend_direction = "stabil"
    elif slope > 0:
        trend_direction = "meningkat"
    else:
        trend_direction = "menurun"
    
    # Calculate percentage change
    first_value = data_sorted.iloc[0][value_col]
    last_value = data_sorted.iloc[-1][value_col]
    pct_change = ((last_value - first_value) / first_value) * 100 if first_value != 0 else 0
    
    return {
        'trend_direction': trend_direction,
        'slope': slope,
        'r_squared': r_value**2,
        'p_value': p_value,
        'percentage_change': pct_change,
        'first_value': first_value,
        'last_value': last_value
    }

def analyze_correlation(df, col1, col2):
    """Analyze correlation between two columns"""
    correlation = df[col1].corr(df[col2])
    
    if abs(correlation) > 0.7:
        strength = "sangat kuat"
    elif abs(correlation) > 0.5:
        strength = "kuat"
    elif abs(correlation) > 0.3:
        strength = "sedang"
    else:
        strength = "lemah"
    
    direction = "positif" if correlation > 0 else "negatif"
    
    return {
        'correlation': correlation,
        'strength': strength,
        'direction': direction,
        'interpretation': f"Korelasi {direction} {strength} ({correlation:.3f})"
    }

def analyze_distribution(data, value_col):
    """Analyze distribution of values"""
    values = data[value_col].dropna()
    
    analysis = {
        'mean': values.mean(),
        'median': values.median(),
        'std': values.std(),
        'min': values.min(),
        'max': values.max(),
        'q25': values.quantile(0.25),
        'q75': values.quantile(0.75),
        'skewness': stats.skew(values),
        'kurtosis': stats.kurtosis(values)
    }
    
    # Determine distribution shape
    if abs(analysis['skewness']) < 0.5:
        shape = "normal"
    elif analysis['skewness'] > 0.5:
        shape = "condong kanan"
    else:
        shape = "condong kiri"
    
    analysis['shape'] = shape
    
    return analysis

def analyze_outliers(data, value_col, method='iqr'):
    """Detect outliers in data"""
    values = data[value_col].dropna()
    
    if method == 'iqr':
        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = values[(values < lower_bound) | (values > upper_bound)]
    
    elif method == 'zscore':
        z_scores = np.abs(stats.zscore(values))
        outliers = values[z_scores > 3]
    
    return {
        'outliers': outliers.tolist(),
        'outlier_count': len(outliers),
        'outlier_percentage': (len(outliers) / len(values)) * 100,
        'lower_bound': lower_bound if method == 'iqr' else None,
        'upper_bound': upper_bound if method == 'iqr' else None
    }

def analyze_top_bottom_performers(data, value_col, entity_col, top_n=5):
    """Analyze top and bottom performers"""
    sorted_data = data.sort_values(value_col, ascending=False)
    
    top_performers = sorted_data.head(top_n)
    bottom_performers = sorted_data.tail(top_n)
    
    analysis = {
        'top_performers': top_performers[[entity_col, value_col]].to_dict('records'),
        'bottom_performers': bottom_performers[[entity_col, value_col]].to_dict('records'),
        'best_value': sorted_data.iloc[0][value_col],
        'worst_value': sorted_data.iloc[-1][value_col],
        'best_entity': sorted_data.iloc[0][entity_col],
        'worst_entity': sorted_data.iloc[-1][entity_col]
    }
    
    return analysis

def analyze_seasonal_patterns(data, value_col, period_col='Bulan'):
    """Analyze seasonal patterns in data"""
    if period_col not in data.columns:
        return "Kolom periode tidak ditemukan untuk analisis seasonal."
    
    seasonal_data = data.groupby(period_col)[value_col].mean().reset_index()
    
    # Find peak and low seasons
    peak_season = seasonal_data.loc[seasonal_data[value_col].idxmax(), period_col]
    low_season = seasonal_data.loc[seasonal_data[value_col].idxmin(), period_col]
    
    peak_value = seasonal_data[value_col].max()
    low_value = seasonal_data[value_col].min()
    
    seasonal_variation = ((peak_value - low_value) / low_value) * 100 if low_value != 0 else 0
    
    return {
        'peak_season': peak_season,
        'low_season': low_season,
        'peak_value': peak_value,
        'low_value': low_value,
        'seasonal_variation': seasonal_variation,
        'seasonal_data': seasonal_data
    }

def generate_insights(data, analysis_type='general'):
    """Generate automated insights based on data analysis"""
    insights = []
    
    if analysis_type == 'trend':
        # Add trend-specific insights
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols[:3]:  # Analyze top 3 numeric columns
            if len(data) > 1:
                trend_analysis = analyze_trend(data, col, data.columns[0])
                if trend_analysis['trend_direction'] != 'stabil':
                    insights.append(f"Tren {col} menunjukkan pola {trend_analysis['trend_direction']} dengan perubahan {trend_analysis['percentage_change']:.1f}%")
    
    elif analysis_type == 'distribution':
        # Add distribution insights
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols[:2]:
            dist_analysis = analyze_distribution(data, col)
            insights.append(f"Distribusi {col} memiliki bentuk {dist_analysis['shape']} dengan rata-rata {dist_analysis['mean']:.2f}")
    
    return insights

def create_summary_statistics(data, group_col=None):
    """Create summary statistics for data"""
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    
    if group_col and group_col in data.columns:
        summary = data.groupby(group_col)[numeric_cols].agg(['mean', 'sum', 'count', 'std']).round(2)
    else:
        summary = data[numeric_cols].describe().round(2)
    
    return summary
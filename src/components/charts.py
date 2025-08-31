"""
Chart components for dashboard visualization
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_line_chart(data, x_col, y_col, color_col=None, title="Line Chart"):
    """Create line chart with plotly"""
    fig = px.line(
        data, 
        x=x_col, 
        y=y_col, 
        color=color_col,
        title=title,
        markers=True
    )
    fig.update_layout(height=400)
    return fig

def create_bar_chart(data, x_col, y_col, color_col=None, title="Bar Chart", orientation='v'):
    """Create bar chart with plotly"""
    fig = px.bar(
        data,
        x=x_col if orientation == 'v' else y_col,
        y=y_col if orientation == 'v' else x_col,
        color=color_col,
        title=title,
        orientation='h' if orientation == 'h' else 'v'
    )
    fig.update_layout(height=400)
    return fig

def create_pie_chart(data, values_col, names_col, title="Pie Chart"):
    """Create pie chart with plotly"""
    fig = px.pie(
        data,
        values=values_col,
        names=names_col,
        title=title
    )
    fig.update_layout(height=400)
    return fig

def create_scatter_plot(data, x_col, y_col, color_col=None, title="Scatter Plot"):
    """Create scatter plot with plotly"""
    fig = px.scatter(
        data,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title
    )
    fig.update_layout(height=400)
    return fig

def create_heatmap(data, x_col, y_col, z_col, title="Heatmap"):
    """Create heatmap with plotly"""
    pivot_data = data.pivot(index=y_col, columns=x_col, values=z_col)
    
    fig = px.imshow(
        pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        title=title,
        aspect='auto'
    )
    fig.update_layout(height=400)
    return fig

def create_combo_chart(data, x_col, y1_col, y2_col, title="Combo Chart"):
    """Create combination chart with bar and line"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=data[x_col],
        y=data[y1_col],
        name=y1_col,
        yaxis='y'
    ))
    
    fig.add_trace(go.Scatter(
        x=data[x_col],
        y=data[y2_col],
        mode='lines+markers',
        name=y2_col,
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=title,
        yaxis=dict(title=y1_col, side='left'),
        yaxis2=dict(title=y2_col, side='right', overlaying='y'),
        height=400
    )
    
    return fig

def create_area_chart(data, x_col, y_col, color_col=None, title="Area Chart"):
    """Create area chart with plotly"""
    fig = px.area(
        data,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title
    )
    fig.update_layout(height=400)
    return fig
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os
import io
import base64

# Set paths
CSV_FILE = os.path.join(os.path.dirname(__file__), "file.csv")

def get_medicine_data():
    """Load and clean medicine data using Pandas."""
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame()
    
    df = pd.read_csv(CSV_FILE)
    
    # Clean MRP column: "Rs. 1,644.15" -> 1644.15
    def clean_mrp(val):
        if pd.isna(val): return 0.0
        try:
            # Remove "Rs.", commas, and whitespace
            cleaned = str(val).replace('Rs.', '').replace(',', '').strip()
            return float(cleaned)
        except:
            return 0.0

    df['MRP_Cleaned'] = df['MRP'].apply(clean_mrp)
    return df

def generate_price_distribution_plot():
    """Generate a distribution plot using Seaborn and Matplotlib."""
    df = get_medicine_data()
    if df.empty:
        return None
    
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    
    # Plot top 10 companies by average price
    top_companies = df.groupby('Company Name')['MRP_Cleaned'].mean().sort_values(ascending=False).head(10)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(x=top_companies.values, y=top_companies.index, palette="viridis")
    plt.title('Top 10 Pharmaceutical Companies by Average Medicine Price')
    plt.xlabel('Average Price (Rs.)')
    plt.ylabel('Company Name')
    plt.tight_layout()
    
    # Save to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def perform_medicine_clustering():
    """Use Scikit-learn to cluster medicines based on price (Demonstration)."""
    df = get_medicine_data()
    if df.empty or len(df) < 5:
        return []
    
    # Prepare data for clustering (Price)
    X = df[['MRP_Cleaned']].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Apply KMeans
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['Cluster'] = kmeans.fit_predict(X_scaled)
    
    # Map clusters to labels
    cluster_map = {0: 'Budget', 1: 'Mid-Range', 2: 'Premium'}
    # Re-order based on actual price means to ensure labels are correct
    means = df.groupby('Cluster')['MRP_Cleaned'].mean().sort_values().index
    correct_map = {means[0]: 'Budget', means[1]: 'Mid-Range', means[2]: 'Premium'}
    
    df['Category'] = df['Cluster'].map(correct_map)
    
    return df[['Brand Name', 'Company Name', 'MRP_Cleaned', 'Category']].head(20).to_dict(orient='records')

def get_interactive_chart_data():
    """Generate interactive chart data using Plotly."""
    df = get_medicine_data()
    if df.empty:
        return {}
    
    # Price by Company
    fig = px.box(df.head(100), x="Company Name", y="MRP_Cleaned", 
                 title="Medicine Price Range by company (Sample)",
                 labels={"MRP_Cleaned": "Price (Rs.)", "Company Name": "Company"})
    
    return fig.to_json()

def get_market_statistics():
    """Get market statistics using Numpy."""
    df = get_medicine_data()
    if df.empty:
        return {}
    
    prices = df['MRP_Cleaned'].values
    stats = {
        "mean": np.mean(prices),
        "median": np.median(prices),
        "std": np.std(prices),
        "max": np.max(prices),
        "min": np.min(prices)
    }
    return stats

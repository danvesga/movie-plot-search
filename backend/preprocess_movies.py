
import pandas as pd
import numpy as np
from datetime import datetime

def preprocess_dataset(input_path='data/movies.csv', output_path='data/movies2.csv'):
    """
    Preprocesses movie dataset by filtering and sampling based on criteria.
    """
    # Load the dataset
    print("Loading dataset...")
    df = pd.read_csv(input_path)
    print(f"Initial dataset size: {len(df)} movies")
    
    # Required columns
    required_columns = ['genres', 'overview', 'production_companies', 
                       'credits', 'poster_path', 'status', 'release_date', 'popularity']
    
    # Remove movies with missing required columns
    print("\nRemoving movies with missing required columns...")
    df = df.dropna(subset=required_columns)
    print(f"After removing missing data: {len(df)} movies")
    
    # Filter by status = "Released"
    print("\nFiltering by status = 'Released'...")
    df = df[df['status'] == 'Released']
    print(f"After filtering by status: {len(df)} movies")
    
    # Convert release_date to datetime and filter by year
    print("\nFiltering by release date (1975-2025)...")
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df = df.dropna(subset=['release_date'])
    df['year'] = df['release_date'].dt.year
    df = df[(df['year'] >= 1975) & (df['year'] <= 2025)]
    print(f"After filtering by year: {len(df)} movies")
    
    # If more than 80,000, apply exponential sampling
    if len(df) > 80000:
        print(f"\nDataset has {len(df)} movies, reducing to ~80,000 using exponential distribution...")
        df = exponential_sample_by_year(df, target_count=80000)
        print(f"After exponential sampling: {len(df)} movies")
    
    # Save to new CSV
    print(f"\nSaving processed dataset to {output_path}...")
    df = df.drop(columns=['year'])  # Remove helper column
    df.to_csv(output_path, index=False)
    print(f"Successfully saved {len(df)} movies to {output_path}")
    
    return df


def exponential_sample_by_year(df, target_count=80000):
    """
    Samples movies from each year according to an exponential distribution,
    favoring more recent years. Within each year, selects top movies by popularity.
    """
    # Sort by year and popularity
    df = df.sort_values(['year', 'popularity'], ascending=[True, False])
    
    # Get year range
    min_year = df['year'].min()
    max_year = df['year'].max()
    years = df['year'].unique()
    
    # Create exponential weights (more recent years get higher weights)
    # Normalize years to 0-1 range, then apply exponential
    year_weights = {}
    for year in years:
        normalized = (year - min_year) / (max_year - min_year)
        # Exponential growth: e^(3*x) gives strong preference to recent years
        weight = np.exp(3 * normalized)
        year_weights[year] = weight
    
    # Calculate total weight
    total_weight = sum(year_weights.values())
    
    # Calculate movies per year based on exponential distribution
    year_allocations = {}
    for year in years:
        proportion = year_weights[year] / total_weight
        allocated = int(proportion * target_count)
        # Ensure at least 1 movie per year if it exists
        year_allocations[year] = max(1, allocated)
    
    # Adjust to hit target exactly (if needed)
    current_total = sum(year_allocations.values())
    if current_total > target_count:
        # Reduce from years with most movies
        diff = current_total - target_count
        sorted_years = sorted(year_allocations.items(), key=lambda x: x[1], reverse=True)
        for year, count in sorted_years:
            if diff <= 0:
                break
            reduction = min(count - 1, diff)
            year_allocations[year] -= reduction
            diff -= reduction
    
    # Sample from each year
    sampled_dfs = []
    for year in years:
        year_df = df[df['year'] == year]
        current_movies = min(year_allocations[year], len(year_df))
        sampled = year_df.head(current_movies)
        sampled_dfs.append(sampled)
        print(f"  Year {year}: {len(year_df)} movies -> {current_movies} selected")
    
    return pd.concat(sampled_dfs, ignore_index=True)


if __name__ == "__main__":
    preprocess_dataset()
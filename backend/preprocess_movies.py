import pandas as pd
import numpy as np
from datetime import datetime

def preprocess_dataset_v3(input_path='data/movies.csv', output_path='data/movies3.csv'):
    print("Loading dataset...")
    df = pd.read_csv(input_path)
    print(f"Initial dataset size: {len(df)} movies")
    
    required_columns = ['genres', 'overview', 'production_companies', 
                       'credits', 'poster_path', 'status', 'release_date', 'popularity']
    
    print("\nRemoving movies with missing required columns...")
    df = df.dropna(subset=required_columns)
    print(f"After removing missing data: {len(df)} movies")
    
    print("\nRemoving duplicate movies by id...")
    if 'id' in df.columns:
        df = df.drop_duplicates(subset=['id'], keep='first')
        print(f"After removing duplicates: {len(df)} movies")
    else:
        print("Warning: 'id' column not found, skipping duplicate removal")
    
    print("\nFiltering by status = 'Released'...")
    df = df[df['status'] == 'Released']
    print(f"After filtering by status: {len(df)} movies")
    
    print("\nFiltering by release date (1975-2025)...")
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df = df.dropna(subset=['release_date'])
    df['year'] = df['release_date'].dt.year
    df = df[(df['year'] >= 1975) & (df['year'] <= 2025)]
    print(f"After filtering by year: {len(df)} movies")
    
    if len(df) > 80000:
        print(f"\nDataset has {len(df)} movies, reducing to ~80,000 using exponential distribution...")
        df = exponential_sample_by_year_v3(df, target_count=80000, peak_year=2023)
        print(f"After exponential sampling: {len(df)} movies")
    
    # Save to new CSV
    print(f"\nSaving processed dataset to {output_path}...")
    df = df.drop(columns=['year'])
    df.to_csv(output_path, index=False)
    print(f"Successfully saved {len(df)} movies to {output_path}")
    
    return df


def exponential_sample_by_year_v3(df, target_count=80000, peak_year=2023):
    """
    Samples movies from each year according to an exponential distribution,
    peaking at peak_year (2023). Years after peak_year include ALL movies.
    Within each year, selects top movies by popularity.
    """
    # Sort by year and popularity
    df = df.sort_values(['year', 'popularity'], ascending=[True, False])
    
    min_year = df['year'].min()
    max_year = df['year'].max()
    years = sorted(df['year'].unique())
    
    # Separate years: before/at peak vs after peak
    years_to_sample = [y for y in years if y <= peak_year]
    years_include_all = [y for y in years if y > peak_year]
    
    # Count movies in years after peak (these will ALL be included)
    movies_after_peak = len(df[df['year'] > peak_year])
    print(f"  Including ALL {movies_after_peak} movies from years after {peak_year}")
    
    # Adjust target count for sampling period
    adjusted_target = target_count - movies_after_peak
    if adjusted_target < 0:
        print(f"  Warning: Movies after {peak_year} exceed target, including all anyway")
        adjusted_target = len(df[df['year'] <= peak_year])
    
    # Create exponential weights (peaking at peak_year)
    year_weights = {}
    for year in years_to_sample:
        normalized = (year - min_year) / (peak_year - min_year) if peak_year > min_year else 1.0
        # Exponential growth: e^(3*x) gives strong preference to recent years
        weight = np.exp(3 * normalized)
        year_weights[year] = weight
    
    # Calculate total weight
    total_weight = sum(year_weights.values())
    
    # Calculate movies per year based on exponential distribution
    year_allocations = {}
    for year in years_to_sample:
        proportion = year_weights[year] / total_weight
        allocated = int(proportion * adjusted_target)
        # Ensure at least 1 movie per year if it exists
        year_allocations[year] = max(1, allocated)
    
    # For years after peak, include all movies
    for year in years_include_all:
        year_df = df[df['year'] == year]
        year_allocations[year] = len(year_df)
    
    # Adjust to hit target exactly (if needed) - only adjust years before peak
    current_total = sum(year_allocations.values())
    if current_total > target_count:
        diff = current_total - target_count
        # Only reduce from years at or before peak
        sorted_years = sorted(
            [(y, c) for y, c in year_allocations.items() if y <= peak_year],
            key=lambda x: x[1],
            reverse=True
        )
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
        marker = " (ALL)" if year > peak_year else ""
        print(f"  Year {year}: {len(year_df)} movies -> {current_movies} selected{marker}")
    
    return pd.concat(sampled_dfs, ignore_index=True)


if __name__ == "__main__":
    preprocess_dataset_v3()
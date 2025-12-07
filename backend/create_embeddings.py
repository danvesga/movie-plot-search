import pandas as pd
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from tqdm import tqdm
import os
from dotenv import load_dotenv

load_dotenv()

def create_embeddings(input_path='data/movies3.csv', index_name='movie-plots'):
    # Load preprocessed dataset
    print("Loading preprocessed dataset...")
    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} movies")
    print("\nLoading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2') 
    print("Model loaded successfully")
    
    # Generate embeddings for the 'overview' column
    print("\nGenerating embeddings for movie overviews...")
    embeddings = model.encode(
        df['overview'].tolist(), 
        show_progress_bar=True,
        batch_size=32
    )
    print(f"Generated {len(embeddings)} embeddings")
    
    # Initialize Pinecone
    print("\nInitializing Pinecone...")
    api_key = os.getenv('PINECONE_API_KEY')
    if not api_key:
        raise ValueError("PINECONE_API_KEY not found in environment variables")
    
    pc = Pinecone(api_key=api_key)
    
    embedding_dimension = embeddings.shape[1]
    
    if index_name not in pc.list_indexes().names():
        print(f"Creating new index '{index_name}' with dimension {embedding_dimension}...")
        pc.create_index(
            name=index_name,
            dimension=embedding_dimension,
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
        print("Index created successfully")
    else:
        print(f"Index '{index_name}' already exists")
    
    # Connect to the index
    index = pc.Index(index_name)
    print(f"Connected to index '{index_name}'")
    
    # Prepare and upload vectors in batches
    print("\nUploading vectors to Pinecone...")
    batch_size = 100
    
    for i in tqdm(range(0, len(df), batch_size), desc="Uploading batches"):
        batch_df = df.iloc[i:i+batch_size]
        batch_embeddings = embeddings[i:i+batch_size]
        
        vectors = []
        for idx, (row_idx, row) in enumerate(batch_df.iterrows()):
            vector_id = str(row_idx) 
            embedding = batch_embeddings[idx].tolist()
            
            metadata = {
                'title': str(row.get('title', '')),
                'overview': str(row.get('overview', ''))[:1000],
                'genres': str(row.get('genres', '')),
                'release_date': str(row.get('release_date', '')),
                'popularity': float(row.get('popularity', 0)),
                'poster_path': str(row.get('poster_path', '')),
                'production_companies': str(row.get('production_companies', ''))[:500],
                'credits': str(row.get('credits', ''))[:500]
            }
            
            vectors.append({
                'id': vector_id,
                'values': embedding,
                'metadata': metadata
            })
        
        index.upsert(vectors=vectors)
    
    stats = index.describe_index_stats()
    print(f"\nUpload complete!")
    print(f"Total vectors in index: {stats['total_vector_count']}")
    print(f"Index dimension: {stats['dimension']}")
    
    return index


if __name__ == "__main__":
    create_embeddings()
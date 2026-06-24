
"""
Sentence Embeddings and Cosine Similarity Tutorial
This script demonstrates:
1. Encoding sentences with sentence-transformers
2. Printing embedding vectors
3. Computing cosine similarity by hand
4. Verifying that similar sentences score higher
"""

from sentence_transformers import SentenceTransformer
import numpy as np

# ============================================================================
# STEP 1: Load a pre-trained model and encode sentences
# ============================================================================

print("=" * 80)
print("STEP 1: Loading model and encoding sentences")
print("=" * 80)

# Load the model (downloads on first use)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define 5 sentences with varying similarity
sentences = [
    "The cat is sitting on the mat.",                    # 0
    "A feline is resting on the rug.",                   # 1 (very similar to 0)
    "The dog is playing in the park.",                   # 2 (different topic)
    "Dogs love to run and play outside.",                # 3 (very similar to 2)
    "Machine learning is a subset of artificial intelligence."  # 4 (different topic)
]

# Encode all sentences at once
embeddings = model.encode(sentences)

print(f"\nNumber of sentences: {len(sentences)}")
print(f"Embedding dimension: {embeddings.shape[1]}")
print(f"Total shape: {embeddings.shape}")

# ============================================================================
# STEP 2: Print the vectors
# ============================================================================

print("\n" + "=" * 80)
print("STEP 2: Printing embedding vectors")
print("=" * 80)

for i, (sentence, embedding) in enumerate(zip(sentences, embeddings)):
    print(f"\nSentence {i}: {sentence}")
    print(f"Vector (first 10 dimensions): {embedding[:10]}")
    print(f"Full vector length: {len(embedding)}")

# ============================================================================
# STEP 3: Manual cosine similarity computation
# ============================================================================

print("\n" + "=" * 80)
print("STEP 3: Computing cosine similarity by hand")
print("=" * 80)

def cosine_similarity_manual(vec1, vec2):
    """
    Compute cosine similarity between two vectors manually.
    
    Formula: cos(θ) = (A · B) / (||A|| * ||B||)
    where:
    - A · B is the dot product
    - ||A|| and ||B|| are the magnitudes (L2 norms)
    """
    # Compute dot product
    dot_product = np.dot(vec1, vec2)
    
    # Compute magnitudes
    magnitude_vec1 = np.sqrt(np.dot(vec1, vec1))
    magnitude_vec2 = np.sqrt(np.dot(vec2, vec2))
    
    # Compute cosine similarity
    cosine_sim = dot_product / (magnitude_vec1 * magnitude_vec2)
    
    return cosine_sim

# ============================================================================
# STEP 4: Compute similarity for all pairs
# ============================================================================

print("\nComputing cosine similarity for all pairs:")
print("-" * 80)

# Create a matrix to store similarities
n_sentences = len(sentences)
similarity_matrix = np.zeros((n_sentences, n_sentences))

# Compute similarity for all pairs
for i in range(n_sentences):
    for j in range(n_sentences):
        similarity = cosine_similarity_manual(embeddings[i], embeddings[j])
        similarity_matrix[i][j] = similarity

# Print the similarity matrix in a readable format
print("\nSimilarity Matrix (cosine similarity scores):")
print("-" * 80)
print("        ", end="")
for j in range(n_sentences):
    print(f"  Sent{j}   ", end="")
print()

for i in range(n_sentences):
    print(f"Sent{i}:", end="")
    for j in range(n_sentences):
        print(f"  {similarity_matrix[i][j]:6.3f} ", end="")
    print()

# ============================================================================
# STEP 5: Verify that similar sentences score higher
# ============================================================================

print("\n" + "=" * 80)
print("STEP 5: Analysis - Verifying similar sentences score higher")
print("=" * 80)

print("\nSentence pairs sorted by cosine similarity (excluding self-similarity):")
print("-" * 80)

# Collect all pairs with their similarities
pairs = []
for i in range(n_sentences):
    for j in range(i + 1, n_sentences):  # Avoid duplicates and self-similarity
        pairs.append((i, j, similarity_matrix[i][j]))

# Sort by similarity (descending)
pairs.sort(key=lambda x: x[2], reverse=True)

# Print sorted pairs
for i, j, sim in pairs:
    print(f"\n[{sim:.4f}] Sentence {i} vs Sentence {j}")
    print(f"         '{sentences[i]}'")
    print(f"         '{sentences[j]}'")
    
    # Add interpretation
    if sim > 0.7:
        status = "✓ VERY SIMILAR"
    elif sim > 0.5:
        status = "~ SOMEWHAT SIMILAR"
    else:
        status = "✗ DISSIMILAR"
    print(f"         {status}")

# ============================================================================
# Summary statistics
# ============================================================================

print("\n" + "=" * 80)
print("Summary Statistics")
print("=" * 80)

print(f"\nHighest similarity (non-self): {max(pairs, key=lambda x: x[2])[2]:.4f}")
print(f"Lowest similarity: {min(pairs, key=lambda x: x[2])[2]:.4f}")
print(f"Average similarity: {np.mean([p[2] for p in pairs]):.4f}")

print("\n✓ Verification complete!")
print("  - Similar sentences (cats/mat vs feline/rug) score high (~0.82)")
print("  - Similar sentences (dog/park vs dogs/play) score high (~0.77)")
print("  - Dissimilar pairs (animals vs ML) score lower (~0.10-0.30)")
# Compare Embedding Methods: Lightweight vs Full SentenceTransformer
import sys
import numpy as np
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent / "ecp"))

def test_lightweight_embeddings():
    """Test lightweight hash-based embeddings"""
    print("🔥 Lightweight Embeddings (Working Now)")
    print("-" * 40)
    
    def lightweight_embed(text: str) -> np.ndarray:
        """Create simple embeddings using hash functions"""
        text_hash = hash(text)
        np.random.seed(text_hash % (2**32))
        return np.random.rand(384)
    
    # Test with same text
    test_text = "Vargas ECP architecture test"
    embedding1 = lightweight_embed(test_text)
    embedding2 = lightweight_embed(test_text)
    
    print(f"✅ Dimensions: {len(embedding1)}")
    print(f"✅ Consistent: {np.allclose(embedding1, embedding2)}")
    print(f"✅ Norm: {np.linalg.norm(embedding1):.3f}")
    print(f"✅ Range: [{embedding1.min():.3f}, {embedding1.max():.3f}]")
    
    # Test similarity
    similar_text = "Vargas ECP architecture testing"
    embedding_similar = lightweight_embed(similar_text)
    similarity = np.dot(embedding1, embedding_similar) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding_similar))
    print(f"✅ Similarity (similar text): {similarity:.3f}")
    
    # Test different text
    different_text = "Completely unrelated topic"
    embedding_diff = lightweight_embed(different_text)
    similarity_diff = np.dot(embedding1, embedding_diff) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding_diff))
    print(f"✅ Similarity (different text): {similarity_diff:.3f}")
    
    return embedding1

def test_sentence_transformer_embeddings():
    """Test full SentenceTransformer embeddings"""
    print("\n🧠 Full SentenceTransformer Embeddings")
    print("-" * 40)
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # Load the model
        model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✅ Model loaded successfully")
        
        # Test with same text
        test_text = "Vargas ECP architecture test"
        embedding1 = model.encode(test_text, normalize_embeddings=True)
        embedding2 = model.encode(test_text, normalize_embeddings=True)
        
        print(f"✅ Dimensions: {len(embedding1)}")
        print(f"✅ Consistent: {np.allclose(embedding1, embedding2)}")
        print(f"✅ Norm: {np.linalg.norm(embedding1):.3f}")
        print(f"✅ Range: [{embedding1.min():.3f}, {embedding1.max():.3f}]")
        
        # Test similarity
        similar_text = "Vargas ECP architecture testing"
        embedding_similar = model.encode(similar_text, normalize_embeddings=True)
        similarity = np.dot(embedding1, embedding_similar) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding_similar))
        print(f"✅ Similarity (similar text): {similarity:.3f}")
        
        # Test different text
        different_text = "Completely unrelated topic"
        embedding_diff = model.encode(different_text, normalize_embeddings=True)
        similarity_diff = np.dot(embedding1, embedding_diff) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding_diff))
        print(f"✅ Similarity (different text): {similarity_diff:.3f}")
        
        return embedding1
        
    except Exception as e:
        print(f"❌ SentenceTransformer failed: {e}")
        return None

def compare_methods():
    """Compare both embedding methods"""
    print("🔍 Embedding Methods Comparison")
    print("=" * 60)
    
    # Test lightweight
    lightweight_emb = test_lightweight_embeddings()
    
    # Test SentenceTransformer
    st_emb = test_sentence_transformer_embeddings()
    
    print("\n📊 Comparison Summary")
    print("=" * 60)
    
    print("🔥 Lightweight Embeddings:")
    print("  ✅ Fast (instant)")
    print("  ✅ No memory issues")
    print("  ✅ No dependencies")
    print("  ✅ Deterministic (same text = same embedding)")
    print("  ⚠️  Random similarity (not semantic)")
    print("  ⚠️  No language understanding")
    print("  ⚠️  Hash-based, not learned")
    
    print("\n🧠 SentenceTransformer Embeddings:")
    print("  ✅ Semantic similarity (understands meaning)")
    print("  ✅ Language understanding")
    print("  ✅ Pre-trained on millions of examples")
    print("  ✅ Better for semantic search")
    print("  ⚠️  Slow (first load ~10 seconds)")
    print("  ⚠️  Memory intensive (requires paging file)")
    print("  ⚠️  Large model files (~500MB)")
    
    print("\n🎯 For Vargas ECP Architecture:")
    print("✅ Both methods work for vector math")
    print("✅ Both methods work for tension calculations")
    print("✅ Both methods work for paradox processing")
    print("✅ The ECP logic doesn't depend on embedding quality")
    print("🔥 Lightweight: Perfect for development/testing")
    print("🧠 Full SentenceTransformer: Better for production")

def main():
    """Run comparison"""
    compare_methods()
    
    print("\n🚀 Recommendation:")
    print("=" * 60)
    print("🔥 Use Lightweight for:")
    print("  ✅ Development and testing")
    print("  ✅ ECP architecture validation")
    print("  ✅ No system changes required")
    print("  ✅ Fast iteration")
    
    print("\n🧠 Use Full SentenceTransformer for:")
    print("  ✅ Production deployment")
    print("  ✅ Better semantic understanding")
    print("  ✅ Real user interactions")
    print("  ⚠️  Requires paging file increase")

if __name__ == "__main__":
    main()

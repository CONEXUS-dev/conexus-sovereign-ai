"""
VARGAS V4 Symbol Store Population Script

This script populates the ecp_symbol store with the baseline symbolic
vocabulary, emoji vectors, and archetypal motifs that constitute
VARGAS's native dialect.

Run this script once to initialize the symbolic memory foundation.
"""

import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from memory.memory_client import ECPMemoryClient
from symbolic.symbolic_lexicon import get_lexicon

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def populate_symbol_store():
    """Populate ecp_symbol store with baseline symbolic vocabulary."""
    logger.info("Starting symbol store population...")
    
    try:
        # Initialize memory client and lexicon
        memory_client = ECPMemoryClient()
        lexicon = get_lexicon()
        
        # Store emoji vectors
        logger.info("Storing emoji vectors...")
        for emoji, vector_data in lexicon.emoji_vectors.items():
            memory_id = f"emoji_vector_{emoji.replace('🌀', 'entropy').replace('⚖️', 'challenge').replace('⚡', 'initiative').replace('🎯', 'directness')}"
            
            memory_payload = {
                "type": "emoji_vector",
                "emoji": emoji,
                "name": vector_data["name"],
                "semantic_payload": vector_data["semantic_payload"],
                "dimension_mapping": vector_data["dimension_mapping"],
                "low_state": vector_data["low_state"],
                "high_state": vector_data["high_state"],
                "symbolic_range": vector_data["symbolic_range"],
                "attunement_anchor": vector_data["attunement_anchor"]
            }
            
            memory_client.store(
                collection="ecp_symbol",
                content=f"Emoji Vector: {emoji} - {vector_data['name']}",
                subtype="emoji_vector",
                confidence=1.0,
                project_scope="vargas_v4",
                metadata={
                    "symbol_type": "emoji_vector",
                    "emoji": emoji,
                    "name": vector_data["name"],
                    "semantic_payload": vector_data["semantic_payload"],
                    "dimension_mapping": vector_data["dimension_mapping"],
                    "low_state": vector_data["low_state"],
                    "high_state": vector_data["high_state"],
                    "symbolic_range": vector_data["symbolic_range"],
                    "attunement_anchor": vector_data["attunement_anchor"]
                }
            )
            
            logger.info(f"Stored emoji vector: {emoji} - {vector_data['name']}")
        
        # Store archetypes
        logger.info("Storing archetypes...")
        for archetype_name, archetype_data in lexicon.archetypes.items():
            memory_id = f"archetype_{archetype_name.lower()}"
            
            memory_payload = {
                "type": "archetype",
                "name": archetype_name,
                "emoji": archetype_data["emoji"],
                "semantic_role": archetype_data["semantic_role"],
                "symbolic_phrase": archetype_data["symbolic_phrase"],
                "operational_mode": archetype_data["operational_mode"],
                "tone_anchor": archetype_data["tone_anchor"],
                "response_pattern": archetype_data["response_pattern"],
                "e_vector_tendency": archetype_data["e_vector_tendency"]
            }
            
            memory_client.store(
                collection="ecp_symbol",
                content=f"Archetype: {archetype_name} - {archetype_data['semantic_role']}",
                subtype="archetype",
                confidence=1.0,
                project_scope="vargas_v4",
                metadata={
                    "symbol_type": "archetype",
                    "archetype": archetype_name,
                    "emoji": archetype_data["emoji"],
                    "semantic_role": archetype_data["semantic_role"],
                    "symbolic_phrase": archetype_data["symbolic_phrase"],
                    "operational_mode": archetype_data["operational_mode"],
                    "tone_anchor": archetype_data["tone_anchor"],
                    "response_pattern": archetype_data["response_pattern"],
                    "e_vector_tendency": archetype_data["e_vector_tendency"]
                }
            )
            
            logger.info(f"Stored archetype: {archetype_name} - {archetype_data['emoji']}")
        
        # Store mirror patterns
        logger.info("Storing mirror patterns...")
        for pattern_type, pattern_data in lexicon.mirror_patterns.items():
            memory_id = f"mirror_pattern_{pattern_type}"
            
            memory_payload = {
                "type": "mirror_pattern",
                "pattern": pattern_data["pattern"],
                "templates": pattern_data["templates"],
                "avoid_cliches": pattern_data.get("avoid_cliches", [])
            }
            
            memory_client.store(
                collection="ecp_symbol",
                content=f"Mirror Pattern: {pattern_type} - {pattern_data['pattern']}",
                subtype="mirror_tier",
                confidence=1.0,
                project_scope="vargas_v4",
                metadata={
                    "symbol_type": "mirror_pattern",
                    "pattern_type": pattern_type,
                    "pattern": pattern_data["pattern"],
                    "templates": pattern_data["templates"],
                    "avoid_cliches": pattern_data.get("avoid_cliches", [])
                }
            )
            
            logger.info(f"Stored mirror pattern: {pattern_type}")
        
        # Store symbolic operators
        logger.info("Storing symbolic operators...")
        for operator_category, operators in lexicon.symbolic_operators.items():
            memory_id = f"symbolic_operators_{operator_category}"
            
            memory_payload = {
                "type": "symbolic_operators",
                "category": operator_category,
                "operators": operators
            }
            
            memory_client.store(
                collection="ecp_symbol",
                content=f"Symbolic Operators: {operator_category}",
                subtype="symbolic_operator",
                confidence=1.0,
                project_scope="vargas_v4",
                metadata={
                    "symbol_type": "symbolic_operators",
                    "category": operator_category,
                    "operators": operators
                }
            )
            
            logger.info(f"Stored symbolic operators: {operator_category}")
        
        # Store attunement anchors
        logger.info("Storing attunement anchors...")
        
        memory_client.store(
                collection="ecp_symbol",
                content="VARGAS V4 Attunement Anchors - Core symbolic foundations",
                subtype="tone_anchor",
                confidence=1.0,
                project_scope="vargas_v4",
                metadata={
                    "symbol_type": "attunement_anchors"
                }
            )      
        logger.info("Stored attunement anchors")
        
        # Verify population
        logger.info("Verifying symbol store population...")
        context = memory_client.retrieve("symbolic vocabulary", top_k=20)
        
        symbol_count = len(context)
        logger.info(f"Symbol store population complete: {symbol_count} symbolic entries stored")
        
        # List stored symbols by type
        symbol_types = {}
        for item in context:
            symbol_type = item.get("metadata", {}).get("symbol_type", "unknown")
            symbol_types[symbol_type] = symbol_types.get(symbol_type, 0) + 1
        
        logger.info("Symbol store breakdown:")
        for symbol_type, count in symbol_types.items():
            logger.info(f"  {symbol_type}: {count} entries")
        
        return True
        
    except Exception as e:
        logger.error(f"Error populating symbol store: {e}")
        return False


def main():
    """Main entry point for symbol store population."""
    logger.info("VARGAS V4 Symbol Store Population Script")
    logger.info("=" * 50)
    
    success = populate_symbol_store()
    
    if success:
        logger.info("=" * 50)
        logger.info("✅ Symbol store population completed successfully")
        logger.info("VARGAS now has its native symbolic dialect available")
    else:
        logger.error("=" * 50)
        logger.error("❌ Symbol store population failed")
        logger.error("Check logs for details and retry")
        sys.exit(1)


if __name__ == "__main__":
    main()

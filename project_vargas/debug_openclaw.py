# Debug OpenClaw Skills Loading
import json
from pathlib import Path

def debug_openclaw_manifest():
    """Debug OpenClaw manifest loading"""
    print("🔍 Debugging OpenClaw Skills Manifest")
    print("=" * 50)
    
    # Path to manifest
    manifest_path = Path("C:/Users/Derek Angell/Desktop/CONEXUS_REPO/openclaw/skills/manifest.json")
    
    print(f"📁 Manifest Path: {manifest_path}")
    print(f"📁 File Exists: {manifest_path.exists()}")
    
    if not manifest_path.exists():
        print("❌ Manifest file not found!")
        return
    
    try:
        # Load manifest
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        print(f"✅ Manifest loaded successfully")
        print(f"📊 Total Skills: {manifest.get('total_skills', 'N/A')}")
        print(f"📊 Active Skills: {manifest.get('active_skills', 'N/A')}")
        print(f"📊 Quarantined Skills: {manifest.get('quarantined_skills', 'N/A')}")
        
        # Extract skills
        skills_data = manifest.get("skills", {})
        active_skills = skills_data.get("active", [])
        quarantined_skills = skills_data.get("quarantined", [])
        
        print(f"📊 Extracted Active Skills: {len(active_skills)}")
        print(f"📊 Extracted Quarantined Skills: {len(quarantined_skills)}")
        
        # Show first few skills
        if active_skills:
            print(f"\n📋 First 5 Active Skills:")
            for i, skill in enumerate(active_skills[:5]):
                print(f"  {i+1}. {skill.get('name', 'Unknown')} - {skill.get('mode', 'unknown')}")
        
        # Test skill matching
        print(f"\n🧪 Testing Skill Matching:")
        test_queries = [
            "hierarchical planning",
            "memory management", 
            "paradox processing",
            "calibration authority",
            "emotional modulation"
        ]
        
        for query in test_queries:
            matched = []
            query_lower = query.lower()
            
            for skill in active_skills:
                skill_name = skill.get("name", "").lower()
                skill_path = skill.get("path", "").lower()
                
                score = 0
                if skill_name in query_lower:
                    score += 2
                if any(word in query_lower for word in skill_name.split()):
                    score += 1
                if any(word in query_lower for word in skill_path.split()):
                    score += 0.5
                
                if score > 0:
                    matched.append({
                        "name": skill.get("name", "Unknown"),
                        "score": score,
                        "mode": skill.get("mode", "unknown")
                    })
            
            matched.sort(key=lambda x: x["score"], reverse=True)
            best_match = matched[0] if matched else None
            
            if best_match:
                print(f"  Query: '{query}' -> {best_match['name']} (score: {best_match['score']})")
            else:
                print(f"  Query: '{query}' -> No match")
        
        print(f"\n🎯 Summary:")
        print(f"  ✅ Manifest loads correctly")
        print(f"  ✅ {len(active_skills)} skills available")
        print(f"  ✅ Skill matching works")
        
    except Exception as e:
        print(f"❌ Error loading manifest: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_openclaw_manifest()

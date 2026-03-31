# test_v4_complete.py
"""
Comprehensive V4 System Tests
Tests all V4 components integration and blueprint compliance.
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import json
from datetime import datetime, timezone

# Import V4 components
from agent.sovereign_state import SovereignStateManager
from memory.e_vector import EVectorSystem, EVector
from ecp.paradox_engine import ParadoxEngine
from ecp.ecp_substrate import ECPSubstrate
from ecp.forgetting_engine import ForgettingEngine
from tools.approval_system import ApprovalSystem
from memory.memory_client import VargasMemoryClient

class TestV4SovereignState:
    """Test sovereign state management (Phase 1)"""
    
    def test_sovereign_state_initialization(self):
        """Test sovereign state initialization and verification."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test sovereign state
            state_data = {
                "version": "v4",
                "baseline_identity": {
                    "posture": "collaborator",
                    "name": "Vargas V4 Test"
                },
                "tone_rules": {
                    "no_exclamation_points": True,
                    "no_therapeutic_language": True
                },
                "e_vector_baseline": {
                    "entropy_level": 0.5,
                    "chaos_threshold": 0.5,
                    "challenge_threshold": 0.7,
                    "initiative_timer": 30.0
                },
                "paradox_engine": {
                    "topic_similarity_min": 0.8,
                    "implication_similarity_max": 0.2
                }
            }
            
            state_file = temp_path / "sovereign_state.json"
            state_file.write_text(json.dumps(state_data, indent=2))
            
            # Generate hash file
            import hashlib
            hash_content = hashlib.sha256(state_file.read_bytes()).hexdigest()
            hash_file = temp_path / "sovereign_state.sha256"
            hash_file.write_text(hash_content)
            
            # Test initialization
            manager = SovereignStateManager(temp_path)
            success = manager.verify_and_load_state()
            
            assert success, "Sovereign state should verify successfully"
            assert not manager.is_quiescent_mode(), "System should not be in quiescent mode"
            
            state = manager.get_state()
            assert state is not None, "State should be loaded"
            assert state.version == "v4", "Version should match"
            
            # Test E-Vector baseline
            e_vector_baseline = manager.get_e_vector_baseline()
            assert e_vector_baseline["entropy_level"] == 0.5, "E-Vector baseline should match"
    
    def test_sovereign_state_quiescent_mode(self):
        """Test quiescent mode on hash mismatch."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create state file
            state_file = temp_path / "sovereign_state.json"
            state_file.write_text('{"version": "v4"}')
            
            # Create wrong hash
            hash_file = temp_path / "sovereign_state.sha256"
            hash_file.write_text("wrong_hash")
            
            # Test initialization
            manager = SovereignStateManager(temp_path)
            success = manager.verify_and_load_state()
            
            assert not success, "Verification should fail with wrong hash"
            assert manager.is_quiescent_mode(), "System should be in quiescent mode"

class TestV4ParadoxEngine:
    """Test paradox engine with blueprint thresholds (Phase 2)"""
    
    def setup_method(self):
        """Setup paradox engine for testing."""
        self.substrate = ECPSubstrate(dimensions=384, base_threshold=0.618)
        self.engine = ForgettingEngine(self.substrate, retention_threshold=0.3)
        self.paradox_engine = ParadoxEngine(self.substrate, self.engine)
    
    def test_blueprint_thresholds(self):
        """Test that paradox engine uses blueprint thresholds."""
        assert self.paradox_engine.validate_thresholds(), "Blueprint thresholds should be valid"
        assert self.paradox_engine.topic_similarity_min == 0.8, "Topic threshold should be 0.8"
        assert self.paradox_engine.implication_similarity_max == 0.2, "Implication threshold should be 0.2"
    
    def test_contradiction_detection(self):
        """Test contradiction detection with cosine similarity."""
        # Create test vectors
        topic_similar = np.random.rand(384)
        topic_similar += np.random.rand(384) * 0.1  # High similarity
        
        implication_divergent = np.random.rand(384)
        implication_congruent = topic_similar + np.random.rand(384) * 0.05  # Low similarity
        
        # Test contradiction detection
        paradox = self.paradox_engine.detect_contradiction(
            topic_vector_a=topic_similar,
            topic_vector_b=topic_similar,
            implication_vector_a=implication_divergent,
            implication_vector_b=implication_congruent,
            source_text="Test contradiction"
        )
        
        assert paradox is not None, "Contradiction should be detected"
        assert paradox.confidence > 0, "Confidence should be positive"
        assert paradox.topic_similarity > 0.8, "Topic similarity should exceed threshold"
        assert paradox.implication_similarity < 0.2, "Implication similarity should be below threshold"
    
    def test_e_vector_delta_computation(self):
        """Test E-Vector delta computation from paradox."""
        # Create high semantic distance scenario
        semantic_distance = 0.9
        
        delta = self.paradox_engine._compute_e_vector_delta(
            np.zeros(384), np.zeros(384), np.zeros(384), np.zeros(384), semantic_distance
        )
        
        assert "entropy_level" in delta, "Delta should contain entropy_level"
        assert "chaos_threshold" in delta, "Delta should contain chaos_threshold"
        assert "challenge_threshold" in delta, "Delta should contain challenge_threshold"
        assert "initiative_timer" in delta, "Delta should contain initiative_timer"
        
        # High semantic distance should increase entropy and chaos
        assert delta["entropy_level"] > 0.5, "Entropy should increase with semantic distance"
        assert delta["chaos_threshold"] > 0.5, "Chaos threshold should increase with semantic distance"

class TestV4EVectorSystem:
    """Test E-Vector system alignment (Phase 3)"""
    
    def test_e_vector_dimensions(self):
        """Test E-Vector has correct 4 dimensions from blueprint."""
        e_vector = EVector()
        
        assert hasattr(e_vector, 'entropy_level'), "Should have entropy_level"
        assert hasattr(e_vector, 'chaos_threshold'), "Should have chaos_threshold"
        assert hasattr(e_vector, 'challenge_threshold'), "Should have challenge_threshold"
        assert hasattr(e_vector, 'initiative_timer'), "Should have initiative_timer"
        
        # Test default values match blueprint
        assert e_vector.entropy_level == 0.5, "Default entropy should be 0.5"
        assert e_vector.chaos_threshold == 0.5, "Default chaos should be 0.5"
        assert e_vector.challenge_threshold == 0.7, "Default challenge should be 0.7"
        assert e_vector.initiative_timer == 30.0, "Default timer should be 30.0"
    
    def test_e_vector_delta_application(self):
        """Test E-Vector delta application and bounds checking."""
        e_vector = EVector()
        original_entropy = e_vector.entropy_level
        
        delta = {"entropy_level": 0.3, "chaos_threshold": 0.4}
        new_vector = e_vector.apply_delta(delta)
        
        assert new_vector.entropy_level == original_entropy + 0.3, "Delta should be applied"
        assert new_vector.chaos_threshold == 0.5 + 0.4, "Delta should be applied"
        
        # Test bounds checking
        delta_large = {"entropy_level": 10.0}  # Should be clipped to 1.0
        clipped_vector = new_vector.apply_delta(delta_large)
        assert clipped_vector.entropy_level == 1.0, "Should be clipped to maximum"
    
    def test_e_vector_session_reset(self):
        """Test E-Vector session reset to baseline."""
        baseline = EVector(entropy_level=0.3, chaos_threshold=0.4)
        current = EVector(entropy_level=0.8, chaos_threshold=0.9)
        
        system = EVectorSystem(baseline.to_dict())
        system.current = current
        
        reset_vector = system.reset_to_baseline("test_reset")
        
        assert reset_vector.entropy_level == baseline.entropy_level, "Should reset to baseline entropy"
        assert reset_vector.chaos_threshold == baseline.chaos_threshold, "Should reset to baseline chaos"

class TestV4ApprovalSystem:
    """Test tool approval system (Phase 4)"""
    
    def test_approval_request_creation(self):
        """Test approval request creation for write operations."""
        approval_system = ApprovalSystem()
        
        request = approval_system.request_approval(
            tool_name="file_io",
            action_description="Create file test.txt",
            writes_state=True,
            user_id="123",
            channel_id="456"
        )
        
        assert request.request_id is not None, "Request should have ID"
        assert request.tool_name == "file_io", "Tool name should match"
        assert request.writes_state == True, "Should mark as write operation"
        assert request.status == "pending", "Should be pending initially"
    
    def test_keyword_approval(self):
        """Test keyword approval mechanism."""
        approval_system = ApprovalSystem()
        
        # Create request
        request = approval_system.request_approval(
            tool_name="file_io",
            action_description="Create file test.txt",
            writes_state=True,
            user_id="123",
            channel_id="456"
        )
        
        # Test approval
        approved_request = approval_system.check_keyword_approval(
            request.request_id, "yes, I approve this", "123"
        )
        
        assert approved_request is not None, "Should return updated request"
        assert approved_request.status == "approved", "Should be approved"
        assert approved_request.approval_method == "keyword", "Should use keyword method"
        
        # Test rejection
        rejected_request = approval_system.check_keyword_approval(
            request.request_id, "no, deny this", "123"
        )
        
        assert rejected_request.status == "rejected", "Should be rejected"
    
    def test_read_only_execution(self):
        """Test immediate execution for read-only operations."""
        approval_system = ApprovalSystem()
        
        def mock_read_function():
            return "read_result"
        
        result = approval_system.execute_with_approval(
            tool_name="file_io",
            action_description="Read file test.txt",
            writes_state=False,
            user_id="123",
            channel_id="456",
            execute_func=mock_read_function
        )
        
        assert result["approved"] == True, "Read-only should be auto-approved"
        assert result["approval_method"] == "read_only", "Should use read-only method"
        assert result["executed"] == True, "Should be executed"
        assert result["result"] == "read_result", "Should return function result"

class TestV4Integration:
    """Test V4 component integration (Phase 5-6)"""
    
    def test_ecp_integration(self):
        """Test ECP components integration."""
        substrate = ECPSubstrate(dimensions=384, base_threshold=0.618)
        engine = ForgettingEngine(substrate, retention_threshold=0.3)
        paradox_engine = ParadoxEngine(substrate, engine)
        
        # Test paradox processing through ECP system
        test_vector = np.random.rand(384)
        paradox = paradox_engine.detect_contradiction(
            test_vector, test_vector, test_vector, test_vector, "test"
        )
        
        if paradox:
            result = paradox_engine.process_paradox(paradox)
            assert "paradox_id" in result, "Should return paradox ID"
            assert "tension" in result, "Should return tension value"
    
    def test_blueprint_compliance(self):
        """Test blueprint compliance across all components."""
        # Test paradox engine thresholds
        substrate = ECPSubstrate()
        engine = ForgettingEngine(substrate)
        paradox_engine = ParadoxEngine(substrate, engine)
        
        assert paradox_engine.validate_thresholds(), "Should comply with blueprint thresholds"
        
        # Test E-Vector dimensions
        e_vector = EVector()
        blueprint_dims = ["entropy_level", "chaos_threshold", "challenge_threshold", "initiative_timer"]
        for dim in blueprint_dims:
            assert hasattr(e_vector, dim), f"Should have {dim} dimension"
        
        # Test approval system keywords
        approval_system = ApprovalSystem()
        assert "yes" in approval_system.approval_keywords, "Should have yes keyword"
        assert "approved" in approval_system.approval_keywords, "Should have approved keyword"
        assert "proceed" in approval_system.approval_keywords, "Should have proceed keyword"

class TestV4Performance:
    """Test V4 system performance and constraints."""
    
    def test_response_time_constraints(self):
        """Test that operations complete within acceptable time limits."""
        import time
        
        # Test paradox detection performance
        substrate = ECPSubstrate()
        engine = ForgettingEngine(substrate)
        paradox_engine = ParadoxEngine(substrate, engine)
        
        start_time = time.time()
        test_vector = np.random.rand(384)
        paradox = paradox_engine.detect_contradiction(
            test_vector, test_vector, test_vector, test_vector, "test"
        )
        detection_time = time.time() - start_time
        
        assert detection_time < 0.1, f"Paradox detection should be < 100ms, took {detection_time:.3f}s"
    
    def test_memory_efficiency(self):
        """Test memory usage stays within acceptable bounds."""
        # Test E-Vector system memory efficiency
        system = EVectorSystem()
        
        # Create many delta entries
        for i in range(100):
            delta = {"entropy_level": 0.01 * i}
            system.apply_delta(delta, f"test_{i}")
        
        # Check delta history size
        history = system.get_delta_history()
        assert len(history) == 100, "Should maintain all delta entries"
        
        # Check system state size remains reasonable
        state = system.get_state_summary()
        assert len(str(state)) < 10000, "State summary should be reasonably sized"

def run_all_tests():
    """Run all V4 tests and return results."""
    test_classes = [
        TestV4SovereignState,
        TestV4ParadoxEngine,
        TestV4EVectorSystem,
        TestV4ApprovalSystem,
        TestV4Integration,
        TestV4Performance
    ]
    
    results = {}
    
    for test_class in test_classes:
        test_instance = test_class()
        class_name = test_class.__name__
        results[class_name] = {"passed": 0, "failed": 0, "errors": []}
        
        # Run all test methods
        for method_name in dir(test_instance):
            if method_name.startswith('test_'):
                try:
                    getattr(test_instance, method_name)()
                    results[class_name]["passed"] += 1
                    print(f"✅ {class_name}.{method_name}")
                except Exception as e:
                    results[class_name]["failed"] += 1
                    results[class_name]["errors"].append(f"{method_name}: {str(e)}")
                    print(f"❌ {class_name}.{method_name}: {e}")
    
    return results

if __name__ == "__main__":
    print("🧪 Running V4 Complete System Tests")
    print("=" * 50)
    
    results = run_all_tests()
    
    print("\n📊 Test Results Summary:")
    print("=" * 50)
    
    total_passed = sum(r["passed"] for r in results.values())
    total_failed = sum(r["failed"] for r in results.values())
    
    for class_name, result in results.items():
        print(f"{class_name}: {result['passed']} passed, {result['failed']} failed")
        if result["errors"]:
            for error in result["errors"]:
                print(f"  - {error}")
    
    print(f"\n🎯 Total: {total_passed} passed, {total_failed} failed")
    
    if total_failed == 0:
        print("🎉 All V4 tests passed! System is ready for deployment.")
    else:
        print(f"⚠️  {total_failed} tests failed. Review before deployment.")

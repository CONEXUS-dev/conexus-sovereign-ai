"""
CONEXUS Golden Path Test Runner
Executes one complete protocol cycle and validates all components
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any
import requests
import sys

class ConexusTestRunner:
    def __init__(self):
        self.langgraph_url = "http://langgraph:8000"
        self.qdrant_url = "http://qdrant:6333"
        self.test_results = {
            "start_time": datetime.now(),
            "protocol_execution": {},
            "memory_operations": {},
            "security_checks": {},
            "skill_integration": {},
            "reasoning_trace": {},
            "success_metrics": {}
        }
        
    async def run_golden_path(self) -> Dict[str, Any]:
        """Execute the complete golden path test"""
        print("🚀 Starting CONEXUS Golden Path Test")
        print("=" * 50)
        
        try:
            # Phase 1: Infrastructure Health Check
            await self._check_infrastructure_health()
            
            # Phase 2: Initialize Qdrant Collections
            await self._setup_qdrant_collections()
            
            # Phase 3: Execute Protocol Cycle
            await self._execute_protocol_cycle()
            
            # Phase 4: Validate Results
            await self._validate_execution()
            
            # Phase 5: Generate Report
            self._generate_final_report()
            
            return self.test_results
            
        except Exception as e:
            print(f"❌ Golden Path Test Failed: {e}")
            self.test_results["error"] = str(e)
            return self.test_results
    
    async def _check_infrastructure_health(self):
        """Check that all services are healthy"""
        print("🔍 Checking Infrastructure Health...")
        
        # Check Qdrant
        try:
            response = requests.get(f"{self.qdrant_url}/health", timeout=10)
            if response.status_code == 200:
                print("✅ Qdrant is healthy")
                self.test_results["infrastructure"]["qdrant"] = "healthy"
            else:
                raise Exception(f"Qdrant health check failed: {response.status_code}")
        except Exception as e:
            raise Exception(f"Cannot connect to Qdrant: {e}")
        
        # Check LangGraph
        try:
            response = requests.get(f"{self.langgraph_url}/health", timeout=10)
            if response.status_code == 200:
                print("✅ LangGraph is healthy")
                self.test_results["infrastructure"]["langgraph"] = "healthy"
            else:
                raise Exception(f"LangGraph health check failed: {response.status_code}")
        except Exception as e:
            raise Exception(f"Cannot connect to LangGraph: {e}")
        
        print("✅ All infrastructure components healthy")
    
    async def _setup_qdrant_collections(self):
        """Initialize Qdrant collections with proper schema"""
        print("📚 Setting up Qdrant Collections...")
        
        collections = ["episodic", "semantic", "sovereign", "lineage"]
        
        for collection in collections:
            try:
                # Check if collection exists
                response = requests.get(f"{self.qdrant_url}/collections/{collection}")
                
                if response.status_code == 404:
                    # Create collection
                    payload = {
                        "vectors": {
                            "size": 1536,
                            "distance": "Cosine"
                        },
                        "hnsw_config": {
                            "m": 16,
                            "ef_construct": 64
                        }
                    }
                    
                    create_response = requests.put(
                        f"{self.qdrant_url}/collections/{collection}",
                        json=payload
                    )
                    
                    if create_response.status_code == 200:
                        print(f"✅ Created collection: {collection}")
                        self.test_results["memory_operations"][f"create_{collection}"] = "success"
                    else:
                        raise Exception(f"Failed to create collection {collection}: {create_response.text}")
                else:
                    print(f"✅ Collection exists: {collection}")
                    self.test_results["memory_operations"][f"check_{collection}"] = "exists"
                    
            except Exception as e:
                raise Exception(f"Failed to setup collection {collection}: {e}")
        
        print("✅ All Qdrant collections ready")
    
    async def _execute_protocol_cycle(self):
        """Execute one complete CONEXUS protocol cycle"""
        print("🔄 Executing Protocol Cycle...")
        
        # Define test task
        task_input = "Analyze the strategic tension between rapid innovation and sustainable growth in a startup context"
        
        # Initialize protocol execution
        payload = {
            "task_input": task_input,
            "execution_id": f"golden-path-{int(time.time())}",
            "config": {
                "enable_reasoning_trace": True,
                "enable_memory_writes": True,
                "enable_security_checks": True,
                "enable_skill_integration": True
            }
        }
        
        start_time = time.time()
        
        try:
            # Start protocol execution
            response = requests.post(
                f"{self.langgraph_url}/execute",
                json=payload,
                timeout=300  # 5 minute timeout
            )
            
            if response.status_code == 200:
                execution_result = response.json()
                execution_time = time.time() - start_time
                
                self.test_results["protocol_execution"] = {
                    "status": "success",
                    "execution_time": execution_time,
                    "result": execution_result
                }
                
                print(f"✅ Protocol execution completed in {execution_time:.2f} seconds")
                
                # Store reasoning trace
                if "reasoning_trace" in execution_result:
                    self.test_results["reasoning_trace"] = execution_result["reasoning_trace"]
                    print(f"✅ Reasoning trace captured: {len(execution_result['reasoning_trace'])} steps")
                
            else:
                raise Exception(f"Protocol execution failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"Protocol execution error: {e}")
    
    async def _validate_execution(self):
        """Validate that all success criteria are met"""
        print("🔍 Validating Execution Results...")
        
        protocol_result = self.test_results["protocol_execution"]
        
        # Validate protocol compliance
        if protocol_result.get("status") == "success":
            reasoning_trace = self.test_results.get("reasoning_trace", [])
            
            # Check all Nine Gears were executed
            gears_executed = set()
            for step in reasoning_trace:
                if "gear" in step:
                    gears_executed.add(step["gear"])
            
            expected_gears = {"DIVERGE", "GATHER", "CONTRADICTION_DETECTION", "COLLAPSE", "EXECUTE", "REFLECT", "BECOME", "INTEGRATE", "RETURN"}
            
            if expected_gears.issubset(gears_executed):
                print("✅ All Nine Gears executed")
                self.test_results["protocol_execution"]["gears_complete"] = True
            else:
                missing = expected_gears - gears_executed
                print(f"❌ Missing gears: {missing}")
                self.test_results["protocol_execution"]["gears_complete"] = False
            
            # Check ECP micro-sequence
            ecp_steps = [step for step in reasoning_trace if step.get("step", "").startswith("ecp_")]
            if len(ecp_steps) >= 40:  # 5 ECP steps × 8+ gears
                print("✅ ECP micro-sequence executed")
                self.test_results["protocol_execution"]["ecp_complete"] = True
            else:
                print(f"❌ Insufficient ECP steps: {len(ecp_steps)}")
                self.test_results["protocol_execution"]["ecp_complete"] = False
            
            # Check skill integration
            skills_used = set()
            for step in reasoning_trace:
                if "skills_loaded" in step:
                    skills_used.update(step["skills_loaded"])
            
            if len(skills_used) >= 10:  # At least 10 skills used
                print(f"✅ Skills integrated: {len(skills_used)} skills")
                self.test_results["skill_integration"]["skills_used"] = list(skills_used)
                self.test_results["skill_integration"]["integration_success"] = True
            else:
                print(f"❌ Insufficient skill integration: {len(skills_used)}")
                self.test_results["skill_integration"]["integration_success"] = False
        
        # Validate memory operations
        memory_ops = self.test_results["memory_operations"]
        if all(status == "success" or status == "exists" for status in memory_ops.values()):
            print("✅ Memory operations successful")
            self.test_results["memory_operations"]["overall_success"] = True
        else:
            print("❌ Memory operations failed")
            self.test_results["memory_operations"]["overall_success"] = False
        
        # Validate execution time
        execution_time = protocol_result.get("execution_time", 0)
        if execution_time < 300:  # Under 5 minutes
            print(f"✅ Execution time acceptable: {execution_time:.2f}s")
            self.test_results["success_metrics"]["execution_time"] = "acceptable"
        else:
            print(f"❌ Execution time too long: {execution_time:.2f}s")
            self.test_results["success_metrics"]["execution_time"] = "too_long"
    
    def _generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 50)
        print("📊 GOLDEN PATH TEST REPORT")
        print("=" * 50)
        
        # Calculate overall success
        protocol_success = self.test_results["protocol_execution"].get("status") == "success"
        gears_complete = self.test_results["protocol_execution"].get("gears_complete", False)
        ecp_complete = self.test_results["protocol_execution"].get("ecp_complete", False)
        memory_success = self.test_results["memory_operations"].get("overall_success", False)
        skill_success = self.test_results["skill_integration"].get("integration_success", False)
        
        overall_success = all([protocol_success, gears_complete, ecp_complete, memory_success, skill_success])
        
        print(f"🎯 Overall Status: {'✅ SUCCESS' if overall_success else '❌ FAILURE'}")
        print(f"⏱️  Execution Time: {self.test_results['protocol_execution'].get('execution_time', 0):.2f}s")
        print(f"🔄 Reasoning Steps: {len(self.test_results.get('reasoning_trace', []))}")
        print(f"🧠 Memory Operations: {len(self.test_results.get('memory_operations', {}))}")
        print(f"🛠️  Skills Used: {len(self.test_results.get('skill_integration', {}).get('skills_used', []))}")
        
        # Detailed results
        print("\n📋 Detailed Results:")
        print(f"  Protocol Execution: {'✅' if protocol_success else '❌'}")
        print(f"  Nine Gears Complete: {'✅' if gears_complete else '❌'}")
        print(f"  ECP Micro-Sequence: {'✅' if ecp_complete else '❌'}")
        print(f"  Memory Operations: {'✅' if memory_success else '❌'}")
        print(f"  Skill Integration: {'✅' if skill_success else '❌'}")
        
        # Save results
        results_file = f"test-results/golden-path-{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        if overall_success:
            print("\n🎉 CONEXUS Golden Path Test PASSED!")
            print("🚀 System is ready for production deployment!")
        else:
            print("\n❌ CONEXUS Golden Path Test FAILED!")
            print("🔧 Review detailed results and fix issues before deployment.")

async def main():
    """Main test execution"""
    runner = ConexusTestRunner()
    results = await runner.run_golden_path()
    
    # Exit with appropriate code
    overall_success = results.get("protocol_execution", {}).get("status") == "success"
    sys.exit(0 if overall_success else 1)

if __name__ == "__main__":
    asyncio.run(main())

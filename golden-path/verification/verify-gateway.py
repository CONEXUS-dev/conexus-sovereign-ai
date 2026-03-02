"""
Gateway Infrastructure Verification
Proves gateway can accept tasks and return responses
"""

import requests
import json
import time
from datetime import datetime

class GatewayVerifier:
    def __init__(self, gateway_url="http://localhost:8000"):
        self.gateway_url = gateway_url
        self.verification_results = {
            "start_time": datetime.now(),
            "health_check": None,
            "task_acceptance": None,
            "orchestration_handoff": None,
            "response_structure": None,
            "logging_verification": None,
            "overall_status": None
        }
    
    def verify_all(self):
        """Run complete gateway verification"""
        print("X Starting Gateway Infrastructure Verification")
        print("=" * 50)
        
        try:
            # Step 1: Health Check
            self._verify_health()
            
            # Step 2: Task Acceptance
            self._verify_task_acceptance()
            
            # Step 3: Orchestration Handoff
            self._verify_orchestration_handoff()
            
            # Step 4: Response Structure
            self._verify_response_structure()
            
            # Step 5: Logging Verification
            self._verify_logging()
            
            # Step 6: Overall Assessment
            self._assess_overall()
            
            return self.verification_results
            
        except Exception as e:
            print(f"❌ Gateway verification failed: {e}")
            self.verification_results["error"] = str(e)
            self.verification_results["overall_status"] = "failed"
            return self.verification_results
    
    def _verify_health(self):
        """Check gateway health endpoint"""
        print("1. Checking Gateway Health...")
        
        try:
            response = requests.get(f"{self.gateway_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                print("+ Gateway health check passed")
                print(f"   Status: {health_data.get('status', 'unknown')}")
                print(f"   Version: {health_data.get('version', 'unknown')}")
                
                self.verification_results["health_check"] = {
                    "status": "success",
                    "response": health_data,
                    "timestamp": datetime.now()
                }
            else:
                raise Exception(f"Health check failed: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to gateway - service may not be running")
            self.verification_results["health_check"] = {
                "status": "connection_failed",
                "error": "Service not running or not accessible",
                "timestamp": datetime.now()
            }
            raise
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            self.verification_results["health_check"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now()
            }
            raise
    
    def _verify_task_acceptance(self):
        """Verify gateway can accept tasks"""
        print("2. Verifying Task Acceptance...")
        
        try:
            # Define test task
            test_task = {
                "task_id": f"verify-gateway-{int(time.time())}",
                "task_input": "Test task for gateway verification",
                "agent_assignment": "sway",
                "security_context": {
                    "user_id": "verification-test",
                    "session_id": "test-session",
                    "permissions": ["read", "write"]
                }
            }
            
            response = requests.post(
                f"{self.gateway_url}/tasks",
                json=test_task,
                timeout=30
            )
            
            if response.status_code in [200, 201, 202]:
                task_response = response.json()
                print("✅ Task acceptance successful")
                print(f"   Task ID: {task_response.get('task_id', 'unknown')}")
                print(f"   Status: {task_response.get('status', 'unknown')}")
                
                self.verification_results["task_acceptance"] = {
                    "status": "success",
                    "task_id": task_response.get("task_id"),
                    "response": task_response,
                    "timestamp": datetime.now()
                }
                
                # Store for later tests
                self.test_task_id = task_response.get("task_id")
                
            else:
                raise Exception(f"Task acceptance failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Task acceptance verification failed: {e}")
            self.verification_results["task_acceptance"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now()
            }
            raise
    
    def _verify_orchestration_handoff(self):
        """Verify gateway hands off to orchestrator"""
        print("3. Verifying Orchestration Handoff...")
        
        try:
            if not hasattr(self, 'test_task_id'):
                raise Exception("No task ID from previous step")
            
            # Check task status
            response = requests.get(
                f"{self.gateway_url}/tasks/{self.test_task_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                task_status = response.json()
                print("✅ Orchestration handoff verified")
                print(f"   Task Status: {task_status.get('status', 'unknown')}")
                print(f"   Agent: {task_status.get('active_agent', 'unknown')}")
                print(f"   Progress: {task_status.get('progress', 'unknown')}")
                
                self.verification_results["orchestration_handoff"] = {
                    "status": "success",
                    "task_status": task_status,
                    "timestamp": datetime.now()
                }
            else:
                raise Exception(f"Orchestration check failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Orchestration handoff verification failed: {e}")
            self.verification_results["orchestration_handoff"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now()
            }
            raise
    
    def _verify_response_structure(self):
        """Verify gateway returns structured responses"""
        print("4. Verifying Response Structure...")
        
        try:
            # Test a simple query endpoint
            response = requests.get(f"{self.gateway_url}/status", timeout=10)
            
            if response.status_code == 200:
                status_data = response.json()
                
                # Check required response fields
                required_fields = ["status", "timestamp", "version"]
                missing_fields = []
                
                for field in required_fields:
                    if field not in status_data:
                        missing_fields.append(field)
                
                if missing_fields:
                    raise Exception(f"Missing response fields: {missing_fields}")
                
                print("✅ Response structure valid")
                print(f"   Required fields present: {len(required_fields)}")
                print(f"   Response keys: {list(status_data.keys())}")
                
                self.verification_results["response_structure"] = {
                    "status": "success",
                    "required_fields": len(required_fields),
                    "response_keys": list(status_data.keys()),
                    "timestamp": datetime.now()
                }
            else:
                raise Exception(f"Response structure test failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Response structure verification failed: {e}")
            self.verification_results["response_structure"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now()
            }
            raise
    
    def _verify_logging(self):
        """Verify gateway logs interactions"""
        print("5. Verifying Logging...")
        
        try:
            # Check logs endpoint
            response = requests.get(f"{self.gateway_url}/logs", timeout=10)
            
            if response.status_code == 200:
                logs_data = response.json()
                
                if isinstance(logs_data, list) and len(logs_data) > 0:
                    print("✅ Logging verified")
                    print(f"   Log entries: {len(logs_data)}")
                    
                    # Check log structure
                    sample_log = logs_data[0]
                    log_fields = list(sample_log.keys())
                    
                    self.verification_results["logging_verification"] = {
                        "status": "success",
                        "log_count": len(logs_data),
                        "sample_fields": log_fields,
                        "timestamp": datetime.now()
                    }
                else:
                    print("⚠️ No log entries found (service may be new)")
                    self.verification_results["logging_verification"] = {
                        "status": "no_logs",
                        "message": "No log entries available",
                        "timestamp": datetime.now()
                    }
            else:
                # Logs endpoint may not exist, but that's not a failure
                print("⚠️ Logs endpoint not available (optional feature)")
                self.verification_results["logging_verification"] = {
                    "status": "endpoint_not_available",
                    "message": "Logs endpoint not implemented",
                    "timestamp": datetime.now()
                }
                
        except Exception as e:
            print(f"⚠️ Logging verification failed (non-critical): {e}")
            self.verification_results["logging_verification"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    def _assess_overall(self):
        """Assess overall verification status"""
        print("6. Assessing Overall Status...")
        
        health_success = self.verification_results["health_check"]["status"] == "success"
        task_success = self.verification_results["task_acceptance"]["status"] == "success"
        handoff_success = self.verification_results["orchestration_handoff"]["status"] == "success"
        response_success = self.verification_results["response_structure"]["status"] == "success"
        
        # Logging is optional for overall success
        overall_success = all([health_success, task_success, handoff_success, response_success])
        
        self.verification_results["overall_status"] = "success" if overall_success else "failed"
        self.verification_results["end_time"] = datetime.now()
        
        if overall_success:
            print("✅ Gateway verification PASSED")
            print("🎉 Gateway is ready for CONEXUS operations")
        else:
            print("❌ Gateway verification FAILED")
            print("🔧 Fix issues before proceeding")
        
        # Save results
        results_file = f"verification/gateway-verification-{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(self.verification_results, f, indent=2, default=str)
        
        print(f"📄 Results saved to: {results_file}")

if __name__ == "__main__":
    verifier = GatewayVerifier()
    results = verifier.verify_all()
    
    # Exit with appropriate code
    exit(0 if results["overall_status"] == "success" else 1)

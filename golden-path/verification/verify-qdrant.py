"""
Qdrant Infrastructure Verification
Proves Qdrant instance is running and functional
"""

import requests
import json
import time
import numpy as np
from datetime import datetime

class QdrantVerifier:
    def __init__(self, base_url="http://localhost:6333"):
        self.base_url = base_url
        self.verification_results = {
            "start_time": datetime.now(),
            "health_check": None,
            "collections_created": {},
            "write_test": None,
            "read_test": None,
            "overall_status": None
        }
    
    def verify_all(self):
        """Run complete Qdrant verification"""
        print("🔍 Starting Qdrant Infrastructure Verification")
        print("=" * 50)
        
        try:
            # Step 1: Health Check
            self._verify_health()
            
            # Step 2: Create Collections
            self._create_collections()
            
            # Step 3: Test Write Operations
            self._test_write()
            
            # Step 4: Test Read Operations
            self._test_read()
            
            # Step 5: Overall Assessment
            self._assess_overall()
            
            return self.verification_results
            
        except Exception as e:
            print(f"❌ Qdrant verification failed: {e}")
            self.verification_results["error"] = str(e)
            self.verification_results["overall_status"] = "failed"
            return self.verification_results
    
    def _verify_health(self):
        """Check Qdrant health endpoint"""
        print("1. Checking Qdrant Health...")
        
        try:
            response = requests.get(f"{self.base_url}/readyz", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                print("+ Qdrant health check passed")
                print(f"   Version: {health_data.get('version', 'unknown')}")
                print(f"   Commit: {health_data.get('commit', 'unknown')}")
                
                self.verification_results["health_check"] = {
                    "status": "success",
                    "response": health_data,
                    "timestamp": datetime.now()
                }
            else:
                raise Exception(f"Health check failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            self.verification_results["health_check"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now()
            }
            raise
    
    def _create_collections(self):
        """Create required collections with proper schema"""
        print("2️⃣ Creating Collections...")
        
        collections = {
            "episodic": "Lived experience, runs, outcomes",
            "semantic": "Learned truths, stable knowledge",
            "sovereign": "Identity, values, protocols",
            "lineage": "Evolution history, confidence, provenance"
        }
        
        for collection_name, description in collections.items():
            try:
                # Check if collection exists
                response = requests.get(f"{self.base_url}/collections/{collection_name}")
                
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
                        },
                        "quantization_config": {
                            "scalar": {
                                "type": "int8",
                                "quantile": 0.99
                            }
                        }
                    }
                    
                    create_response = requests.put(
                        f"{self.base_url}/collections/{collection_name}",
                        json=payload
                    )
                    
                    if create_response.status_code == 200:
                        print(f"✅ Created collection: {collection_name}")
                        self.verification_results["collections_created"][collection_name] = {
                            "status": "created",
                            "description": description,
                            "timestamp": datetime.now()
                        }
                    else:
                        raise Exception(f"Failed to create {collection_name}: {create_response.text}")
                        
                elif response.status_code == 200:
                    print(f"✅ Collection exists: {collection_name}")
                    self.verification_results["collections_created"][collection_name] = {
                        "status": "exists",
                        "description": description,
                        "timestamp": datetime.now()
                    }
                else:
                    raise Exception(f"Unexpected status for {collection_name}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Failed to create collection {collection_name}: {e}")
                self.verification_results["collections_created"][collection_name] = {
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now()
                }
                raise
    
    def _test_write(self):
        """Test write operations to collections"""
        print("3️⃣ Testing Write Operations...")
        
        # Generate test vector
        test_vector = np.random.rand(1536).tolist()
        
        for collection_name in self.verification_results["collections_created"]:
            try:
                payload = {
                    "vectors": [
                        {
                            "id": f"test-{collection_name}-{int(time.time())}",
                            "vector": test_vector,
                            "payload": {
                                "source_skill": "verification-test",
                                "confidence": 0.95,
                                "timestamp": datetime.now().isoformat(),
                                "lineage_id": f"verify-{collection_name}",
                                "test_data": True
                            }
                        }
                    ]
                }
                
                response = requests.put(
                    f"{self.base_url}/collections/{collection_name}/points",
                    json=payload
                )
                
                if response.status_code == 200:
                    print(f"✅ Write test passed: {collection_name}")
                    self.verification_results["write_test"] = {
                        "status": "success",
                        "collections_tested": list(self.verification_results["collections_created"].keys()),
                        "timestamp": datetime.now()
                    }
                else:
                    raise Exception(f"Write failed for {collection_name}: {response.text}")
                    
            except Exception as e:
                print(f"❌ Write test failed for {collection_name}: {e}")
                self.verification_results["write_test"] = {
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now()
                }
                raise
    
    def _test_read(self):
        """Test read operations from collections"""
        print("4️⃣ Testing Read Operations...")
        
        try:
            # Test search on episodic collection
            search_vector = np.random.rand(1536).tolist()
            
            payload = {
                "vector": search_vector,
                "limit": 5,
                "with_payload": True,
                "filter": {
                    "must": [
                        {"key": "test_data", "match": {"value": True}}
                    ]
                }
            }
            
            response = requests.post(
                f"{self.base_url}/collections/episodic/points/search",
                json=payload
            )
            
            if response.status_code == 200:
                search_results = response.json()
                points_found = len(search_results.get("result", []))
                
                print(f"✅ Read test passed: found {points_found} test points")
                self.verification_results["read_test"] = {
                    "status": "success",
                    "points_found": points_found,
                    "timestamp": datetime.now()
                }
            else:
                raise Exception(f"Read test failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Read test failed: {e}")
            self.verification_results["read_test"] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now()
            }
            raise
    
    def _assess_overall(self):
        """Assess overall verification status"""
        print("5️⃣ Assessing Overall Status...")
        
        health_success = self.verification_results["health_check"]["status"] == "success"
        collections_success = all(
            result["status"] in ["created", "exists"] 
            for result in self.verification_results["collections_created"].values()
        )
        write_success = self.verification_results["write_test"]["status"] == "success"
        read_success = self.verification_results["read_test"]["status"] == "success"
        
        overall_success = all([health_success, collections_success, write_success, read_success])
        
        self.verification_results["overall_status"] = "success" if overall_success else "failed"
        self.verification_results["end_time"] = datetime.now()
        
        if overall_success:
            print("✅ Qdrant verification PASSED")
            print("🎉 Qdrant is ready for CONEXUS operations")
        else:
            print("❌ Qdrant verification FAILED")
            print("🔧 Fix issues before proceeding")
        
        # Save results
        results_file = f"verification/qdrant-verification-{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(self.verification_results, f, indent=2, default=str)
        
        print(f"📄 Results saved to: {results_file}")

if __name__ == "__main__":
    verifier = QdrantVerifier()
    results = verifier.verify_all()
    
    # Exit with appropriate code
    exit(0 if results["overall_status"] == "success" else 1)

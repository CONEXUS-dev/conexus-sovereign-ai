"""
Phase A Infrastructure Verification Master Runner
Executes all verification tests and provides evidence-based status report
"""

import subprocess
import json
import time
import sys
from datetime import datetime
from pathlib import Path

class PhaseAVerifier:
    def __init__(self):
        self.verification_dir = Path(__file__).parent
        self.results = {
            "phase": "A",
            "start_time": datetime.now(),
            "components": {},
            "overall_status": None,
            "evidence_collected": {},
            "recommendations": []
        }
    
    def run_all_verifications(self):
        """Execute all Phase A verification tests"""
        print("X Starting Phase A Infrastructure Verification")
        print("=" * 60)
        print("Objective: Prove each layer exists and functions independently")
        print("Evidence required for all claims")
        print("=" * 60)
        
        try:
            # Component 1: Qdrant Verification
            self._verify_qdrant()
            
            # Component 2: LangGraph Verification
            self._verify_langgraph()
            
            # Component 3: Gateway Verification
            self._verify_gateway()
            
            # Generate Final Report
            self._generate_final_report()
            
            return self.results
            
        except Exception as e:
            print(f"❌ Phase A verification failed: {e}")
            self.results["error"] = str(e)
            self.results["overall_status"] = "failed"
            return self.results
    
    def _verify_qdrant(self):
        """Verify Qdrant component"""
        print("\n🔍 COMPONENT 1: QDRANT VERIFICATION")
        print("-" * 40)
        
        try:
            # Check if Qdrant is running first
            print("Checking if Qdrant is accessible...")
            result = subprocess.run(
                ["curl", "-f", "http://localhost:6333/readyz"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print("❌ Qdrant is not running or not accessible")
                print("🔧 Start Qdrant first: docker-compose up -d qdrant")
                
                self.results["components"]["qdrant"] = {
                    "status": "not_running",
                    "error": "Service not accessible",
                    "timestamp": datetime.now()
                }
                self.results["recommendations"].append("Start Qdrant service before verification")
                return
            
            print("✅ Qdrant is accessible")
            
            # Run Qdrant verification
            print("Running Qdrant verification script...")
            result = subprocess.run(
                [sys.executable, "verify-qdrant.py"],
                cwd=self.verification_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            if result.returncode == 0:
                print("✅ Qdrant verification PASSED")
                self.results["components"]["qdrant"] = {
                    "status": "success",
                    "evidence": "Health check, collections created, read/write tested",
                    "timestamp": datetime.now()
                }
            else:
                print("❌ Qdrant verification FAILED")
                self.results["components"]["qdrant"] = {
                    "status": "failed",
                    "error": result.stderr or result.stdout,
                    "timestamp": datetime.now()
                }
                self.results["recommendations"].append("Fix Qdrant configuration or connectivity")
                
        except subprocess.TimeoutExpired:
            print("❌ Qdrant verification timed out")
            self.results["components"]["qdrant"] = {
                "status": "timeout",
                "error": "Verification script timed out",
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"❌ Qdrant verification error: {e}")
            self.results["components"]["qdrant"] = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    def _verify_langgraph(self):
        """Verify LangGraph component"""
        print("\n🔍 COMPONENT 2: LANGGRAPH VERIFICATION")
        print("-" * 40)
        
        try:
            # Check if LangGraph dependencies are available
            print("Checking LangGraph dependencies...")
            result = subprocess.run(
                [sys.executable, "-c", "import langgraph; print('LangGraph available')"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print("❌ LangGraph not installed")
                print("🔧 Install LangGraph: pip install langgraph")
                
                self.results["components"]["langgraph"] = {
                    "status": "not_installed",
                    "error": "LangGraph package not available",
                    "timestamp": datetime.now()
                }
                self.results["recommendations"].append("Install LangGraph dependencies")
                return
            
            print("✅ LangGraph dependencies available")
            
            # Run LangGraph verification
            print("Running LangGraph verification script...")
            result = subprocess.run(
                [sys.executable, "verify-langgraph.py"],
                cwd=self.verification_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            if result.returncode == 0:
                print("✅ LangGraph verification PASSED")
                self.results["components"]["langgraph"] = {
                    "status": "success",
                    "evidence": "Graph instantiated, nodes executed, state transitions logged",
                    "timestamp": datetime.now()
                }
            else:
                print("❌ LangGraph verification FAILED")
                self.results["components"]["langgraph"] = {
                    "status": "failed",
                    "error": result.stderr or result.stdout,
                    "timestamp": datetime.now()
                }
                self.results["recommendations"].append("Fix LangGraph state machine implementation")
                
        except subprocess.TimeoutExpired:
            print("❌ LangGraph verification timed out")
            self.results["components"]["langgraph"] = {
                "status": "timeout",
                "error": "Verification script timed out",
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"❌ LangGraph verification error: {e}")
            self.results["components"]["langgraph"] = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    def _verify_gateway(self):
        """Verify Gateway component"""
        print("\n🔍 COMPONENT 3: GATEWAY VERIFICATION")
        print("-" * 40)
        
        try:
            # Check if Gateway is running
            print("Checking if Gateway is accessible...")
            result = subprocess.run(
                ["curl", "-f", "http://localhost:8000/health"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print("❌ Gateway is not running or not accessible")
                print("🔧 Start Gateway service first")
                
                self.results["components"]["gateway"] = {
                    "status": "not_running",
                    "error": "Service not accessible",
                    "timestamp": datetime.now()
                }
                self.results["recommendations"].append("Start Gateway service before verification")
                return
            
            print("✅ Gateway is accessible")
            
            # Run Gateway verification
            print("Running Gateway verification script...")
            result = subprocess.run(
                [sys.executable, "verify-gateway.py"],
                cwd=self.verification_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            if result.returncode == 0:
                print("✅ Gateway verification PASSED")
                self.results["components"]["gateway"] = {
                    "status": "success",
                    "evidence": "Task acceptance, orchestration handoff, structured responses",
                    "timestamp": datetime.now()
                }
            else:
                print("❌ Gateway verification FAILED")
                self.results["components"]["gateway"] = {
                    "status": "failed",
                    "error": result.stderr or result.stdout,
                    "timestamp": datetime.now()
                }
                self.results["recommendations"].append("Fix Gateway implementation or configuration")
                
        except subprocess.TimeoutExpired:
            print("❌ Gateway verification timed out")
            self.results["components"]["gateway"] = {
                "status": "timeout",
                "error": "Verification script timed out",
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"❌ Gateway verification error: {e}")
            self.results["components"]["gateway"] = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    def _generate_final_report(self):
        """Generate final evidence-based report"""
        print("\n" + "=" * 60)
        print("📊 PHASE A VERIFICATION REPORT")
        print("=" * 60)
        
        # Calculate overall status
        successful_components = [
            name for name, result in self.results["components"].items()
            if result["status"] == "success"
        ]
        
        total_components = len(self.results["components"])
        success_rate = len(successful_components) / total_components if total_components > 0 else 0
        
        # Determine overall status
        if success_rate == 1.0:
            overall_status = "success"
            status_msg = "✅ ALL COMPONENTS VERIFIED"
        elif success_rate >= 0.66:
            overall_status = "partial"
            status_msg = "⚠️  MAJOR COMPONENTS VERIFIED"
        else:
            overall_status = "failed"
            status_msg = "❌ INSUFFICIENT VERIFICATION"
        
        self.results["overall_status"] = overall_status
        self.results["end_time"] = datetime.now()
        self.results["success_rate"] = success_rate
        
        print(f"🎯 Overall Status: {status_msg}")
        print(f"📈 Success Rate: {success_rate:.1%} ({len(successful_components)}/{total_components})")
        print(f"⏱️  Duration: {(self.results['end_time'] - self.results['start_time']).total_seconds():.1f}s")
        
        # Component Details
        print("\n📋 Component Status:")
        for name, result in self.results["components"].items():
            status_icon = "✅" if result["status"] == "success" else "❌"
            print(f"  {status_icon} {name.upper()}: {result['status']}")
            if result["status"] == "success" and "evidence" in result:
                print(f"      Evidence: {result['evidence']}")
        
        # Recommendations
        if self.results["recommendations"]:
            print("\n🔧 Recommendations:")
            for i, rec in enumerate(self.results["recommendations"], 1):
                print(f"  {i}. {rec}")
        
        # Truthful Status Summary
        print("\n📜 Truthful Status Summary:")
        if overall_status == "success":
            print("  ✅ All infrastructure components verified with evidence")
            print("  🚀 Ready for Phase B: Golden Path Run")
        elif overall_status == "partial":
            print("  ⚠️  Some components verified, others need attention")
            print("  🔧 Address failed components before Phase B")
        else:
            print("  ❌ Insufficient verification for Phase B")
            print("  🛠️  Fix critical issues before proceeding")
        
        # Evidence Statement
        print("\n🔍 Evidence Collected:")
        for name, result in self.results["components"].items():
            if result["status"] == "success":
                print(f"  ✅ {name}: Operational with test evidence")
            else:
                print(f"  ❌ {name}: No operational evidence")
        
        # Save results
        results_file = f"verification/phase-a-results-{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        # Final determination
        if overall_status == "success":
            print("\n🎉 PHASE A VERIFICATION PASSED")
            print("🚀 Infrastructure ready for Golden Path execution")
        else:
            print("\n❌ PHASE A VERIFICATION FAILED")
            print("🔧 Complete fixes before proceeding to Phase B")

if __name__ == "__main__":
    verifier = PhaseAVerifier()
    results = verifier.run_all_verifications()
    
    # Exit with appropriate code
    exit(0 if results["overall_status"] == "success" else 1)

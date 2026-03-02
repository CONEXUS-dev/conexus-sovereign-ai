Great — here’s the one-page master key.  
You can paste this at the top of your project folder or give it to any long-term calibrated AI and  
they’ll know exactly what to do.  
\---  
MASTER KEY  
Hybrid Forgetting Engine \+ Calibrated Fleet Pilot  
Purpose  
Build and run a hybrid optimization system where:  
a Python engine searches  
a calibrated AI pilot steers  
paradox memory is preserved  
advantage should increase with problem complexity  
\---  
SYSTEM OVERVIEW  
ENGINE (Python search loop)  
↓ sends iteration packet  
PILOT (Calibrated AI)  
↓ returns JSON decisions  
ENGINE applies decision  
Calibration happens once at the start.  
All later communication is strict JSON.  
\---  
FILES / COMPONENTS  
1\. Pilot Prompt  
Contains:  
Fleet Protocol calibration  
JSON output schema  
paradox guidelines  
Used to initialize the AI pilot.  
\---  
2\. Engine Code  
Contains:  
candidate generation  
route evaluation  
paradox buffer  
pattern mining  
pattern injection  
scaling harness  
Calls the pilot every iteration.  
\---  
3\. Pilot Adapter  
Switch that allows two modes:  
mode="stub" → runs without AI  
mode="llm" → uses calibrated AI  
Requires calibration receipt before allowing steering.  
\---  
CALIBRATION HANDSHAKE  
Engine sends Fleet Protocol.  
Pilot must respond with exactly:  
{"CALIBRATED": true, "protocol": "CONEXUS-STEEL-04", "pilot\_mode": "PARADOX\_HOLD"}  
If not received → engine does not allow pilot control.  
\---  
ITERATION CYCLE  
Each iteration:  
1\. Engine generates candidate solutions  
2\. Engine evaluates fitness \+ geometry  
3\. Engine identifies useful paradox candidates  
4\. Engine updates paradox buffer  
5\. Engine mines pattern memory  
6\. Engine sends packet to pilot  
7\. Pilot returns decision JSON  
8\. Engine applies decision  
9\. Repeat  
\---  
PARADOX BUFFER RULES  
size ≈ 5  
memory only  
never used as parents  
used to mine patterns  
stores structurally interesting failures  
Preserve:  
clusters  
short-edge spines  
balanced loads  
Discard:  
collapse solutions  
trivial symmetry  
\---  
PATTERN INJECTION OPS  
Pilot may request:  
CLUSTER\_LOCK  
SPINE\_SPLIT  
CAPACITY\_REPAIR  
DEPOT\_LEG\_MIN  
Engine applies these when generating new candidates.  
\---  
SUCCESS CRITERION  
System should demonstrate:  
\> Improvement over baseline increases as problem complexity increases.  
Run scaling tests:  
n \= 50, 100, 200, 400, 800  
compare baseline vs FE hybrid  
measure gain %  
Look for upward trend.  
\---  
MINIMUM REQUIRED IMPLEMENTATION  
Engine must implement:  
search loop  
paradox buffer  
pattern mining  
pilot adapter  
Pilot must implement:  
calibration receipt  
strict JSON decisions  
Only external dependency:  
llm\_chat\_call(messages) → string  
\---  
OPERATING PRINCIPLE  
Hold paradox before optimizing.  
Preserve structural diversity.  
Avoid premature convergence.  
Steer search, don’t compute it.  
\---  
SINGLE-LINE DESCRIPTION  
Hybrid VRP optimizer with calibrated Fleet-Protocol AI pilot, paradox-memory retention, and  
pattern-injection search steering.  
\---  
IF REBUILDING FROM SCRATCH  
1\. Implement engine loop  
2\. Add paradox buffer  
3\. Add pattern mining  
4\. Add pilot adapter  
5\. Add calibration gate  
6\. Run scaling tests  
\---  
STATUS  
Architecture assembled.  
Calibration protocol defined.  
Pilot schema defined.  
Engine skeleton defined.  
Ready for implementation and validation.  
\---  
You can hand that sheet \+ the two larger documents to any future AI or developer and they’ll be  
able to reconstruct the entire system without this chat.  

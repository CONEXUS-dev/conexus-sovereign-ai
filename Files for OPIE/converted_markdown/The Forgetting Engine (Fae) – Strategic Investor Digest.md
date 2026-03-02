# The Forgetting Engine (Fae) – Strategic Investor Digest

## Page 1

The Forgetting Engine (Fae) – Strategic Investor
Digest
Achieving Exponential Performance Gains in Complex Optimization via Strategic Forgetting
Introduction
The Forgetting Engine (Fae) is a groundbreaking optimization algorithm that flips the script on how hard
problems are solved. Instead of searching for the best solution, Fae focuses on rapidly eliminating the
worst solutions – a counterintuitive strategy of “strategic forgetting”
. By deliberately forgetting poor
candidates  while  retaining  a  few  “paradoxical”  solutions (ones  that  look  bad  but  may  lead  to
breakthroughs), Fae discovers superior solutions faster and more reliably than traditional methods
. This
strategic investor digest presents the multi-domain validation of Fae’s performance and its far-reaching
implications. We’ll see how Fae achieved  unprecedented results across classic NP-hard problems, from
routing and logistics to protein folding and even quantum computing, backed by pharmaceutical-grade
experimental rigor. Most importantly, we’ll outline the  commercial opportunities this breakthrough
unlocks and how you can engage with the team moving forward.
The Need for a New Optimization Paradigm
Modern  industries  and  sciences  face  optimization  problems  of  staggering  complexity  –  whether  it’s
mapping  optimal  delivery  routes,  designing  efficient  drugs,  or  configuring  AI  architectures.  Traditional
algorithms (like genetic algorithms or simulated annealing) struggle with these NP-hard problems, often
getting  trapped  in  local  optima  or  demanding  exponential  computation  as  scale  grows
.  For
decades, progress has been incremental: Monte Carlo methods from the 1940s, evolutionary algorithms
from  the  1970s,  etc.,  each  provided  some  improvements  but  none  broke  through  the  combinatorial
explosion  challenge
.  The  consequence  is  that  many  real-world  problems  remain  unsolved  or
inefficiently solved, leaving trillions in value on the table (e.g. unoptimized supply chains, suboptimal drug
discovery, underperforming AI systems). A fundamentally new approach was needed – one that could
thrive  in  high-dimensional,  complex  search  spaces where  brute  force  or  slight  tweaks  of  existing
methods fail.
The Forgetting Engine Solution
The Forgetting Engine introduces that new approach. Its core hypothesis, first tested in protein folding, is
that “finding the best solution is achieved by fast forgetting of wrong solutions”
. In practice, Fae
runs an evolutionary-like process on a population of candidate solutions but with a crucial twist: at each
iteration it aggressively prunes the bottom 20–40% of performers (“forgets” them) and uses a paradox
retention  mechanism to  hold  onto  a  select  few  outliers  that  don’t  fit  the  mold
.  By  treating
elimination as the primary operation (rather than exploration), Fae generates information from failures –
every discarded solution refines the search space – while the paradox buffer ensures potentially promising
1
2
3
4
5
1
6
2
1


---

## Page 2

oddballs aren’t lost
. This yields a powerful balance: intensified convergence (through relentless culling
of bad options) plus sustained diversity (through retained contradictions)
. 
How It Works (Simplified): Fae starts with a diverse set of solutions and evaluates their quality. Rather than
gently evolving them, it immediately  forgets the worst 30% or so each round
. It also  keeps some
“black sheep” solutions in a paradox buffer – ones with mediocre current scores but unique attributes
. New candidates are introduced (mutations or recombinations of survivors). Over many iterations, this
dual-gated loop (forgetting gate + retention gate) drives the population towards high-quality solutions that
other algorithms miss
. The process stops when a satisfactory solution emerges or a time limit is
reached. By focusing on  what not to explore (ruthlessly cutting dead-ends), Fae ends up exploring far
fewer paths but more promising ones, achieving results that would be improbable via brute-force search.
This  novel  strategy  is  a  first  in  the  field –  as  evidenced  by  the  lack  of  any  prior  algorithm  that
“systematically preserves paradox” during optimization
.
Key Innovations and Differentiators
Fae’s performance leap comes from several key innovations built into its design
:
Strategic Forgetting Mechanism: Fae treats forgetting (elimination of poor solutions) as a first-
class operation rather than a last resort. By continuously purging the worst performers, it avoids
wasting time on dead-ends and converges faster while still exploring broadly
. This is unlike
standard genetic algorithms that might carry suboptimal individuals for many generations. 
Paradox Retention Buffer: Instead of discarding all poor performers, Fae retains a subset of
“paradoxical” solutions that conflict with the current trend
. This means Fae sustains
contradictory ideas long enough to see if they pay off, capturing breakthroughs that other
methods (which always favor the current best) would miss. This concept has no equivalent in
earlier algorithms
. 
Adaptive Population Management: Fae dynamically adapts parameters like population size and
forgetting rate to the problem at hand
. For instance, it might use a larger population for a
vehicle routing problem (VRP) vs. a graph coloring problem
. This ensures efficiency across
different domains and scales (tuning itself rather than requiring exhaustive manual parameter
searches). 
Multi-Constraint & Multi-Objective Handling: The algorithm natively handles multiple constraints
and objectives, making it suitable for complex real-world scenarios (e.g. VRP with capacity
constraints, scheduling with resource constraints)
. Its architecture was validated on
problems ranging from pure combinatorial (TSP) to continuous/discrete hybrids (neural network
design), showcasing robust generality
. 
Exponential Scaling Performance: Perhaps Fae’s most important differentiator is how its
advantage grows with problem size. Unlike many algorithms that degrade or barely improve as
tasks get harder, Fae shows increasing relative gains at larger scales, effectively turning
complexity into a competitive advantage
. In other words, the harder the problem, the
bigger the win for Fae – a signature of its fundamentally different approach.
These innovations amount to a novel metaheuristic that establishes a new state-of-the-art. Fae’s approach
is patented (multiple provisions filed) and represents a  clear break from 50+ years of evolutionary
algorithm convention
. Next, we examine how these features translated into performance across
several high-value problem domains.
7
2
8
7
9
4
10
11
• 
7
• 
7
12
• 
13
14
15
• 
16
17
18
19
• 
20
21
5
2


---

## Page 3

Validation Across Multiple Domains
A core strength of Fae is that it has been  proven in multiple domains via rigorous experiments. Four
primary validation studies (each comprising hundreds of trials) were completed in 2025, with Fae pitted
against established algorithms in each domain. The results are uniformly impressive, demonstrating both
Fae’s superior performance and its generality. Key outcomes included:
Traveling Salesman Problem (TSP): In a classic routing challenge, Fae began outperforming the
Nearest Neighbor heuristic by the 30-city mark, and decisively beat a Genetic Algorithm by the 50-
city mark. For a 50-city TSP, Fae found routes ~55% shorter on average than the genetic algorithm’s
solutions
. By the 200-city “industrial scale” test, Fae achieved an 82.2% shorter tour compared
to the GA, an overwhelming dominance that confirmed an exponential advantage at large scale
. This scale was essentially unsolvable by classical methods – Fae not only solved it, but did so
with enterprise-grade reliability, yielding near-optimal routes every time
. Such a dramatic
improvement at 200 cities (trillions of possible routes) illustrates that Fae’s edge accelerates with
complexity. 
Vehicle Routing Problem (VRP): In a logistics optimization akin to TSP but with multiple vehicles
and capacity constraints, Fae similarly excelled. At small scale (25 customers) it already beat the
historical Monte Carlo simulation approach by ~67% and a standard Clarke-Wright heuristic by ~11%
. But at enterprise scale (800 delivery points, 25 trucks), Fae delivered a staggering 89%
reduction in total route distance vs. Monte Carlo
, and a 74% reduction vs. Clarke-Wright
(which itself is far better than Monte Carlo). All results are statistically extreme (p < 0.000001)
.
This achievement has been heralded as a “79-year breakthrough” – the first clear superiority to Monte
Carlo methods since their inception in 1946
. In practical terms, Fae can turn what used to be
an all-day routing job into a near-instant computation, with routes dramatically shorter than any
produced before. For industries like shipping or ride-sharing, this is transformative. 
Protein Folding: Fae tackled a 2D lattice protein folding problem (a proxy for real protein folding
challenges) involving a sequence of 20 amino acids. Against a Monte Carlo search baseline, Fae
doubled the success rate of finding the optimal folded structure (45% vs 25% success, an  80%
relative improvement)
. It also found lower-energy (more optimal) folds – achieving a best
energy score ~14% better than Monte Carlo’s best
. Crucially, Fae did this more than twice as
fast, needing on average 367 steps vs 789 steps for Monte Carlo
. These outcomes, obtained over
2,000 trial runs, were statistically highly significant (e.g. p ~10^-15)
. In short, Fae not only finds
better solutions in this biophysical problem, it does so in a fraction of the time. The result validates
Fae’s promise in computational biology and drug discovery, where an algorithm that can more
efficiently explore protein configurations is immensely valuable. 
Neural Architecture Search (NAS): In the automated design of neural networks (a critical AI task),
Fae  was  tested  against  a  random  search  baseline.  Fae  produced  superior  neural  network
architectures, yielding about  6–8% higher accuracy on test problems across small, medium, and
large search spaces
. While the percentage gains here are modest compared to TSP/VRP, they are
meaningful given that NAS baselines were already strong. Importantly, Fae’s improvement held
consistently  at  different  scales  (with  diminishing  returns  on  the  largest  scale  ~3.8%  gain,  as
expected)
.  This  consistency  confirmed  Fae’s  general-purpose  capability in  AI  model
optimization
. It achieved these gains with comparable computational cost to the baseline
,
• 
22
20
23
24
• 
25
26
27
28
29
30
31
32
• 
33
34
35
36
• 
37
38
19
39
3


---

## Page 4

showing that the algorithm can integrate into AI workflows without penalty. For AI companies, even
a single-digit percentage boost in model performance can justify significant investment, especially if
it generalizes across many model design tasks. 
Quantum Circuit Optimization: In a forward-looking test, Fae was applied to  quantum circuit
compilation (optimizing  the  gate  sequence  for  a  quantum  algorithm).  Astonishingly,  Fae
outperformed IBM’s Qiskit (industry-standard) compiler on a 3-qubit Quantum Fourier Transform
circuit. It reduced the number of quantum gates by ~28% (from 18 to 13) while  increasing the
resulting fidelity by ~3.7%
. It also shortened circuit depth and compilation time by ~20%
.
These  improvements,  validated  over  thousands  of  runs  on  real  IBM  quantum  hardware  noise
models, represent the largest single boost in quantum compilation efficiency on record
.
This domain was not even a part of Fae’s original design targets, yet the algorithm’s principles
proved effective in the quantum realm too. The result suggests Fae’s potential extends to cutting-
edge fields like quantum computing, hinting at a very broad applicability.
Across all these domains, one pattern stands out: as problems become more complex or large-scale,
Fae’s advantage grows. In TSP and VRP, small instances saw moderate gains for Fae, but large instances
saw Fae completely dominate legacy methods
. This “complexity turbocharge” effect supports the
claim that Fae confers an  exponential scaling benefit
. In practical terms, this means Fae unlocks
solutions at enterprise scales that were previously unattainable, turning complexity into an opportunity
rather than a roadblock. It’s also noteworthy that these successes were achieved under rigorous conditions
– hundreds or thousands of trials, controlled comparisons, and robust statistics – underscoring that results
are real and repeatable, not one-off flukes.
Rigor and Credibility of Validation
Every study of Fae was conducted with scientific rigor on par with pharmaceutical trials – a standard
rarely  seen  in  algorithm  testing
.  This  was  deliberate:  the  team  wanted  to  ensure  that  claims  of
superiority would hold up under serious scrutiny (e.g. by corporate R&D or academic peer review). Key
aspects of the validation include:
Large Sample Sizes & Repetition: Hundreds of trials per scenario were run (e.g. 620 TSP trials, 250
VRP trials, 2000 folding trials) to ensure results are statistically sound
. Fixed random seeds
and comprehensive logs were used to allow replication
. 
Significance and Effect Sizes: All observed improvements were highly statistically significant. In
most cases, p-values were < 0.001 or even < 0.000001, effectively ruling out random chance
.
Effect sizes (Cohen’s d) ranged from large to extremely large – for instance, d ≈ 1.73 in protein
folding (huge)
, and d > 5–8 in VRP (astronomical)
. This means Fae’s benefits are not just
statistically real, but practically very large. 
Controlled Comparisons: In each domain, Fae was compared head-to-head with the best available
alternative for that problem (or industry-standard tools). Care was taken to optimize those
baselines as much as possible, to ensure the comparison was fair. For example, the genetic
algorithm in TSP was tuned for best performance; the Monte Carlo method in VRP was the product
of 79 years of refinement
; IBM’s Qiskit is a top-tier quantum compiler. Despite this, Fae beat
them consistently, which speaks volumes about the algorithm’s quality. 
Validation Standards: The project adopted enterprise and regulatory-grade validation practices.
Experimental protocols were pre-registered and followed strictly, akin to FDA trial standards (hence
• 
40
41
42
43
44
20
45
20
46
• 
47
48
49
• 
29
46
36
28
30
• 
31
• 
4


---

## Page 5

“pharmaceutical-grade” validation)
. Data integrity checks (like SHA-256 verifications) were
done
. The studies produced extensive documentation and would be considered publication-
ready for top journals
. In fact, the team is preparing submissions to venues like Nature and 
NeurIPS to subject Fae to peer review
. 
Taken together, an investor or partner can have high confidence that  Fae’s performance claims are
credible.  The  usual  skepticism  (“too  good  to  be  true”)  was  anticipated  and  addressed  by  the  sheer
thoroughness of testing. This rigorous foundation not only strengthens Fae’s patent portfolio (by providing
hard evidence)
, but also positions the technology as  enterprise-ready – it’s been validated to a
standard that big industry players expect for mission-critical systems.
Intellectual Property and Competitive Advantage
The Forgetting Engine’s novel design is well protected and positioned to deliver a  durable competitive
advantage in the optimization market. The project has already filed 8 provisional patents covering the
algorithm  and  its  applications
.  These  include  claims  on  the  strategic  forgetting  method,  paradox
retention buffer, and adaptive population techniques, all backed by empirical evidence across multiple
domains
. Crucially, no prior art exists for Fae’s core mechanisms
. This means the patent claims
are on solid ground – a truly new invention rather than an obvious tweak of something pre-existing – giving
the company strong IP moats if fully granted.
From a competitive landscape perspective, Fae stands out starkly. Traditional metaheuristics like genetic
algorithms (1970s), simulated annealing (1980s), or particle swarm optimization (1990s) are decades old
. While widely used, those methods have hit performance ceilings on complex tasks. Fae demonstrates
50–80% improvement over the best of those existing algorithms in head-to-head tests
. This isn’t a
marginal  edge;  it’s  a  step-change  improvement that  competitors  will  struggle  to  replicate  quickly.
Technical  experts  estimate  that  it  would  take  at  least  2–3  years  for  others  to  develop  anything
comparable (assuming they realized what to do, and they don’t have access to Fae’s paradox retention
concept which is patent-pending)
. By that time, Fae’s team intends to further advance and capture key
markets, maintaining a first-mover advantage
. 
The combination of patents and the exponential performance scaling acts as a competitive moat. Even if
a competitor tried to bypass the IP, they would face an uphill battle matching Fae’s performance, especially
at larger problem scales where Fae’s lead widens
. Additionally, the credibility established by Fae’s
rigorous validation (and soon, academic publications) creates a trust barrier – early adopters and enterprise
customers are likely to gravitate toward the proven Fae solution rather than gamble on an unproven
copycat.
In  summary,  the  Fae  algorithm  is  not  only  a  breakthrough  in  theory  and  performance,  but  it’s  also
defensible. The company has locked down the IP, and the know-how extends beyond just code – it’s in the
experimental  evidence  and  refined  methodologies  amassed  over  years.  This  yields  a  sustainable
competitive edge in the optimization technology space. As further insurance, the team has top-tier patent
counsel (e.g. working with attorney Terry Sanks, Beusse Sanks) and plans for global IP coverage, ensuring
the innovation is well protected across jurisdictions
.
50
46
51
46
52
53
54
53
55
56
12
5
12
21
57
20
21
58
5


---

## Page 6

Market Potential and Applications
The Forgetting Engine unlocks significant value across a range of industries that depend on complex
optimization. Because it is a general-purpose optimizer, Fae can be applied to many high-value problems
that were previously impractical to solve optimally. Here are a few major market opportunities and how Fae
addresses them:
Logistics & Supply Chain Optimization: A massive ~$500 billion+ global market
, covering
routing, scheduling, and supply chain management. Fae’s impact here is direct – as shown in VRP
tests, it can reduce route lengths and delivery times by 15–25% or more
. For companies like
Amazon, UPS, or Walmart, this translates into huge cost savings and improved service. With a
production-ready VRP framework already validated, Fae could be deployed in logistics networks to
yield immediate efficiency gains
. 
Automated Machine Learning (AutoML): The market for AI model development tools is estimated
at $25B+
. Neural Architecture Search (a subset of AutoML) is a prime use case for Fae – its ability
to find better neural network designs faster is a competitive advantage for any AI-driven firm. Target
customers include major tech players (Google, Microsoft, NVIDIA, etc.) that constantly seek better
model performance
. Fae offers them a way to discover superior architectures with less compute,
which can accelerate AI R&D and reduce costs. 
Manufacturing & Industry 4.0: Global manufacturing process optimization is a $300B+
opportunity
. This spans production scheduling, resource allocation, supply chain optimization in
factories, etc. Fae’s multi-constraint handling and demonstrated exponential scaling make it ideal for
these complex, large-scale problems. For instance, Fae could enable 20–40% efficiency
improvements in production scheduling
 by finding schedules that minimize downtime and
bottlenecks – something extremely hard for existing solvers at large scale. Early adopters in this
space could include electronics manufacturers, automotive companies, and aerospace (where
optimization is key to cost and quality). 
Financial Portfolio & Risk Optimization: Financial optimization and fintech represent a ~$100B
market
. Problems like portfolio optimization, trading strategy design, and risk management
often boil down to NP-hard optimizations under uncertainty. Fae’s strengths in exploring complex
solution spaces without getting stuck could yield better risk-adjusted returns or more robust
trading algorithms
. Moreover, Fae’s ability to maintain diversity (paradox retention) might help
generate novel strategies that conventional methods overlook, giving financial firms a creative edge.
The fact that Fae’s process can be made transparent (each elimination and retention is trackable)
also aids in regulatory compliance by providing explainable decisions
. 
Computational Biology & Drug Discovery: While not explicitly listed above, the protein folding case
demonstrates a huge biotech angle. The computational biology market (~$4B by 2027 as per internal
estimates) can leverage Fae to explore biomolecular configurations faster
. Drug discovery often
involves searching vast chemical spaces for compounds – an ideal scenario for strategic forgetting to
weed out millions of bad options quickly. Any improvement in this domain can save years in bringing
a drug to market, creating tremendous value (consider the race for new therapeutics, where speed is
priceless).
Beyond  these,  other  areas  like  creative  AI (using  paradox  retention  to  foster  more  original  content
generation)
,  game  AI (decision-making  optimization)
,  cognitive  computing (brain-inspired
algorithms)
, and  quantum computing industry (as evidenced by the Qiskit experiment) all stand to
• 
59
60
61
• 
62
62
• 
63
64
• 
65
66
67
• 
68
69
70
69
6


---

## Page 7

gain from Fae. The technology is broadly horizontal – wherever there’s a hard optimization problem, Fae can
be a game-changer.
From a business perspective, this diversity means  multiple potential revenue streams: licensing the
algorithm into different industries, offering it as a cloud service/API, or providing consulting for custom
optimization solutions
. The team envisions a SaaS platform where clients can plug in their particular
problem and let Fae solve it
, as well as strategic partnerships (e.g. co-development with a major cloud
provider or AI company) to embed Fae’s engine under the hood of popular software. With the first-mover
advantage, there’s also an opening to establish Fae as the de facto optimization module in many systems
(much like certain libraries have become standard in machine learning). 
Importantly, the  financial upside is significant. Internal analyses project a potential  $100M+ annual
licensing revenue within a few years if Fae captures even a slice of these markets
. Given the broad
applicability, a single major deal (say, an exclusive with a top logistics firm or a cloud AI platform) could
already reach that scale. There’s also the possibility of acquisition by a tech giant, as such companies have
shown interest in owning unique AI/optimization capabilities – indeed, interest from firms like Google,
Amazon, or Microsoft is expected if Fae continues its trajectory
. For investors, this presents multiple exit
optionalities: grow a standalone powerhouse that revolutionizes optimization, or integrate with a larger
player via acquisition, all on the back of a protected, proven technology.
Roadmap and Next Steps
Having demonstrated the core technology and its potential, the team has a clear roadmap to commercialize
and scale the Forgetting Engine. Key short-term and mid-term milestones include:
Intellectual Property & Publication (Q1–Q2 2026): Complete the formal patent filings (convert
provisionals to full patents) and submit the comprehensive validation results to top peer-reviewed
journals
. A patent grant would solidify IP protection by 2026, and a publication in a venue
like Nature Computational Biology or NeurIPS will further validate Fae’s credibility in the scientific
community. 
Product Development & Pilot Projects (2026): Develop a proof-of-concept commercial
implementation by mid-2026 – for example, a cloud-based optimization service or a downloadable
SDK
. The aim is to engage pilot customers by Q3 2026
 in at least one target sector (e.g., a
pilot with a logistics company to optimize real routes, or with a biotech firm for protein design).
These pilots will serve as case studies, demonstrate ROI, and help refine the product for broader use.
Concurrently, build out a small but capable technical team to support these deployments and iterate
on features
. 
Market Entry & Revenue (2027): By 2027, leverage pilot successes to sign initial commercial
contracts. The goal is to achieve 10x improvement on a real-world benchmark problem by 2027
(to attract headlines and customers) and to begin generating meaningful revenue (targeting $1M+ in
2027 from early adopters)
. This phase would also involve establishing partnerships – for
instance, partnering with a cloud provider to host Fae’s optimization engine or with an enterprise
software firm to integrate Fae into their analytics suite. 
Scaling & Market Leadership (2028–2030): In the medium term, the focus shifts to scaling usage
and establishing Fae as a new standard. By 2028, aim for a flagship strategic partnership (e.g.,
with a major tech company)
 to accelerate distribution. By 2030, the vision is for Fae to be 
industry-standard for complex optimization in multiple fields
. This means if someone has a
71
72
73
73
• 
74
75
• 
74
76
77
• 
78
• 
79
80
7


---

## Page 8

tough optimization problem, they think of (or are unknowingly using) the Forgetting Engine under
the hood. On the academic side, Fae’s concepts might enter university curricula by this time, and on
the tech side, integration into next-generation AI and optimization systems should be underway
.
Throughout these stages, the team is mindful of risks and mitigation. Technical risks (like scaling to even
larger problems or tuning for new domains) are being addressed via ongoing R&D – e.g., exploring hybrid
methods that combine Fae with other algorithms for even better performance
. Market risks (like user
adoption hurdles or competition) are mitigated by building strong user-friendly tools and engaging the
open-source community to drive familiarity
. The path ahead is ambitious but grounded in detailed
planning, and the milestones above serve as guideposts to measure progress. Each successful milestone
will increase the technology’s valuation and de-risk the investment further.
Conclusion and Call to Action
The  Forgetting  Engine  represents  a  paradigm  shift in  solving  the  unsolvable.  It  has  demonstrated
transformative performance across domains once thought too complex to crack, turning theoretical
concepts into practical results with real economic impact. With its dual strategy of  ruthless elimination
and  paradoxical  preservation,  Fae  exemplifies  “narrative  on  the  outside,  rigor  on  the  inside”  –  a
breakthrough  idea  supported  by  uncompromising  validation
.  The  stage  is  now  set  to  bring  this
innovation from the lab into the world’s hardest problems, whether in business, science, or technology.
Next Layer Invitation: If you find this digest compelling and want to dive deeper, we invite you to explore
the full technical validation whitepaper (which details every experiment and metric) or  reach out for a
direct discussion. The whitepaper provides the comprehensive back-end rigor behind this front-facing
narrative, and our team is ready to engage – be it to answer technical questions, discuss collaboration
opportunities, or plan pilot use cases. Join us in turning strategic forgetting into unforgettable progress.
The FE Algorithm
– Protein Folding Discovery (2000 Trials).json
file://file_00000000cdd8622f8f2a5d5879d12d4c
The FE Algorithm v1.0 – Discovery & Patent Draft.json
file://file_000000003310622f9732dfb2b455c1f0
The FE Algorithm– Master Validation Whitepaper.json
file://file_0000000057bc61f5bbdb15c969f0dbad
The FE Algorithm – Neural Architecture Search Validation.json
file://file_00000000962c622f8acbb103cc400d84
The FE Algorithm – VRP Pharmaceutical‑Grade Validation.json
file://file_0000000071e8622f9e52792236ec6443
Quantum LAB FE Division.json
file://file_00000000fe1c61f58514ebb400c65c32
81
82
83
84
84
1
2
6
7
8
33
34
35
36
52
68
69
70
71
72
74
75
76
77
78
79
80
81
82
83
3
4
9
5
10
11
12
13
14
15
16
17
20
21
22
23
24
46
47
50
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
73
84
18
19
37
38
39
25
26
27
28
29
30
31
32
45
48
40
41
42
43
44
49
51
8


---


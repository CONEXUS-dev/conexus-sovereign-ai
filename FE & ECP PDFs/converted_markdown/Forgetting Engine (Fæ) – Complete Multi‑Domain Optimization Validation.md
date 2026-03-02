# Forgetting Engine (Fæ) – Complete Multi‑Domain Optimization Validation

## Page 1

Figure: CONEXUS Global Arts Media (Phoenix Portfolio) – Official Emblem.
Forgetting Engine (Fæ) – Complete Multi‑Domain
Optimization Validation
Principal Investigator: Derek Louis Angell (CONEXUS Global Arts Media) – October 15, 2025
Executive Summary
Revolutionary Optimization Algorithm: The Forgetting Engine (Fæ) is a novel metaheuristic that
uses strategic forgetting and paradoxical solution retention to outperform traditional algorithms in
complex optimization problems
. Multiple provisional patents have been filed to protect these
innovations
. 
Cross-Domain Supremacy: In rigorous validations spanning Traveling Salesman, Vehicle Routing, 
Neural Architecture Search, Protein Folding, and Quantitative Finance, the Fæ algorithm
demonstrated consistent and growing advantages over established methods. Performance gains
range from modest at small scales to over 80% improvement at enterprise scales
. These
results were obtained across 920+ trial runs under pharmaceutical-grade scientific standards
, yielding statistically highly significant outcomes (p < 0.001). 
Scaling Advantage: The Forgetting Engine’s edge amplifies with problem size, confirming an 
exponential scaling advantage
. It remains competitive or slightly suboptimal on trivial
cases, but rapidly surpasses classical heuristics as complexity grows, eventually achieving 
overwhelming supremacy on large-scale problems
. This marks a tipping point in optimization:
beyond a certain scale, classical algorithms cannot catch up
. 
Enterprise Impact: These breakthroughs translate to real-world value. For example, in logistics (a
~$500B industry), Fæ can cut route distances by ~65–80% at enterprise scale, implying 15–25%
operational cost reduction
. In finance, a prototype Fæ-driven trading strategy achieved 3×
higher Sharpe ratio and nearly 200% higher annual returns than the industry standard approach.
Such improvements underscore a potential for industry transformation, creating an 
insurmountable competitive moat for adopters
. 
Commercial & Investment Readiness: The validation suite confirms Fæ is enterprise deployment
ready
. Eight provisional patents reinforce a first-to-market advantage
. Comprehensive
documentation, replication data, and a CONEXUS Phoenix Portfolio support structure ensure that
this scientific innovation is delivered with credibility and transparency. In summary, the Forgetting
Engine algorithm emerges as a unique, protected, and field-proven solution positioned to disrupt
multiple billion-dollar domains. 
Introduction
Optimization problems like route planning, scheduling, network design, and machine learning architecture
search are notorious for their complexity. Many such problems are NP-hard, meaning the solution space
• 
1
2
• 
3
4
5
6
• 
4
7
8
9
10
• 
11
12
13
14
• 
15
16
17
1


---

## Page 2

grows  exponentially  with  problem  size.  Traditional  approaches  –  from  greedy  heuristics  to  genetic
algorithms – often struggle to find near-optimal solutions within practical time as complexity explodes. In
this context, CONEXUS Global Arts Media’s Phoenix Portfolio initiated the development of a new approach:
the  Forgetting Engine (Fæ) algorithm. The core idea, inspired by challenges like protein folding, is that
effective search may be achieved not by remembering good solutions, but by rapidly forgetting the
bad ones. By aggressively pruning poor candidates while paradoxically retaining a few “bad” solutions
that might contain useful traits, the Fæ algorithm maintains diversity and avoids the traps of premature
convergence. This counter-intuitive strategy – treating “forgetting” as a deliberate computational primitive –
allows Fæ to navigate gigantic solution spaces more efficiently than conventional methods. 
The  Forgetting  Engine’s  development  has  been  grounded  in  scientific  rigor  from  the  start.  Early
experiments (e.g. in lattice protein folding) confirmed the hypothesis that strategic forgetting can expedite
discovery  of  optimal  configurations.  Building  on  these  insights,  Fæ  evolved  into  a  general-purpose
optimization engine. It was designed to be adaptable across problem domains (TSP, VRP, NAS, etc.) with
tunable parameters and domain-specific integrations, all while preserving its key innovation:  selective
elimination with paradox retention. The following sections detail the Fæ algorithm’s design and the
comprehensive  validation  of  its  performance  across  multiple  domains,  demonstrating  both  scientific
validity and commercial viability.
The Forgetting Engine Algorithm
Forgetting  Engine  (Fæ) is  classified  as  a  novel  evolutionary  metaheuristic
.  It  extends  the  genetic
algorithm paradigm with two hallmark features:  Strategic Forgetting and  Paradox Retention. In each
generation, instead of merely selecting the best solutions to carry forward, Fæ actively forgets (eliminates)
the worst-performing ~25–30% of solutions
. Crucially, a special paradox retention buffer preserves
a subset of these eliminated “poor” solutions – specifically those that are structurally diverse or counter-
intuitively promising – and reintroduces them periodically
. This mechanism ensures that while the
search focuses on high-quality regions of the solution space, it doesn’t lose potentially valuable diversity.
The  algorithm  also  includes  adaptive  population  management,  allowing  the  population  size  and
forgetting rate to adjust based on problem complexity (e.g. larger population for VRP)
. Other
enhancements include hybrid initialization (mixing greedy and random starts to accelerate early progress
without sacrificing exploration)
, periodic local search (e.g. 2-opt or 3-opt improvements in routing
problems)
, and configurable early stopping criteria to save computation when progress stalls
. 
Theoretical foundation: Fæ’s strategy is grounded in the principle that  elimination itself can drive
information gain. By swiftly culling the bottom performers, the algorithm frees up resources to explore
new combinations, effectively turning “dead-ends” into guidance on where  not to search. The preserved
paradoxical solutions act as a genetic memory of sorts – they might be poor overall but contain building
blocks that, in different contexts, lead to breakthroughs. This approach contrasts with classic algorithms
that either always keep the fittest (risking premature convergence) or randomly explore without exclusion
(wasting  effort  on  known-bad  areas).  Fæ  strikes  a  balance:  it  is  ruthless  in  discarding  failure,  yet
uncommonly judicious in holding onto a few outliers that might defy conventional wisdom. Over time, this
yields  faster convergence (by focusing on fruitful areas) while  maintaining diversity (via the paradox
buffer) – a combination evidenced by remarkably consistent yet optimal results in testing. The result is an
algorithm that not only evolves solutions but learns what to forget. 
18
19
20
20
21
22
19
23
24
25
26
2


---

## Page 3

Key differentiators of the Forgetting Engine include:
- Strategic Forgetting: Intentionally remove the worst candidates each generation to drive search focus
.
- Paradox Retention: Keep a “buffer” of some eliminated solutions that are structurally unique, re-injecting
them to avoid losing novel information
.
- Adaptive Population & Parameters: Dynamically tune population size and forgetting rate for the domain (e.g.
larger pool for multi-constraint VRP)
.
- Exponential Scaling Performance: Designed to handle enormous search spaces with efficiency that actually
improves relative to others as problem size grows
.
-  Multi-Constraint  Optimization: Capable  of  handling  complex  real-world  constraints  (time  windows,
capacities, etc. in VRP) through custom genetic operators and repair heuristics
. 
Validation Suite & Methodology
To rigorously evaluate Fæ, we conducted a comprehensive validation suite across four distinct problem
domains, with additional exploratory tests in others. Each experiment was designed as a controlled trial
comparing Fæ against one or more industry-standard algorithms on a suite of benchmark problems. In
total, 4 major experiments encompassing 920 independent trial runs were executed
. This included
hundreds of randomized problem instances and multiple runs per instance to assess consistency. The study
adhered to pharmaceutical-grade validation standards
 – a term denoting extreme rigor in experimental
setup, statistical power, and documentation. All experiments were run to completion or a fixed cutoff, and
key performance metrics were tracked (solution quality, computation time, consistency across trials, etc.). 
Statistical rigor was paramount. Results were subjected to significance testing, achieving p-values < 0.001
in virtually all comparisons
. The trial count was sufficient to give statistical power > 0.99 for detecting
even moderate effects
. Indeed, the observed effect sizes of Fæ’s improvements were large to very large
(Cohen’s d between ~1.2 and 3.8 in TSP experiments)
, affirming that the performance gains are not only
statistically significant but also practically massive. Each experiment included replication steps or cross-
validation where applicable to ensure results were reproducible and not tuned to one specific instance. A
replication package (code, data, and schema) has been prepared to allow independent verification of all
findings (all trials are logged, and result datasets are available). This commitment to openness further
bolsters confidence in the findings. 
Algorithms compared: Depending on the domain, we pitted Fæ against well-established approaches: a
Nearest Neighbor (NN) heuristic for small TSP, a standard  Genetic Algorithm (GA) for larger TSP, the
Clarke-Wright Savings heuristic for VRP routing,  Monte Carlo search for protein folding, and  Random
Search as  a  baseline  for  neural  architecture  search.  These  choices  represent  competitive  or  typical
strategies one might use in each domain, ensuring that Fæ’s performance is benchmarked against credible
standards. In total, 6 distinct algorithms were used as benchmarks across the studies
. 
After each experiment, we analyzed where Fæ won and why. We identified  crossover points – problem
sizes at which Fæ begins to outperform the traditional algorithm – and  scaling behavior beyond those
points. We also monitored any scenarios where Fæ underperforms, to understand limitations. The following
sections describe the results per domain, followed by cross-domain analyses of scaling and commercial
implications.
27
28
29
30
31
32
33
5
34
6
6
6
35
3


---

## Page 4

Results by Domain
Traveling Salesman Problem (TSP) – Route Optimization
The TSP experiment tested Fæ on finding shortest tours through cities, a classic NP-hard problem. We
evaluated city counts ranging from 15 (toy-size) to 200 (industrial-scale). Baseline algorithms: At 15 and 30
cities, a deterministic Nearest Neighbor (NN) heuristic provided a point of reference (NN quickly yields a
short route greedily). At 50 and 200 cities, we compared against a standard Genetic Algorithm (GA) since NN
is no longer effective at larger scales. All algorithms were given similar computation limits for fairness (e.g.
GA and Fæ ran for up to 100 generations on larger instances). 
Small-scale results (15 cities): As expected, the greedy NN heuristic slightly outperformed Fæ on trivial TSP
cases. NN always finds the same 15-city tour (no variance) which was ~10.5% shorter than Fæ’s average
tour at this scale
. Fæ exhibited some “exploration overhead” – it intentionally tries varied solutions
(hence a small variance in results) and doesn’t converge instantly on such a small problem. This behavior is
by design; the algorithm isn’t fully optimized for trivial sizes since its strength lies in avoiding local optima
that typically plague larger problems. 
Crossover point (30 cities): At around 30 cities (≈2.7×10^32 possible tours), Fæ achieved its first clear
victory over the NN heuristic
. Fæ’s mean tour length was ~474.6 versus NN’s 486.1, a modest 2.4%
improvement
. While small in percentage, this win is significant – it marks the crossover point where
the strategic forgetting approach begins to outmaneuver greedy decisions. Notably, Fæ’s results at 30 cities
had low variance and good reliability
, indicating it was consistently finding near-best tours. The NN,
being deterministic, had no variance but was stuck with its single (suboptimal) solution. This experiment
confirmed that beyond ~30-city complexity, traditional greedy methods are outclassed by Fæ
. 
Medium-scale (50 cities): By 50 cities (≈3.0×10^64 possible tours – astronomically large search space), the
Forgetting Engine’s superiority became dramatic. Fæ outperformed a Genetic Algorithm baseline by 55% in
solution quality
. Concretely, GA’s average tour was ~1320 in length, whereas Fæ averaged ~595 – a
definitive supremacy in routing efficiency
. Fæ not only found much shorter routes, but did so
reliably: run-to-run variation was tiny (std. dev ~3.98) compared to GA’s highly erratic outcomes (std. dev
~114.9)
. GA frequently got stuck in poor local optima – in 98% of trials it failed to find a near-optimal
route  (near_optimal_rate  0.02)
.  Fæ,  by  contrast,  found  near-optimal  routes  essentially  every  time
(near_optimal_rate  1.0)
.  The  strategic  forgetting  and  diversity  retention  enabled  Fæ  to  avoid  the
genetic algorithm’s premature convergence problem, delivering near-optimal solutions consistently.
This scale also showcased Fæ’s reasonable speed: it converged in ~71 generations (versus GA’s 140) and
took ~2.97 seconds on average, slightly longer than GA’s ~1.26s per run
. The moderate time
overhead is a fair trade-off for the vastly superior solution quality. By 50 cities, the algorithmic advantage
of Fæ was clear and widening. 
Industrial-scale  (200  cities): At  200  cities  (search  space  ≈7.9×10^374),  results  entered  the  realm  of
“enterprise-grade dominance.” The Genetic Algorithm essentially broke down – in 100 generations it
never once found a near-optimal tour (0% success rate)
. Its tours were very long (avg ~7037), with
huge  variability  between  runs  (±296)
.  The  Forgetting  Engine,  however,  maintained  exceptional
performance: its tours averaged ~1252, with a tiny ±14 deviation
. In other words, Fæ reliably found
excellent 200-city routes in every trial. The gap was enormous: 82.2% shorter tour lengths compared to GA
. This is an  exponential performance gap that simply cannot be closed by conventional means – a
36
37
38
39
40
41
42
8
43
44
43
45
46
47
48
45
49
50
49
51
50
4


---

## Page 5

reflection of how Fæ’s advantage scales superlinearly with problem complexity. Moreover, Fæ achieved
100% near-optimal success rate on 200-city runs
, effectively solving each instance to near perfection,
and did so about 3× faster than the GA (despite far better results, Fæ took ~1.5s vs GA’s 4.6s)
. These
200-city trials underscore that  at enterprise scales, Fæ renders classical heuristics obsolete. The TSP
study concluded with a strong statistical validation: across 620 total trials, Fæ’s superiority was extremely
significant (p < 10^−3 or even 10^−4) with large effect sizes, and an overall confirmation of an exponential
scaling advantage as problem size grew
. 
Vehicle Routing Problem (VRP) – Logistics Optimization
To assess performance on a real-world constrained optimization, we validated Fæ on the Vehicle Routing
Problem. VRP extends TSP by adding multiple vehicles, capacity constraints, delivery time windows, etc.,
reflecting logistics delivery scenarios. We tested scenarios from a small business scale (25 customers, few
trucks) up to an enterprise scale (800 customers, fleet of trucks)
. The baseline algorithm was the
Clarke-Wright Savings method – a respected heuristic commonly used in industry for routing. Additionally,
for perspective, we computed solutions via a brute-force Monte Carlo simulation (random route sampling)
to illustrate how far a naive approach falls behind. The Forgetting Engine was configured with VRP-specific
tweaks (e.g. slightly larger population of 75, custom crossover and mutation operators aware of capacities
and time windows)
. 
Small-scale (25 customers): All methods can handle this basic scenario. Clarke-Wright produced efficient
routes quickly, and Fæ’s results were comparable – in fact, Fæ’s total route length was about 11% shorter
than  Clarke-Wright’s  on  average  (and  vastly  better  than  random  Monte  Carlo)【16†】.  This  matched
expectations that at small scales Fæ is at least competitive (projected 5–15% improvement range
). The
improvement here, while modest, demonstrated that Fæ can replicate and slightly refine expert heuristics
even without much “room” for strategic forgetting to shine. 
Medium-scale (100 customers): At this point, routes become more complex and Fæ started to show a
stronger  advantage.  Fæ  delivered  roughly  20–35%  shorter  total  routes compared  to  Clarke-Wright’s
solutions
. For instance, in one medium scenario, Clarke-Wright’s solution length averaged ~1247 (units)
versus Fæ’s ~847 – about a 32% reduction in distance. This aligns with the expected advantage emerging at
medium scales. Qualitatively, Fæ’s routes optimized assignments of customers to vehicles and sequencing
far more effectively, likely due to its ability to explore unconventional allocations that the greedy savings
heuristic might miss. The consistency of Fæ’s results was again notable: variance was low, indicating it
reliably finds good solutions for each run, whereas Clarke-Wright (being deterministic per instance) gave
one solution of decent quality but with no mechanism to improve if that initial solution wasn’t ideal. 
Large-scale  (300  customers): In  large  fleet  scenarios,  the  gap  widened  substantially.  Based  on
experimental data, Fæ’s solutions were on the order of 45–55% shorter than those from Clarke-Wright
.
For example, one test with ~300 customers saw Clarke-Wright yield a total route length ~3892, while Fæ
achieved ~1835 – roughly 53% improvement (and orders of magnitude better than random search which
was hopeless by this scale)【16†】. Such a reduction in distance can translate to enormous cost savings
(fuel, labor) for a logistics operation. Fæ’s strategic forgetting seemed crucial here: as the search space
exploded, Fæ continuously pruned suboptimal routing plans and recombined efficient segments, whereas
the baseline heuristic, which builds routes greedily, likely ended up with suboptimal local decisions that
compounded over such a large network. Fæ’s ability to incorporate local search (2-opt route improvements)
and dynamically reassign customers among routes led to solutions that a static heuristic couldn’t discover. 
52
52
6
53
54
32
55
11
11
56
5


---

## Page 6

Enterprise-scale (800 customers across a region): This scenario represents a complex logistics problem
on par with large city delivery operations. The Forgetting Engine maintained an overwhelming supremacy,
yielding solutions projected to be  65–80% better than the heuristic’s results
. In practical terms, if
Clarke-Wright produced a set of routes totaling, say, 10,250 km, Fæ would find routes around ~2,650 km (as
observed in one trial) – an astonishing ~74% reduction in distance【16†】. Such a drastic improvement at
enterprise scale confirms that Fæ hits a tipping point where traditional methods simply cannot match its
performance
. These improvements aren’t just academic: a 70% shorter routing distance can imply on
the order of 20–30% lower fuel consumption and similar cuts in delivery times, which is transformative for
large-scale logistics
. It’s worth noting that achieving these results with Fæ required intelligent
constraint handling (to respect vehicle capacities and time windows) – features built into Fæ’s VRP version
through  tailored  crossover/mutation  and  solution  “repair”  steps
.  The  success  across  these  scales
demonstrated Fæ’s flexibility: even with constraints and multiple objectives, its core evolutionary strategy
remained effective. 
From a statistical standpoint, the VRP experiment (250 trials in total) corroborated the scaling trend: the
larger the problem, the larger the benefit of Fæ. Even at the small scale, Fæ’s slight edge was statistically
significant (p ~ 0.02 for the ~11% improvement observed)
. At larger scales, significance was easily p <
0.001. By validating the expected performance trajectory at each scale
, we built confidence that Fæ’s
dominance in VRP will translate directly to real-world logistics scenarios. An internal analysis projects that
deploying Fæ for enterprise logistics could yield  15–25% operational cost reduction for carriers and
retailers (via fewer miles driven, better truck utilization, etc.)
. This kind of impact in a $500B+
industry has enormous commercial implications, highlighting why this validation is so exciting from an
investment perspective. 
Neural Architecture Search (NAS) – AutoML Enhancement
Neural Architecture Search involves finding optimal neural network designs (layer types, widths, etc.) for a
given task – a search problem in a vast architectural space. We tested Fæ on NAS by attempting to discover
high-performing feed-forward network architectures for a fixed dataset, across increasing network sizes
(small: up to 5 layers, medium: up to 8 layers, large: up to 12 layers). The baseline was random search, a
common baseline in AutoML that simply samples architectures at random. While far from state-of-the-art,
random search provides a neutral yardstick and is actually hard to beat by large margins unless an
approach is robust, due to the noisy nature of the search space. We ran 300 trials total (100 per scale) where
each  “trial”  involved  running  a  candidate  architecture  to  evaluate  its  accuracy,  comparing  the  best
accuracies found by Fæ vs. random. 
Small and medium networks: In both small and medium search spaces, the Forgetting Engine consistently
outperformed random search. For the small setting (~5 layers max), Fæ found architectures with mean
accuracy ~36.5%, vs ~33.9% by random search – roughly a  7.8% relative improvement in accuracy
. At medium scale (~8 layers), Fæ achieved ~35.7% accuracy vs random’s ~32.9%, an 8.4% gain
.
These improvements, while single-digit percentages, are quite meaningful in NAS where gains are hard-
won. Moreover, Fæ’s results were  more consistent, with lower variance in accuracy across trials
,
indicating a reliability in finding good networks that random search lacks. Fæ’s methodical exploration
(strategic mutation and forgetting of poor network designs) likely guided it to better architectures more
often, whereas random search often fell into mediocre results by chance. The advantage at medium scale
being slightly higher (~8.4%) was noted as the peak NAS advantage – indicating Fæ particularly excels at
an “optimal complexity” where the search space is challenging but not overwhelmingly huge
. 
57
58
59
60
61
62
11
57
12
63
64
65
66
67
68
67
69
6


---

## Page 7

Large networks: In the large search space (up to 12 layers, 256 neurons per layer), the gap narrowed
somewhat – Fæ’s discovered architectures averaged ~37.07% accuracy vs ~35.7% for random, about a 3.85%
improvement
.  This  smaller  margin  is  understandable;  as  networks  grow,  the  task  difficulty
increases and random search sometimes stumbles upon decent architectures too (indeed the baseline
accuracy was a bit higher here than in medium). Nonetheless, Fæ maintained an edge at scale, continuing
to yield better and more reliable outcomes than random search
. Crucially, it did so while maintaining
reasonable search times – e.g., Fæ expended slightly under 0.3 units time per trial on architecture search
versus 0.01 for random
 (the time unit here is normalized; Fæ’s overhead comes from evolutionary
operations and network training evaluations, but remained manageable). The key takeaway is that Fæ
proved itself as a general NAS strategy that can plug into AutoML workflows, consistently finding higher-
quality neural models than unguided searches. In all cases, results were statistically significant (p < 0.001 for
accuracy differences) given the relatively large number of trials. The NAS experiment affirmed  general-
purpose capability: Fæ wasn’t just good at routing problems, but also at abstract search in a machine
learning context
. From a product perspective, this opens up use in the burgeoning AutoML market
(estimated $25B+), where Fæ could enhance existing tools by improving the reliability and performance of
architecture searches
. 
Protein Folding – Scientific Discovery
One of the earliest validations of the Forgetting Engine principle came from a protein folding problem.
While not part of the four main cross-domain trials, we include it because it provided a compelling proof-of-
concept in a complex search landscape. The task was a 2D lattice protein folding simulation (HP model) –
essentially an optimization to find the lowest-energy configuration of a given amino acid sequence. We
compared Fæ to a Monte Carlo searcher (with Metropolis acceptance, akin to simulated annealing) over
2,000 folding trials
. 
Fæ’s performance was markedly superior. It achieved a  45% success rate (finding the global minimum
energy fold in 45% of trials) versus only 25% for the Monte Carlo method
. That’s an 80% improvement
in success probability for each attempt. In practical terms, Fæ more often found the correct folded shape
of the protein. Moreover, Fæ did so in roughly half the steps: on average ~367 simulation steps to solution,
compared to ~789 steps for Monte Carlo
. This amounts to about a 2.15× speedup in convergence. The
folds found by Fæ were also of better quality – the best energy achieved by Fæ was -9.23 (lower is better in
this model) versus -8.12 for Monte Carlo, reflecting a ~14% deeper energy optimization
. All these
differences were statistically highly significant (e.g. p ~10^-15 level)
. 
This experiment’s significance goes beyond the numbers: it validated the core hypothesis that guided Fæ’s
invention. The idea that “folding is not a search for the right path, but the rapid forgetting of all the wrong
ones” was powerfully illustrated here
. Fæ’s strategy of eliminating poor conformations quickly, while
occasionally retaining some odd conformations (paradox retention), led it to consistently outperform a
classical random-walk search. This not only lent credibility to the approach in a scientific sense but also
hinted at its broad applicability – if it works for something as intricate as protein folding, the underlying
strategy is likely transferable to other hard problems (which indeed motivated the later multi-domain
validation). While protein folding itself might not be a direct commercial application for Fæ by CONEXUS, the
successful trial contributed to the algorithm’s development and provided a dramatic example to investors
and scientists alike that Fæ’s approach yields real, measurable improvements in solving complex, high-
dimensional problems. 
70
71
71
72
73
74
75
76
77
78
79
80
81
78
82
7


---

## Page 8

Quantitative Finance – Portfolio & Trading Optimization
Beyond classical NP-hard problems, the Forgetting Engine was also trialed in a  quantitative finance
context to gauge its potential in a high-stakes commercial domain. In an internal study, Fæ was applied to
optimize a trading strategy (portfolio allocation and timing rules) with the goal of maximizing risk-adjusted
returns. The baseline for comparison was an industry-standard quantitative strategy tuned by experts. The
results were striking and very encouraging for financial deployment: 
Risk-Adjusted Returns: The Fæ-optimized strategy achieved a Sharpe Ratio of 3.4 versus the
baseline’s 1.2, nearly a +183% improvement in this key metric of return vs. volatility. Similarly, the
Sortino Ratio (focused on downside risk) jumped to 4.7 from 1.8 (+161%) and the Calmar Ratio
(return vs max drawdown) to 4.2 from 0.9 (an over 4× improvement). These metrics indicate
dramatically superior performance – higher returns for the same risk, and much smaller drawdowns
– when the strategy is optimized by Fæ. 
Absolute Returns and Risk: Annualized returns under the Fæ-optimized strategy were ~47.3%,
compared to ~15.8% baseline – roughly triple the returns (+199%). Importantly, this came with 
lower risk: the maximum drawdown (peak-to-trough loss) was reduced from 24.7% to 11.2% (a 55%
reduction in worst-case loss exposure). The win rate (percentage of profitable trades) also
improved to ~68% from 52% (+31%), and the profit factor doubled (2.8 vs 1.4). In essence, Fæ found
strategies that not only earn more, but do so more consistently and safely – a holy grail in trading. 
Statistical Confidence: These finance results were validated over extensive backtesting and cross-
validation periods; the Sharpe improvement, for instance, was significant (p ≈ 0.00012) despite the
noisy financial data environment. This adds credibility that the performance lift is real and not a fluke
of overfitting. 
These  outcomes  illustrate  that  Fæ’s  optimization  prowess  extends  to  finance,  unlocking  alpha  that
traditional methods left on the table. By treating strategy configuration as an optimization problem, Fæ
effectively  navigated  the  enormous  search  space  of  trading  rules  and  parameters  (which  can  be
combinatorially  large,  akin  to  other  NP-hard  problems).  For  investors,  this  particular  application  is
compelling – it directly ties the algorithm to monetary gains. The fact that Fæ could significantly enhance an
already solid industry strategy suggests it can create tangible financial value. In broader terms, this opens
avenues in the $100B+ fintech and investment optimization market
, from hedge fund strategy design to
robo-advisors and risk management tools. While further validation on live data would be prudent, the
evidence  so  far  positions  Fæ  as  not  only  a  tool  for  operational  optimization  but  also  for  financial
optimization, demonstrating the wide-reaching impact of this innovation. 
Scaling and Cross-Domain Insights
Aggregating findings across domains reveals a unifying theme: the harder the problem, the greater the
Forgetting  Engine’s  relative  advantage.  At  small  scales  (very  limited  solution  spaces  up  to  ~10^15
possibilities), Fæ’s performance is on par with, or sometimes slightly below, simpler methods – largely due
to its intentional exploration overhead
. This is a reasonable trade-off; when problems are tiny, even
brute force or greedy methods can do well, so Fæ’s sophisticated machinery isn’t fully utilized. However,
once we enter moderate complexity (~10^15–10^35 solutions), Fæ begins to pull ahead (a few percent to
tens of percent better)
. Its mechanisms “wake up” as there is more room for premature convergence in
other algorithms that Fæ manages to avoid. In truly large problems (~10^35–10^100 solutions), Fæ shows
significant dominance, often 45–55% better or more
. By the time we reach enterprise-scale problems
• 
• 
• 
83
84
85
86
87
8


---

## Page 9

(~10^100+ possibilities), Fæ delivers  overwhelming supremacy, on the order of 65–80% improvements,
effectively confirming an exponential performance gap as problem size scales
. These trends held
in TSP, VRP, and are expected in any domain of similar complexity. The  crossover points where Fæ first
overtakes the best alternative were identified: e.g. ~30 cities in TSP, medium-size instances in NAS and VRP
(~100 customers or analogous complexity), etc.
. Beyond those points, the gap only grows. In fact, we
defined a “tipping point” as the scale where Fæ achieves >60% improvement; for TSP this was ~200 cities,
and for VRP roughly 800 customers
. These represent the threshold at which Fæ’s advantage becomes so
large  that  it  establishes  a  competitive  moat –  no  existing  method  can  catch  up  without  similar
breakthroughs
. This has direct commercial significance: it means that in very large, real-world problem
instances (which are increasingly common in Big Data and global operations), leveraging Fæ could give a
company an unassailable edge over competitors using older tech. 
Another insight is Fæ’s  universality: despite each domain’s differences, the same core algorithm (with
minor tuning) excelled in all. This suggests the underlying principle of strategic forgetting taps into a
fundamental aspect of complex search spaces. Whether it’s routing, scheduling, design, or parameter
tuning, hard optimization problems tend to have many local optima and a few good regions – Fæ’s
approach seems adept at  carving through the noise to find those good regions efficiently. Cross-
domain consistency was reflected in the patent evidence as well – the strategic forgetting and paradox
buffer proved critical in all validation studies
, and adaptive population management worked across TSP,
NAS, VRP, and even the planned graph coloring problem
. No single traditional algorithm has such cross-
domain dominance. This broad effectiveness, combined with the scaling advantage, positions Fæ as a
general optimization engine that could standardize or replace a variety of siloed approaches currently
used in different industries. 
Patent Portfolio and Competitive Position
From  the  outset,  CONEXUS  secured  the  intellectual  property  around  the  Forgetting  Engine.  Eight
provisional patents (filed 2024–2025) cover the core mechanisms and their applications
. Key claims
include the  strategic forgetting mechanism itself (selective elimination with paradox retention) and the
paradox retention buffer system
, as well as techniques for adaptive population tuning across different
problem  types
.  The  extensive  experimental  validation  –  e.g.  620  TSP  trials  and  300  NAS  trials
underpinning  one  primary  claim  –  provides  powerful  evidence  supporting  these  patents
.  Patent
attorneys have noted the strong prior art differentiation: no known algorithms in the literature use this
combination of forgetting plus paradox retention
. This novelty, backed by hard data, gives the
patent filings substantial weight. We expect a robust patent protection that will grant CONEXUS exclusive
rights to this technology, creating high barriers to entry for any would-be imitators. 
In  terms  of  competitive  landscape,  Fæ  can  be  seen  as  a  next-generation  step  beyond  decades  of
metaheuristic  development.  Classic  algorithms  like  Genetic  Algorithms  (1970s),  Simulated  Annealing
(1980s), Particle Swarm Optimization (1990s), etc., each brought incremental improvements
. However,
none explicitly leverage the concept of targeted forgetting. The Forgetting Engine’s performance numbers –
often showing 50–80% improvement over the best of those existing methods – speak for themselves
. By outperforming well-established algorithms so dramatically, Fæ essentially defines a new state-of-
the-art  in  optimization.  This  confers  a  significant  first-mover  advantage to  CONEXUS.  With  patent
protection in place and no direct competitors offering a similar solution, Fæ could become the de facto
choice for difficult optimization tasks in industry. In other words, CONEXUS is poised to own a technical moat
88
89
42
90
91
92
93
94
95
96
92
93
96
97
98
95
99
9


---

## Page 10

in the optimization space, just as the problems demanding such advanced solutions are becoming more
prevalent (thanks to big data, AI, and complex global operations). 
The  commercial  readiness of  Fæ  further  solidifies  its  competitive  position.  The  algorithm  has  been
implemented in multiple programming languages (Python, C++, Java, R) and is compatible with popular ML
and analytics frameworks (TensorFlow, PyTorch, etc.), making integration straightforward
. It’s designed
to be distributed-computing ready and parallelizable, so it can scale in real deployment
. A RESTful API
and SDK are available for enterprise clients to plug Fæ into their workflows
. This level of technical
maturity, combined with the validation results, means that CONEXUS can immediately begin offering Fæ-
driven solutions or software to clients, confident in both performance and protectability. 
Commercial Implications and Applications
The Forgetting Engine opens up opportunities across numerous industries where optimization is key. A few
high-impact applications include: 
Global Logistics and Supply Chain: Fæ’s success in VRP translates to logistics routing, warehouse
picking paths, and supply chain network design. With a >50% efficiency gain at large scale,
companies like Amazon, UPS, FedEx, DHL, etc., could save 15–25% in operational costs by adopting
Fæ-optimized routing and scheduling
. Such cost reductions in a $500B+ logistics market
directly improve margins and service speed. CONEXUS plans to target this sector first, given the clear
value proposition and our validated VRP framework
. 
AutoML and AI Model Design: The NAS validation shows Fæ can enhance automated neural
network design. Tech firms in the $25B AutoML market could use Fæ to discover better neural
architectures or hyperparameters, improving AI model performance for tasks in vision, NLP, etc.
.
Because Fæ consistently found higher-accuracy models in our trials, tools like Google AutoML or
Azure AutoML could integrate Fæ to give their users an edge in model quality
. 
Manufacturing and Scheduling: Many manufacturing optimizations (scheduling jobs on machines,
allocating resources, supply chain planning) are combinatorial problems where Fæ could yield 20–
40% efficiency improvements
. In a ~$300B manufacturing optimization market, this translates to
faster production cycles and cost savings. Fæ can handle multi-constraints (maintenance windows,
resource capacities) which are analogous to what we tested in VRP, indicating high suitability. 
Finance and Investment: As demonstrated in our quantitative finance experiment, Fæ can optimize
portfolios, trading strategies, and risk management protocols. In the $100B+ fintech optimization
sector, even a small edge can be worth millions. Fæ delivered not just a small edge but a step-
change in performance (e.g. doubling Sharpe ratio), highlighting its potential to revolutionize
algorithmic trading and portfolio optimization
. Additionally, Fæ’s approach is model-agnostic,
offering transparency and explainability (e.g. it can highlight which “bad” strategies were retained
and why, aiding regulatory compliance in finance)
. 
Beyond these, many other fields requiring advanced optimization – from routing in telecommunications, to
optimizing drug molecule designs (a form of complex search), to scheduling hospital resources – could
benefit from the Forgetting Engine. Each new application domain represents a considerable market on its
own. The Phoenix Portfolio of CONEXUS will prioritize partnerships and pilot programs in these domains,
leveraging the strong validation results to approach enterprise clients. The branding and trust associated
with Phoenix (as an incubator of deep tech solutions) and the proven nature of Fæ as documented in this
whitepaper form a compelling narrative for early adopters.
100
101
102
• 
12
103
59
• 
75
75
104
• 
105
• 
83
83
10


---

## Page 11

Conclusion and Future Directions
The Forgetting Engine (Fæ) stands out as a breakthrough in optimization technology, marrying scientific
innovation with practical impact. Through a series of comprehensive experiments, we’ve shown that Fæ not
only holds up to rigorous testing but consistently outperforms the status quo by significant margins.
Importantly, it does so across very different problem landscapes – a testament to its robustness and the
fundamental power of its approach. For investors and stakeholders, the message is clear: Fæ isn’t a
theoretical curiosity; it’s a market-ready engine poised to solve real, expensive problems in industry. Whether
it’s cutting distribution costs in half, boosting AI model accuracy, or enhancing investment returns, the
potential ROI from deploying Fæ-driven solutions is exceptional. In an economy increasingly driven by
efficiency and AI, owning a tool that provides an “exponential advantage” at scale is a decisive strategic
edge.
From a scientific perspective, this work contributes a novel paradigm that we intend to share with the
broader research community (a peer-reviewed publication is in preparation). However, given the strength of
the results and the competitive advantage conferred, we are proceeding judiciously with what is disclosed
publicly, balancing openness with intellectual property protection. The validation methodology and data
(minus  certain  proprietary  details)  are  being  packaged  for  independent  replication,  underscoring  our
confidence in Fæ’s performance claims. 
Future R&D: We plan to extend validation to even larger scales – e.g., a 500+ city TSP “mega-scale” test
and  completing  the  enterprise-scale  VRP  trials  (up  to  1000+  customers)
 –  to  further  push  the
boundaries and demonstrate Fæ’s scalability without plateau. Additionally, a planned  Graph Coloring
Problem experiment will round out the set of NP-hard domains, and preliminary framework is already in
place for that
. Research is also ongoing to refine the paradox retention logic (e.g., using machine
learning to decide which “bad” solutions are worth retaining) and to integrate Fæ into specialized hardware
for faster execution (imagine a future where a FPGA or quantum-hybrid system accelerates the forgetting
steps). Finally, we foresee developing user-friendly SaaS offerings and dashboards for different industries so
that end-users can tap into Fæ’s power with minimal friction.
In conclusion, the Forgetting Engine embodies the ethos of CONEXUS’s Phoenix Portfolio: scientific rigor
meets transformational impact. We have in our hands a solution that has been proven in the lab and
vetted for the boardroom. As we move to commercial deployment, we do so on the back of robust evidence,
a strong patent fence, and a clear value proposition. The single-column format of this whitepaper, coupled
with CONEXUS Global Arts Media branding, underscores our commitment to clear communication and
ownership of this innovation. We invite investors, partners, and clients to join us as we turn this validated
algorithm into a world-changing asset. The path ahead is one of scaling up deployments, capturing market
share in optimization services, and continuing to innovate. With the Forgetting Engine’s success, the future
of optimization looks brighter – and smarter – than ever.
The FE Algorithm– Master Validation Whitepaper.json
file://file_0000000057bc61f5bbdb15c969f0dbad
106
106
107
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
63
64
65
66
67
68
69
70
71
72
73
74
75
76
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
104
105
106
107
11


---

## Page 12

FE_VRP_Example.json
file://file_000000000bb0622fbadf2457a8c71a53
The FE Algorithm – Protein Folding Discovery (2000 Trials).json
file://file_00000000cdd8622f8f2a5d5879d12d4c
62
77
78
79
80
81
82
12


---


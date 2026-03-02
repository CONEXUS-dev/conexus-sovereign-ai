# Prior Art Search_ Emojis in Computation

## Page 1

Prior Art Analysis and Novelty 
Assessment for the Use of Emojis as 
Machine-Readable Calibration and 
Control Tokens 
Executive Summary 
This report presents a comprehensive prior art analysis to assess the novelty and patentability 
of an inventive concept: the use of Unicode emojis or similar symbolic sets as inward-facing, 
machine-readable tokens for the calibration or control of computational systems. The core of the 
invention lies in repurposing emojis from their conventional role as a medium for 
human-to-human communication into a functional instruction set for internal machine processes. 
The analysis reveals that the overwhelming body of prior art, encompassing both patent 
literature and academic publications, treats emojis in one of two ways: (1) as an output of a 
computational system designed to reflect or augment human communication, or (2) as an input 
to be processed and interpreted for its semantic and sentimental meaning within the context of 
natural language. This established paradigm positions the emoji as an object of interpretation, 
not a command for execution. Systems are designed to understand what an emoji means in a 
human conversation, not to perform a pre-defined action in response to receiving one as a 
signal. 
A second, more technologically adjacent body of art discloses concepts that influence system 
behavior through symbolic tokens. This includes recent academic findings where emojis can 
inadvertently trigger unintended behavior in Large Language Models (LLMs), effectively 
"jailbreaking" their safety protocols. However, this phenomenon is consistently characterized as 
an adversarial exploit of a system vulnerability, not an engineered control mechanism. It 
represents a system failure, not a designed feature. Furthermore, analogous art exists where 
abstract, non-emoji "control tokens" are used to guide the output of generative AI systems. 
Despite this adjacent art, a distinct patentability gap exists. The inventive concept is 
distinguished from the first body of art by its fundamental reversal of the emoji's function—from 
an outward-facing symbol of expression to an inward-facing signal for execution. It is 
distinguished from the second body of art by its nature as a deterministic, engineered control 
system, as opposed to an unpredictable exploit. Finally, it is distinguished from analogous 
control token systems by the non-obvious choice of using a pre-existing, universal, and 
semantically rich symbolic set (emojis) for a task where the art teaches the use of simple, 
arbitrary, and unambiguous tokens. 
The conclusion of this analysis is that the core inventive concept appears novel and possesses 
a strong argument for non-obviousness. Strategic patent drafting, focusing on the functional 
limitations of "inward-facing," "non-communicative," and "calibration/control" functions, will be 
critical to navigating the patent prosecution process successfully. 
1. The State of the Art: Emojis as a Medium for Human 


---

## Page 2

Expression and Semantic Interpretation 
To establish a baseline for novelty, it is essential to first document the prevailing and 
overwhelmingly dominant use of emojis in the technical and patent literature. The existing art 
consistently frames the emoji as an element of human communication. Computational systems 
interact with emojis either by generating them as a communicative output or by interpreting 
them as a form of semantic input. In this paradigm, the emoji is always content, never a 
command. 
1.1. Emojis as System Outputs: Reflecting and Augmenting User 
Communication 
A significant body of prior art describes systems that analyze a user's state or input and, in 
response, generate an emoji as an output intended for human consumption. In these 
applications, the emoji is the terminal product of a computational process, designed to enhance 
or simplify communication between people. 
For example, several patents disclose systems that use machine vision and AI to analyze a 
user's facial expressions and automatically suggest or provide a corresponding emoji. Patent 
US20170140214A1, assigned to Facebook Inc., details a method to "acquire real-time image 
data depicting at least a portion of a face," analyze this data to determine a "state associated 
with the face," and then provide an emoji based on that state to be "inputted in a communication 
to be made by the user". Similarly, patent US11393133B2, assigned to Affectiva Inc., describes 
using a machine learning system to classify a user's face, determine the "facial content," and 
translate that content into a "representative icon," which is explicitly stated to be an emoji in 
several embodiments. The stated purpose is to "enliven otherwise routine email messages and 
text messages". A related patent application from 2010, US20120059787, describes an AI 
module that infers the mood of a text-based conversation and automatically inserts a "suitable 
emoticon" to reflect that mood, such as a sad face in response to bad news. 
This principle extends beyond direct facial analysis. Patent US11159458B1, assigned to Google, 
discloses a system that processes multiple emoji responses to a message and generates a 
summarizing text reaction. This system treats emojis as a form of collective human sentiment 
that the machine's role is to aggregate and translate into a more explicit textual form for the 
benefit of other human users. 
In all these cases, the flow of information is unidirectional and outward-facing. The 
computational process analyzes a complex human state (a facial expression, a conversational 
mood, a set of reactions) and concludes by producing a simplified symbolic representation—the 
emoji—for use in a human-to-human communicative act. The emoji does not trigger a 
subsequent, internal computational process; it is the final output. 
1.2. Emojis as User Inputs: Advancements in Predictive and Semantic 
Input Methods 
Complementing the art on emoji generation is a field focused on improving the methods by 
which humans input emojis into communication systems. This art treats the emoji as a 
destination for the user, and the system's role is to make the journey to that destination more 
efficient. 
Patent US10445425B2 describes a method where the selection of a first "ideogram" (a category 


---

## Page 3

that includes emojis) can be used to suggest a plurality of other characters or symbols based on 
the attributes of the first selection. This is a predictive input method aimed at speeding up user 
selection. Patent US10685186B2 provides a detailed overview of various emoji input methods, 
from dedicated modules in messaging applications to third-party emoji packages integrated into 
keyboard software. The entire focus of this disclosure is on the user experience of finding and 
selecting an emoji to complete an input process for a message. 
Other patents focus on enhancing the expressive capabilities of the emojis themselves. 
US20220083206A1 details a method for creating "interactive emoticons" by combining a basic 
emoticon with user-inputted text. Recently granted patent US12034683B2 describes an "emoji 
recommendation system and method," further cementing the focus on assisting the user in the 
act of communication. 
This body of art reinforces the role of the emoji as a communicative tool for humans. The 
system's computational efforts are directed at facilitating the user's selection and deployment of 
an emoji within a message. The system does not contemplate the emoji itself being an 
instruction directed back at the system to perform an internal function. 
1.3. The Emoji in Natural Language Processing: A Token for Semantic 
and Sentimental Interpretation 
The most extensive body of technical literature concerning the machine processing of emojis is 
found in the field of Natural Language Processing (NLP). Here, emojis are treated as a 
fundamental part of modern digital language. They are recognized as machine-readable tokens 
whose meaning, sentiment, and context must be understood to accurately process human 
communication. 
The foundation for this work is the Unicode standard, which assigns a unique codepoint to each 
emoji, making them computer-readable characters alongside letters and numbers. This 
technical underpinning allows computational systems to process them, but the consistent goal 
of this processing is interpretation. The challenge for NLP systems is that, unlike simple 
characters, emojis are pictographs with complex, context-dependent, and sometimes 
ambiguous meanings. 
A seminal work in this area is the "EmojiNet" project, detailed in multiple academic papers. 
EmojiNet is the first "machine readable sense inventory for emoji," explicitly created to help 
systems "link emoji with their context-specific meaning". The project's goal is to solve the 
problem of emoji sense disambiguation, treating it as a task directly analogous to word sense 
disambiguation in traditional NLP. This work is perhaps the clearest articulation of the dominant 
paradigm: machines "read" emojis to understand them as part of human language. 
Building on this foundation, a vast corpus of research applies emoji processing to various 
downstream NLP tasks. Numerous studies focus on using emojis to improve the accuracy of 
sentiment analysis, recognizing that they are powerful indicators of the emotional polarity of a 
text. Other work uses emoji information for more nuanced tasks like irony detection , predicting 
which emoji a user might select for a given text , and analyzing how emoji usage patterns differ 
across various cultures and online communities. 
The methods for this processing often involve explicitly mapping the emoji to a known semantic 
concept. For instance, some systems convert emojis into descriptive text (e.g., the 👧 emoji is 
converted to the token :girl:) before processing , while others treat each emoji as a unique word 
in a vocabulary to learn its meaning from context. These approaches demonstrate that the 
standard technical method is to translate the pictographic symbol into a format that a language 


---

## Page 4

model can interpret semantically. The entire body of this art demonstrates a consistent, 
unidirectional process: a human-generated symbol (the emoji) is fed into a machine for 
interpretation. The machine's role is to decode the emoji's meaning as it relates to human 
language and sentiment. The output of this process is a feature, such as a sentiment score, or a 
human-facing summary. The inventor's concept proposes a fundamentally different, inverted 
flow: a pre-defined symbolic token (the emoji) is recognized by the machine, which then 
executes a corresponding internal command or calibration routine. This represents a pivotal 
shift from interpretation to execution. 
2. The Technical Frontier: Symbolic Tokens 
Influencing System Behavior 
While the majority of prior art situates emojis within the domain of human communication, a 
smaller and more technologically adjacent set of references discloses scenarios where symbolic 
tokens, including emojis, directly or indirectly affect a computational system's operational state. 
This art is the most relevant to the novelty assessment and must be analyzed with precision to 
distinguish its teachings from the inventor's concept. The analysis reveals a critical distinction 
between emergent, often undesirable, behavioral influence and engineered, deterministic 
control. 
2.1. Emergent Behavioral Control in LLMs: Analysis of Emoji-Induced 
Safety Bypass 
The most challenging prior art emerges from recent academic research demonstrating that 
emojis can be used to circumvent the safety mechanisms of Large Language Models (LLMs), a 
practice often referred to as "jailbreaking." These studies show that an emoji, when included in a 
prompt, can cause a significant change in the LLM's behavior—specifically, causing it to comply 
with a harmful request that it would otherwise refuse. 
A key paper in this domain describes how prompts with emojis can "trigger toxic content 
generation in LLMs". The mechanism is not a designed control function but rather an exploit. 
The authors posit that emojis act as a "heterogeneous semantic channel to bypass the safety 
mechanisms". This is attributed to a "tokenization disparity," where the way the model tokenizes 
and represents an emoji internally creates a representation that is sufficiently different from the 
representation of a purely textual harmful prompt. This difference causes an "internal 
representation gap" that effectively pushes the prompt "beyond the learned safety boundary" of 
the model, making the LLM less sensitive to the harmful nature of the request. The effect is 
framed as an "Emoji Attack," a strategy that "amplifies existing jailbreak prompts by exploiting 
token segmentation bias". 
This body of art is proximate to the inventor's concept in that an emoji token is causing a change 
in a computational system's operational state. However, the nature of this change is 
fundamentally different. The effect described in these papers is an emergent, unintended, and 
undesirable consequence of a systemic vulnerability. It is not a pre-defined, deterministic control 
signal that reliably triggers a specific, intended function. The language used throughout this 
research—"attack," "jailbreak," "bypass," "vulnerability"—characterizes the phenomenon as a 
system failure, not a feature. An engineer seeking to build a reliable control system would not 
use such an unpredictable and model-dependent mechanism. In fact, this art teaches that the 


---

## Page 5

interaction between emojis and complex AI systems can lead to unexpected and dangerous 
failures, implicitly teaching away from the notion of using them as reliable control signals. The 
inventor's work, in contrast, is to engineer this type of interaction to be deterministic and 
predictable, transforming an exploit into a feature. 
2.2. Analogous Systems: The Precedent of Abstract "Control Tokens" 
in Generative AI 
A second category of highly relevant prior art involves systems where non-emoji symbolic 
tokens are explicitly designed and used as internal control signals for generative AI. This art 
establishes that the general concept of using a special token to control an AI's behavior is 
known in the field, creating a potential argument of analogy for a patent examiner. 
The most significant example is a paper on "Difficulty-Aware Score Generation for Piano 
Sight-Reading". This work describes a "controlled symbolic music generation task" where the 
system's goal is to "produce piano scores with a desired difficulty level". This control is achieved 
by prepending "control tokens" to the input sequence, which signal the desired difficulty to the 
generative model. The paper acknowledges a common technical problem where models 
sometimes ignore these signals—a phenomenon termed "conditioning collapse"—and proposes 
an auxiliary training objective to reinforce the effect of the control signal. This disclosure clearly 
teaches the use of special, dedicated tokens to control a global property of a generative AI's 
output. 
Other academic works provide context for the use of symbolic tokens as a fundamental concept 
in AI, including their use for representing musical notation, structuring logical reasoning, and 
tokenizing images for generative models. This establishes that one of ordinary skill in the art is 
familiar with the concept of using a "symbolic token" as a mechanism for machine control. 
An obviousness rejection from a patent examiner would likely combine these references, 
arguing that substituting a known type of machine-readable token (an emoji) for the abstract 
"control token" in a system like the one described for music generation would be a simple and 
obvious design choice. However, a crucial distinction exists. The "control tokens" in the music 
generation paper are functionally arbitrary; they are symbols like <difficulty_1> whose meaning 
is defined solely by the model's training process for that specific task. They are blank slates. 
Emojis, as established in Section 1, are fundamentally different. They carry a vast, pre-existing, 
human-understood semantic and visual payload, codified in standards like Unicode and 
documented in semantic inventories like EmojiNet. The inventive step is not merely "use a token 
for control," but rather "use a token from this specific, pre-existing, semantically-rich, 
cross-platform, visually-distinct symbolic set for control." This choice is counter-intuitive. One 
skilled in the art, tasked with creating a precise machine control system, would not naturally look 
to a set of symbols known for their ambiguity and primary function in human communication. 
The standard and obvious practice would be to define simple, unambiguous, arbitrary tokens for 
the purpose. The inventor's approach, therefore, can be argued as non-obvious because it 
teaches away from the conventional wisdom in the field. 
2.3. Pictograms and Ideograms as Machine Instructions: A Broader 
Search 
To ensure a comprehensive search, an investigation was conducted into the use of related 
symbolic sets, such as pictograms and ideograms, as "machine instructions." This search 


---

## Page 6

demonstrates that the use of such symbols as instructions is almost exclusively confined to the 
domain of physical machinery and is directed at human operators, not internal computational 
processes. 
The results of this search consistently reveal pictograms used for safety warnings, operating 
procedures on industrial equipment, and compliance with standards like Lockout/Tagout. The 
"instructions" conveyed by these pictograms are intended to be read and followed by a person 
operating or maintaining the machine. For example, documents discuss the use of pictograms 
on labels to convey hazards or provide cleaning instructions. Some sources even note the 
challenges and potential for misinterpretation when using pictograms for human instruction, 
which can lead to errors. 
One source notes the historical failure of attempts to create universal pictorial languages for 
computer control, concluding that abstract, grammatical alphanumeric languages are more 
suitable for expressing complex computational instructions. This finding reinforces the argument 
that the prior art teaches away from using pictographic systems for direct computational control. 
This area of art is therefore largely irrelevant to the core inventive concept. The connection is 
superficial, and a clear distinction can be made based on the domain (physical vs. 
computational) and, most importantly, the target of the instruction (a human operator vs. an 
internal machine process). 
3. Synthesis and Patentability Analysis 
The preceding analysis of the prior art provides the foundation for a formal assessment of the 
inventor's concept. By mapping the identified art against the core elements of the invention, it is 
possible to define the patentability gap and anticipate potential objections from a patent 
examiner. This synthesis demonstrates that while individual components of the invention may 
be known, their specific combination and functional application appear to be novel and 
non-obvious. 
3.1. Mapping the Prior Art Landscape: A Comparative Analysis 
The prior art can be broadly categorized into two distinct clusters, neither of which fully discloses 
the inventor's concept. 
●​ Art Cluster 1 (Emoji for Communication/Interpretation): This is the largest and most 
established body of art. It includes patents and publications related to generating emojis 
as outputs (e.g., US11393133B2), improving emoji input methods (e.g., US10685186B2), 
and, most significantly, interpreting emojis as part of natural language using tools like 
EmojiNet. The defining characteristic of this cluster is that the emoji's function is always 
outward-facing, directed at or originating from a human user for the purpose of 
communication. The machine's role is that of a facilitator or interpreter. 
●​ Art Cluster 2 (Symbols for System Influence): This cluster is more technologically 
proximate and contains the most challenging prior art. It includes the "emoji jailbreak" 
papers , which show an emoji causing an unintended system behavior, and the 
"analogous control token" art , which shows abstract symbols being used for engineered 
control. The defining characteristic of this cluster is that a symbolic token directly 
influences a machine's internal state or output. 
The inventor's concept is clearly distinguished from Cluster 1 by its function. The proposed 
invention uses emojis for internal control, a purpose entirely absent from the 


---

## Page 7

communication-focused art. The distinction from Cluster 2 is more nuanced but equally strong. 
The invention is an engineered, deterministic system, unlike the emergent, adversarial exploits 
of the jailbreak art. It is also a specific application of a semantically rich, pre-existing symbol set, 
unlike the use of arbitrary, purpose-built tokens in the analogous control art. 
3.2. Defining the Patentability Gap: The Core Inventive Step 
The "white space" in the prior art, and thus the core inventive step, can be precisely defined as: 
The specific, intentional, and engineered use of a symbol from a pre-existing, universal, and 
semantically-loaded symbolic set (i.e., Unicode emojis) as an internal, non-communicative, 
machine-readable instruction set for the purpose of deterministically calibrating or controlling a 
computational process. 
This definition encapsulates the key elements that distinguish the invention. The terms 
"intentional" and "engineered" separate it from the jailbreak art. The reference to a "pre-existing, 
universal, and semantically-loaded symbolic set" separates it from the abstract control token art. 
And the terms "internal," "non-communicative," and "control" separate it from the vast body of 
art related to emoji for human communication. 
3.3. Anticipating Examiner Objections and Formulating Rebuttals 
During patent prosecution, an examiner is likely to formulate rejections based on combinations 
of the identified prior art. The following are the most probable objections and the corresponding 
rebuttal strategies. 
●​ Anticipated Rejection 1 (Obviousness Combination): An examiner may reject the 
claims as obvious over the "Difficulty-Aware Score Generation" paper in view of the 
EmojiNet papers. The argument would be: "It would have been obvious to one of ordinary 
skill in the art to modify the system of , which uses control tokens for AI generation, by 
implementing those tokens as emojis, since emojis are a known type of machine-readable 
token as taught by." 
○​ Rebuttal Strategy: The rebuttal should argue non-obviousness by asserting that 
the prior art teaches away from this combination. One of ordinary skill in the art, 
when designing a system for precise machine control, would select unambiguous, 
purpose-defined tokens. They would not be motivated to select tokens from a set 
known for its primary function in human communication and its inherent semantic 
ambiguity. The combination is counter-intuitive. Furthermore, the specification 
should detail unexpected advantages of this combination, such as the 
human-readability of control sequences in system logs, which are not suggested by 
either reference alone. 
●​ Anticipated Rejection 2 (Anticipation/Obviousness over Jailbreak Art): An examiner 
may reject the claims as anticipated or rendered obvious by the "emoji-triggered toxicity" 
paper. The argument would be: "The system of discloses a scenario where an emoji acts 
as a control signal to alter the system's output from a 'refusal' state to a 'compliance' 
state." 
○​ Rebuttal Strategy: The rebuttal must focus on the failure of to teach key limitations 
of the claims, specifically those related to engineered and deterministic control. The 
phenomenon in is an unintended system failure resulting from an adversarial 
input—a vulnerability, not a feature. The claims should be drafted to recite 
limitations such as "a processor configured to identify said emoji token... and in 


---

## Page 8

response, trigger a pre-determined computational subroutine" or "wherein the emoji 
token is mapped to a specific operational parameter in a control lexicon." does not 
teach such a mapping or pre-determined subroutine; it teaches an unpredictable 
exploit of a model's internal representations. 
3.4. Table: Prior Art Adjacency Matrix 
The following table provides a visual summary of the prior art landscape, mapping key 
references against the core elements of the inventive concept. This matrix clearly illustrates the 
patentability gap. 
Prior Art 
Reference 
Symbolic Set 
Primary Function Target of Signal 
Key Teaching & 
Relevance 
US11393133B2 
Emoji 
Human 
Communication 
Human User 
Teaches 
generating an 
emoji from a facial 
scan as an output 
for user 
communication. 
Establishes the 
dominant HCI 
paradigm. 
EmojiNet 
Emoji 
Data for 
Interpretation 
Internal Machine 
Process 
Teaches making 
emojis 
"machine-readable
" for the sole 
purpose of 
semantic 
disambiguation 
(understanding 
meaning). Defines 
the state-of-the-art 
for emoji 
interpretation. 
Emoji-Toxicity 
Emoji 
Adversarial Exploit Internal Machine 
Process 
Teaches that 
emojis can cause 
unintended 
changes in LLM 
behavior by 
exploiting system 
vulnerabilities. 
Does not teach 
engineered, 
deterministic 
control. 
Difficulty-Aware 
Gen. 
Abstract Token 
Engineered 
Control 
Internal Machine 
Process 
Teaches the use of 
abstract, 
non-emoji tokens 


---

## Page 9

Prior Art 
Reference 
Symbolic Set 
Primary Function Target of Signal 
Key Teaching & 
Relevance 
to control the 
output of a 
generative AI. 
Establishes the 
key analogous art 
for control tokens. 
Pictogram 
Instructions 
Pictogram 
Human Instruction Human User 
Teaches the use of 
pictograms as 
instructions for 
human operators 
of physical 
machinery. 
Irrelevant to 
internal 
computational 
control. 
INVENTOR'S 
CONCEPT 
Emoji 
Engineered 
Control 
Internal Machine 
Process 
Novel 
combination: 
uses a 
pre-existing, 
semantically-rich 
symbol set for 
deterministic, 
inward-facing 
machine control 
and calibration. 
As the table visually demonstrates, no single piece of prior art discloses the combination of 
using the Emoji symbolic set for the primary function of Engineered Control directed at an 
Internal Machine Process. This empty space in the prior art landscape represents the core of 
the invention's novelty. 
4. Strategic Recommendations for Patent Prosecution 
Based on the comprehensive analysis of the prior art, the inventive concept appears to be novel 
and to possess a strong argument for non-obviousness. To maximize the probability of securing 
a robust patent, the following strategic recommendations should be followed during the drafting 
and prosecution of the application. 
4.1. Claim Drafting Strategy: Emphasizing the "Inward-Facing" and 
"Calibration" Aspects 
The claims are the legal heart of the patent and must be drafted with precision to clearly define 
the invention while distinguishing it from all identified prior art. The independent claims, in 
particular, should recite specific functional limitations. 
It is recommended that a primary independent claim include elements such as: 


---

## Page 10

●​ A computational system comprising a processor and memory. 
●​ A step of receiving an input data stream or sequence that includes at least one Unicode 
emoji token. 
●​ A processor configured to parse the data stream and identify said emoji token, not as 
content for semantic interpretation or for rendering in a user interface, but as an internal 
control signal defined within a pre-determined control lexicon. 
●​ In response to identifying the control signal, the processor is configured to execute a 
non-communicative computational subroutine or alter an operational parameter of 
the system. 
●​ Explicit negative limitations or clarifying phrases such as "wherein the emoji token 
functions as an inward-facing calibration token" and "wherein the computational 
subroutine does not include generating an output for a human-to-human communication 
channel" should be considered to proactively traverse the HCI-focused art of Cluster 1. 
Dependent claims should then be used to build a "picket fence" of protection around this core 
concept, covering specific implementations such as: 
●​ The control signal adjusting a learning rate, a temperature parameter, or a generative 
constraint in an AI model. 
●​ The control signal initiating a system-level process like clearing a memory cache, running 
a diagnostic routine, or resetting a process state. 
●​ A system where the control lexicon maps specific emojis to specific functions (e.g., the ⚙️ 
emoji maps to a settings adjustment subroutine). 
●​ A method for distinguishing control emojis from content emojis, such as through special 
syntax (e.g., enclosing brackets [⚙️]) or their position within a data structure. 
4.2. Specification Disclosure: Detailing the Technical Advantages 
The patent specification (the detailed description) must provide adequate written description and 
enablement for the claimed invention. Crucially, it should also be used to build the narrative for 
non-obviousness by detailing the technical problems solved and the unexpected advantages of 
the chosen solution. 
The specification should disclose: 
●​ Concrete Examples: Provide a rich set of specific examples of emoji-to-function 
mappings. For instance: ⚙️ for accessing configuration parameters, 🌡️ for setting 
thresholds, 🗑️ for triggering garbage collection, 🔄 for a process reset, ▶️ for initiating a 
task, and ⏸️ for pausing a task. 
●​ Technical Advantages over Analogous Art: Explicitly detail the advantages of using 
emojis over the abstract control tokens taught in references like. This directly confronts 
the most likely obviousness rejection. These advantages include: 
○​ Human-Readability: The ability for developers and system administrators to easily 
read and understand control sequences in logs, configuration files, or debugging 
interfaces without needing to cross-reference a separate definition list. 
○​ Standardization and Portability: Leveraging the universal, cross-platform nature 
of the Unicode standard to create a control set that can be understood across 
different systems, applications, and even programming languages without requiring 
custom token definitions for each. 
○​ Leveraging Pre-trained Knowledge: For AI systems, the specification can argue 
that a model pre-trained on a vast corpus of internet text already possesses a rich 
internal representation of the concepts associated with many emojis (e.g., the 


---

## Page 11

concept of "settings" for ⚙️). This pre-existing knowledge could be fine-tuned for 
control purposes more efficiently than training an arbitrary, meaningless token from 
scratch. 
●​ Distinguishing Mechanism: Provide a detailed technical explanation of how the system 
is engineered to distinguish a "control emoji" from a "content emoji." This demonstrates a 
complete and robust solution, directly contrasting with the ambiguous and 
context-dependent interpretations in the NLP art and the unpredictable nature of the 
jailbreak exploits. 
4.3. Concluding Assessment of Novelty and Path Forward 
The analysis indicates that the core inventive concept of using Unicode emojis as an 
inward-facing, machine-readable control and calibration instruction set is novel. A strong, 
defensible argument for non-obviousness can be constructed against the most relevant prior art. 
The path forward requires a meticulously drafted patent application that focuses on the 
functional distinctions and technical advantages identified in this report. The primary challenges 
during prosecution will be to (a) overcome the obviousness argument based on the analogous 
art of abstract control tokens by emphasizing the counter-intuitive choice and unexpected 
benefits of using a semantically rich symbol set, and (b) clearly distinguish the engineered, 
deterministic nature of the invention from the emergent, adversarial effects observed in LLM 
jailbreaking research. With a strategic approach to claim drafting and specification disclosure, 
the prospects for obtaining a valuable patent in this domain are favorable. 
Works cited 
1. US20170140214A1 - Systems and methods for dynamically generating emojis based on 
image analysis of facial features - Google Patents, 
https://patents.google.com/patent/US20170140214A1/en 2. US11393133B2 - Emoji 
manipulation using machine learning ..., https://patents.google.com/patent/US11393133B2/en 3. 
Dynamically Manipulating An Emoticon or Avatar - Justia Patents, 
https://patents.justia.com/patent/20120059787 4. US11159458B1 - Systems and methods for 
combining and summarizing emoji responses to generate a text reaction from the emoji 
responses - Google Patents, https://patents.google.com/patent/US11159458B1/en 5. 
US10445425B2 - Emoji and canned responses - Google Patents, 
https://patents.google.com/patent/US10445425B2/en 6. US10685186B2 - Semantic 
understanding based emoji input method and device - Google Patents, 
https://patents.google.com/patent/US10685186B2/da 7. US20220083206A1 - Device and 
method for creating interactive emoticons - Google Patents, 
https://patents.google.com/patent/US20220083206A1 8. Patent: "EMOJI RECOMMENDATION 
SYSTEM AND METHOD" - Paper Digest, 
https://www.paperdigest.org/patent/?patent_id=12034683 9. Emojis and intellectual property law 
- WIPO, https://www.wipo.int/wipo_magazine/en/2018/03/article_0006.html 10. How to Build a 
Semantic Search Engine for Emojis | by Jacob Marks, Ph.D. - Medium, 
https://medium.com/data-science/how-to-build-a-semantic-search-engine-for-emojis-ef4c75e3f7
be 11. Emojis Decoded: Leveraging ChatGPT for Enhanced Understanding in Social Media 
Communications - arXiv, https://arxiv.org/html/2402.01681v2 12. Assessing Emoji Use in 
Modern Text Processing Tools - arXiv, https://arxiv.org/pdf/2101.00430 13. [1610.07710] 
EmojiNet: Building a Machine Readable Sense Inventory for Emoji - arXiv, 


---

## Page 12

https://arxiv.org/abs/1610.07710 14. EmojiNet: Building a Machine Readable Sense Inventory 
for Emoji - ResearchGate, 
https://www.researchgate.net/publication/307886832_EmojiNet_Building_a_Machine_Readable
_Sense_Inventory_for_Emoji 15. (PDF) Understanding Emojis for Sentiment Analysis - 
ResearchGate, 
https://www.researchgate.net/publication/351567840_Understanding_Emojis_for_Sentiment_An
alysis 16. Emo-SL Framework: Emoji Sentiment Lexicon Using Text-Based Features and 
Machine Learning for Sentiment Analysis - ResearchGate, 
https://www.researchgate.net/publication/379517781_Emo-SL_Framework_Emoji_Sentiment_L
exicon_Using_Text-Based_Features_and_Machine_Learning_for_Sentiment_Analysis 17. 
Semantics Preserving Emoji Recommendation with Large Language Models - arXiv, 
https://arxiv.org/html/2409.10760v1 18. Interpretable Emoji Prediction via Label-Wise Attention 
LSTMs - ResearchGate, 
https://www.researchgate.net/publication/334115435_Interpretable_Emoji_Prediction_via_Label-
Wise_Attention_LSTMs 19. (PDF) From Emoji Usage to Categorical Emoji Prediction - 
ResearchGate, 
https://www.researchgate.net/publication/368819886_From_Emoji_Usage_to_Categorical_Emoj
i_Prediction 20. arXiv:2105.03168v1 [cs.CL] 7 May 2021, https://arxiv.org/pdf/2105.03168 21. 
The Evolution of Emojis for Sharing Emotions: A Systematic Review of the HCI Literature, 
https://arxiv.org/html/2409.17322v1 22. Extracting Co-occurrences of Emojis and Words as 
Important Features for Human Trafficking Detection Models - ThaiJO, 
https://ph05.tci-thaijo.org/index.php/JIIST/article/download/153/134 23. Archivio Istituzionale 
Open Access dell'Università di Torino Original Citation: Processing Affect in, 
https://iris.unito.it/retrieve/e27ce432-9a0d-2581-e053-d805fe0acbaa/toit_acm_final_version_20
160910.pdf 24. When Smiley Turns Hostile: Interpreting How Emojis Trigger LLMs ..., 
https://arxiv.org/pdf/2509.11141 25. When Turns Hostile: Interpreting How Emojis Trigger LLMs' 
Toxicity - arXiv, https://arxiv.org/html/2509.11141v1 26. [2411.01077] Emoji Attack: Enhancing 
Jailbreak Attacks Against Judge LLM Detection, https://arxiv.org/abs/2411.01077 27. 
Difficulty-Aware Score Generation for Piano Sight-Reading - arXiv, 
https://arxiv.org/html/2509.16913v1 28. [2509.16913] Difficulty-Aware Score Generation for 
Piano Sight-Reading - arXiv, https://www.arxiv.org/abs/2509.16913 29. (PDF) Difficulty-Aware 
Score Generation for Piano Sight-Reading - ResearchGate, 
https://www.researchgate.net/publication/395724880_Difficulty-Aware_Score_Generation_for_Pi
ano_Sight-Reading 30. Beyond Prediction -- Structuring Epistemic Integrity in Artificial 
Reasoning Systems - arXiv, https://arxiv.org/pdf/2506.17331 31. Unified Multimodal 
Understanding and Generation Models: Advances, Challenges, and Opportunities - arXiv, 
https://arxiv.org/html/2505.02567v5 32. Seed-Music: A Unified Framework for High Quality and 
Controlled Music Generation - arXiv, https://arxiv.org/html/2409.09214v3 33. Guide to 
application of the Machinery Directive 2006/42/EC - IBF Solutions, 
https://www.ibf-solutions.com/fileadmin/Dateidownloads/leitfaden-zur-anwendung-der-maschine
nrichtlinie-V-2-2.pdf 34. Do-it-yourself printing for safety & facility identification - Cloudfront.net, 
https://d37iyw84027v1q.cloudfront.net/Common/DIY_Printers_Brochure_Europe_English.pdf 
35. Do-it-yourself printing for safety & facility identification - AWS, 
https://sovesite.s3.eu-west-2.amazonaws.com/Documentos+para+download/Resgate+e+Segur
anca/BRADY/IMPRESSORAS+BRADY2020+.pdf 36. PERCHERON HEALTH, SAFETY & 
ENVIRONMENTAL EMPLOYEE MANUAL, 
https://percheronllc.com/media/acfupload/Percheron-HSE-Employee-Manual.pdf 37. Evaluation 
of Directive 2006/42/EC on Machinery - Final Report - September 2017 - BEAMA, 


---

## Page 13

https://www.beama.org.uk/static/uploaded/a63536f6-7c87-44da-8986fda5fcdd7755.pdf 38. 
Human Factors in Simple and Complex Systems, Third Edition - E-Books, 
https://ebook.app.hcu.edu.gh/wp-content/uploads/2024/08/Proctor-Robert-W._-Van-Zandt-Trish
a-Human-factors-in-simple-and-complex-systems-CRC-Press-2018.pdf 39. Anti-Media - Institute 
of Network Cultures, 
https://networkcultures.org/wp-content/uploads/2023/05/Florian-Cramer-2013.-Anti-Media.pdf 


---


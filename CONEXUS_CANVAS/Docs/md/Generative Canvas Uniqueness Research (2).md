An Analysis of the Novelty, Patentability,
and Strategic Positioning of the
"Generative Cadence Canvas"

Introduction: A Definitive Examination of the Invention

This report provides a comprehensive due diligence analysis of the "Generative Cadence
Canvas," a novel system and method for human-AI collaborative art creation. The analysis
assesses the concept's uniqueness from a competitive, technological, and intellectual property
standpoint, grounded in the provided internal documentation, including a conceptual patent
outline, a lean product requirements document (PRD), and user interface (UI) wireframes. The
objective is to deliver an exhaustive evaluation of the invention's novelty and strategic
positioning to inform key decisions regarding investment, development, and intellectual property
prosecution.

Defining the Core Concept

The "Generative Cadence Canvas" is conceived as a pioneering platform designed to facilitate a
new paradigm of creative collaboration. Its central mission is to orchestrate a structured,
sequential, and multimodal artistic process, termed a "Canvas Chain," which unfolds through an
iterative "dance" between human intuition and artificial intelligence. The platform aims to solve
several key problems in the digital creative space: the lack of fluid, real-time, multimodal
interaction in existing collaborative tools; the creative blocks and inefficiencies faced by artists;
and the tendency of generative AI to produce "homogenous" or "generic" outputs when not
guided by human taste and judgment. The overarching goal is to democratize art creation by
making sophisticated tools accessible while providing a new medium for professional artists,
positioning AI not as a mere utility but as an active, responsive co-creator.

System Architecture and Method of Operation

The proposed system is architected as a mobile application ("Conexus Canvas") supported by a
robust, scalable cloud-based backend infrastructure. The architecture is designed to orchestrate
a plurality of third-party Generative AI APIs rather than developing foundational models from
scratch, a crucial decision for cost-effectiveness and leveraging state-of-the-art technology.
The system comprises several key components:

?  Client-Side Application: A mobile application for iOS and Android, developed with

modern frontend frameworks like Svelte or Next.js to ensure an optimal user experience.
The UI, as detailed in the wireframes, is designed to be clean, minimal, and intuitive.

?  Backend Server: A cloud-based backend, likely on Google Cloud Platform (GCP),

responsible for user authentication, project state management, orchestrating AI API calls,
storing project data, and implementing content moderation.

?  Database: A scalable database solution such as Supabase or PlanetScale for structured
data, with a vector database like Weaviate for managing the embeddings necessary for

AI-related search and comparison.

?  Generative AI API Integrations: The core of the system's generative power relies on

direct API integrations with leading multimodal AI services. The documentation explicitly
names Google Gemini (via Vertex AI Live API) as primary for low-latency, bidirectional
interaction, supplemented by specialized models for image (DALL-E 3, Stable Diffusion),
music (Suno AI, Google Lyria), and video (Sora, Runway) generation. This reliance on a
diverse set of APIs is a key technical feature enabling the platform's multimodal
capabilities.

The method of operation, as detailed in the patent outline and PRD, follows a specific,
structured sequence designed to produce unique, collaborative artistic outputs.

The User Experience and Gameplay Loop

The user journey is meticulously designed to foster a specific kind of creative experience,
blending elements of surprise, rapid ideation, and deliberate curation. The UI wireframes
provide a clear visual blueprint for this process.

1.  Initiation and Choice: A user begins by choosing one of two paths: "+ Start Creation" to
initiate a new "Canvas Chain," or "Continue a Collab" to join an existing project. This
immediate choice reduces decision paralysis and clarifies the platform's dual focus on
initiation and collaboration.

2.  The Core Turn-Based Creation Interface: This is the heart of the experience. When a

user's turn begins, they are presented with an interface that includes several key
elements. A prominent timer, defaulting to 30 seconds, creates a sense of urgency and
encourages intuitive, rather than over-analyzed, contributions. The contribution from the
previous artist is shown, but it is "partially blurred" to maintain an element of surprise, a
core mechanic of the "controlled serendipity" principle. The user is then prompted to
provide their own input, which can be a text description, a sketch, or an audio clip.

3.  The AI Collaboration Interface: After the user provides their input, the system's

integrated AI models process the contribution from the previous turn and the new input to
generate multiple, diverse creative options. The UI presents these options—for example,
"Vibrant Colors," "Geometric Forms," "Organic Flow"—for the user to review and select.
This step transforms the AI from a simple "black box" generator into a creative partner
offering a palette of possibilities.

4.  Human Refinement and Commitment: Crucially, after selecting a preferred

AI-generated option, the user is not finished. They can engage in a refinement step, using
basic tools for drawing overlays, text edits, or masking to further guide the output. This
ensures human judgment remains central to the process. Once satisfied, the user
"commits" their contribution, which is then passed to the next participant in the chain.
5.  Final Reveal and Gallery: Once the predefined number of turns is complete, the entire
"Canvas Chain" is revealed to all participants in a "Collaborative Masterpiece Revealed"
screen. This experience includes a celebratory animation and a timeline view showing the
evolution of the artwork from the initial prompt through each human and AI transformation.
The final artwork is displayed with clear attribution to all human and AI contributors, and a
prominent notice declares the work as "Public Domain".

Core Principles and Stated Goals

The invention is explicitly built upon a foundation of five core principles that differentiate it from

existing creative tools and platforms. These principles are not merely aspirational but are
embodied in the specific features of the system and method.

?  Human-Centric Control: The system is designed to ensure the human artist remains the
ultimate director, providing "judgment" and "taste" at critical junctures. The AI serves as a
powerful co-creator and assistant, not a replacement.

?  Dynamic Iteration: The creative process is envisioned as an ongoing "dance" between

human and AI, emphasizing continuous feedback loops and successive refinement within
each timed "cadence".

?  Multimodal Fusion: The architecture is built to seamlessly integrate and transition

between different creative forms—text, images, audio, video—within a single project,
leveraging AI to facilitate these complex transformations.

?  Controlled Serendipity: The system intentionally introduces elements of chance and
unpredictability, such as the multiple AI options and concealed contributions, in a
structured manner to break creative homogeneity and drive unexpected, unique
outcomes.

?  Public Domain by Design: All resulting artworks are explicitly and intentionally dedicated
to the public domain. This principle aims to simplify intellectual property ambiguities and
foster an open, collaborative community focused on the shared joy of creation over
individual ownership.

These principles and the detailed system built to enact them form the basis of the invention's
claim to uniqueness. The following analysis will rigorously test this claim against the landscape
of prior art and competitive technologies.

Part I: The Landscape of Prior Art and Competitive
Analysis

To accurately assess the novelty of the Generative Cadence Canvas, it is essential to first
establish the state-of-the-art in related fields. This analysis examines the established
precedents in sequential collaborative art, the integration of AI into these formats, and the
broader technological capabilities of modern creative platforms.

Chapter 1: The Precedent of Sequential Collaborative Art

The core collaborative mechanic of the Generative Cadence Canvas is derived from
well-established parlor games that rely on sequential, partially-informed contributions.
Understanding these precedents is fundamental to evaluating the inventive step of the proposed
system.

Traditional Parlor Games

The most direct ancestor of the proposed game mechanic is cadavre exquis, or Exquisite
Corpse, a game invented by Surrealist artists in the 1920s. The game involves participants
taking turns drawing or writing on a sheet of paper, folding it to conceal their contribution, and
passing it to the next player. The process, which decentralizes authorship and introduces
chance as a key creative driver, was used to generate unexpected and often bizarre composite
figures and texts. This historical precedent establishes the core concepts of sequential
contribution and controlled visibility (the folded paper) as known methods for fostering

collaborative surprise.

Digital Implementations of the "Telephone Game"

The "Telephone Game," where a message is distorted as it's passed from person to person, has
been adapted into numerous online drawing games. These platforms represent the most
common digital form of sequential art creation.

?  Gartic Phone: A widely popular implementation where the game alternates between text
and drawing. One player writes a quirky sentence, the next player receives it and must
draw it, the following player receives the drawing and must describe it, and so on. The
core loop is a direct text-to-drawing-to-text chain.

?  Drawception: This platform operates on a similar principle, describing itself as the

"Telephone Game, but with drawing". A player draws a phrase, their drawing is described
by a random player, that description is drawn by another, and the chain continues for up
to 12 participants. Each turn has a 10-minute time limit.

?  Broken Picturephone: This is a live, real-time version where friends create collaborative
"books" of drawings and phrases. Critically, each player can only see the single preceding
page before making their contribution, mirroring the limited information flow of the
traditional game.

?  Telephone (artists.telephonegame.art): This project embodies the concept more

abstractly, describing its purpose as facilitating "a message changing forms as it travels
across the world from artist ? artist".

These examples demonstrate that the sequential, alternating-modality (text/drawing) game
format is a well-established genre in online entertainment.

Digital Implementations of "Exquisite Corpse"

The more structured format of Exquisite Corpse has also been digitized, focusing on creating
composite figures.

?  Monsterland: This online game explicitly follows the Exquisite Corpse model, allowing
users to draw a head, body, or legs for a monster in collaboration with strangers or in
private groups.

?  ExquisiteCorpse.us: This is a commercial, physical product—a specialized art

book—that formalizes the game with pre-defined sections for the head, torso, genitalia,
legs, and feet, demonstrating the concept's enduring appeal.

Shared Digital Canvases

As a point of contrast, it is important to acknowledge platforms that facilitate real-time,
simultaneous collaboration. Tools like Drawpile and the online whiteboard Miro provide a
shared digital canvas where multiple users can draw, paint, and create at the same time. The
PRD for Conexus Canvas explicitly distinguishes its sequential, turn-based model from these
synchronous platforms, highlighting that its goal is not interwoven co-creation but a structured,
cadenced evolution of an artwork.

Chapter 2: The Emergence of AI as a Creative Collaborator

The integration of artificial intelligence into creative tools is a rapidly advancing field. Several

projects have specifically combined AI with the sequential art game formats described above,
providing the most direct and critical prior art for the Generative Cadence Canvas concept.

?  MoMA's "Exquisite Corpse" with Adobe Firefly: This is a highly significant precedent

launched by the Museum of Modern Art. In this online experience, a player is assigned
one of three body sections (head, torso, or legs). The player then enters descriptive
words, and the AI (Adobe Firefly) generates four different image options based on the
prompt. The user selects their preferred image and submits it. The other two body
sections are completed by other players in the same manner. This project establishes a
clear precedent for a collaborative, sequential game that uses a human-prompt ->
AI-generation -> human-selection workflow. However, the human's role is limited to
providing the initial text prompt and making a final selection; there is no mechanism for
iterative refinement of the AI's output within a turn.

?  Northeastern University's "AI Generated Telephone Game": Developed as an

experimental game design project, this concept also serves as crucial prior art. The
gameplay loop involves one player writing a text prompt, which is sent to the next player.
That player inputs the exact phrase into an AI image generator (e.g., Craiyon) and
chooses one of the resulting images to pass along. The next player receives the image
and writes a detailed description of it. In this model, the AI's role is purely generative, and
players are explicitly instructed not to alter the AI's visual output. The human contribution
is limited to the initial prompt, the selection from the AI's output, and the subsequent
description. This reinforces the concept of AI as the drawing agent in a telephone game
but lacks the human-in-the-loop refinement central to the Generative Cadence Canvas.
?  Tel-AI-phone: This is a web and Steam-based party game for 4-8 players that describes
itself as a spin on the classic telephone game where players "pass around pictures
generated by AI". The game starts with a player-uploaded image, and subsequent
prompts are passed through a content filter to the AI. This further solidifies the game
concept of using AI as the primary image generator within a sequential, telephone-style
loop.

?  Gartic Phone's Controversial AI Mode: For a brief period, the popular game Gartic

Phone tested a beta mode where players could type a phrase and have the game's AI
generate an image. This feature was met with immediate and intense backlash from the
artist community. Streamers and artists, who had been instrumental in the game's
popularity, condemned the feature as "a straight-up slap in the face to any and all artists"
and a use of technology trained on "unethically ripped" artwork. The feature was swiftly
removed. This event is a critical data point, not as technical prior art, but as a powerful
indicator of market sentiment and the ethical sensitivities surrounding the use of
generative AI in creative social games.

?  Doodlocracy: This multiplayer game presents a different model of interaction. Each
player draws a prompt, and their drawing, along with the original prompt, is then
processed by a generative AI. Other players then view the final AI-generated piece and
attempt to guess the original prompt. This establishes a precedent for AI modifying or
interpreting a human drawing, but within a guessing-game format rather than a sequential
creation chain.

Chapter 3: The State of Multimodal and Real-Time AI Platforms

The technical feasibility and novelty of the Generative Cadence Canvas depend heavily on the
capabilities of the underlying AI technologies it proposes to integrate. The platform's claims to

uniqueness rest on its specific orchestration of multimodality, user refinement, and real-time
interaction.

Multimodal AI Capabilities

Multimodal AI refers to systems that can process, interpret, and generate content across
different data types, or modalities, such as text, images, audio, and video. This capability is
fundamental to the Conexus concept, which requires seamless transitions from text-to-image,
image-to-audio, and so on. Foundational models like Google Gemini are explicitly identified in
the Conexus documentation as being critical to this vision, particularly for their ability to handle
low-latency, bidirectional voice, video, and text interactions within a single session. The
evolution from unimodal (text-only) models to multimodal models like GPT-4V, Gemini, and
Llama 3.2 Vision represents a major technological shift that makes the Conexus concept viable.
These models are designed to understand the relationships between modalities, for example,
generating a descriptive caption for an image or generating an image that aligns with a text
narrative.

AI Art Generators with User Refinement

A key principle of the Generative Cadence Canvas is "Human-in-the-Loop Curation &
Refinement". This is presented as the solution to the problem of AI-generated content being
generic or lacking originality. The landscape of AI art generators shows that such refinement
tools are becoming increasingly common, though their integration into a collaborative game is
not.

?  Selection of Multiple Options: The feature of presenting a user with multiple

?

AI-generated options to choose from is not unique. It is a standard feature in many AI
image generators and is a core mechanic in MoMA's Exquisite Corpse game.
Iterative Refinement and Editing Tools: Advanced AI art platforms provide a suite of
tools that give users granular control over the generated output. This directly relates to the
refinement step proposed for Conexus.

?  Leonardo.ai offers a "Canvas Editor" for enhancing and modifying key details,

generating new visuals, and expanding the image.

?  Adobe Firefly is built into the Adobe Creative Cloud and allows users to refine their
vision with simple text prompts after initial generation, as well as adjust style, color,
and lighting.
Invoke features a professional-grade "Invoke Canvas" with layer-based editing,
allowing users to paint, draw, or use text to specify changes in particular areas of an
image, which are then applied on new, editable layers.

?

?  Fotor integrates a series of online AI tools, allowing users to edit AI images within

its graphic design feature by adding text, filters, or applying further AI modifications.

These platforms demonstrate that the technology for human-in-the-loop refinement is
well-established. However, it is typically employed in a solo creation context, where a single
artist is perfecting their own work.

Collaborative AI Workspaces

Several platforms have emerged that focus on team-based creative work, often incorporating AI
to enhance productivity. These platforms are important to analyze as they represent a different

approach to collaboration than the one proposed by Conexus.

?  Jeda.ai: This platform bills itself as the "world's first Multi-model Visual AI Online

Whiteboard". It is designed for real-time collaboration, allowing multiple users to work on
the same workspace simultaneously. It supports multimodal transformations, such as
converting sketches into diagrams or text into visuals. While it is highly collaborative and
multimodal, its documentation does not describe a sequential, turn-based, "telephone
game" style of interaction. Its focus is on synchronous brainstorming and strategic
analysis.

?  Miro: A market-leading collaborative online whiteboard, Miro has integrated AI features to

assist with tasks like summarizing discussions, generating diagrams from text, and
creating project briefs. However, its fundamental mode of interaction is synchronous,
allowing multiple users to contribute to a shared canvas simultaneously, which is distinct
from the asynchronous, sequential "cadence" of the proposed invention.
Invoke: In addition to its powerful refinement tools, Invoke offers collaborative "Studio
spaces" for teams with role-based access and shared images. This facilitates team-based
projects but does not appear to implement the specific, structured "telephone game"
mechanic.

?

?  NightCafe Studio: This platform has a strong community focus, featuring "Official daily AI

Art challenges" and collaborative chat rooms where users can "evolve each others'
creations". This fosters a form of social creativity but lacks the defined structure of timed,
sequential, hidden turns that is central to the Generative Cadence Canvas.
The analysis of the prior art reveals a distinct gap in the market. On one side, there are
established sequential art games (like Gartic Phone and Exquisite Corpse) that possess a
specific, engaging collaborative structure but lack sophisticated, multimodal AI integration. On
the other side, there are advanced AI art platforms (like Midjourney, Invoke, and Jeda.ai) that
offer powerful generative and refinement capabilities but are primarily designed for solo creators
or synchronous team collaboration, not for a structured, sequential game.
The few examples that attempt to bridge this gap, such as MoMA's Exquisite Corpse and the
Northeastern University game, do so in a limited fashion. They employ AI in a simple, one-step
"prompt-and-generate" capacity. The human's role is confined to providing an initial prompt and
selecting a final output from a set of AI-generated options. There is no mechanism for the kind
of iterative "dance" or deep, granular refinement within a single turn that the Generative
Cadence Canvas proposes.
Therefore, the primary area of uniqueness for the Generative Cadence Canvas does not reside
in any single, isolated feature. Timed turns, sequential gameplay, multimodal AI, and user
refinement tools all exist in some form in the prior art. The novelty lies in the specific system and
method for orchestrating these disparate elements into a single, fluid, and cohesive workflow.
The inventive step is the orchestration itself: the structured process that systematically
combines a timed, sequential, multimodal telephone game with a human-in-the-loop AI curation
and refinement cycle at each step. This system is designed to fill the "orchestration gap" by
managing a complex, multi-stage interaction that no existing platform currently facilitates.

Table 1: Competitive Feature Matrix

To provide a clear, quantitative summary of the competitive landscape, the following table
compares the features of the Generative Cadence Canvas against key prior art and related
platforms. This matrix visually highlights the unoccupied niche the proposed invention aims to
fill.

Feature

Core
Mechanic
AI
Integration

Multimodalit
y

CONEXUS
Canvas
(Proposed)
Sequential
Art Game
Collaborative
Partner

Text, Image,
Audio, Video
(Input/Output
)

Timed Turns Yes

Human
Selection of
AI Options
Post-Selecti
on
Refinement

Controlled
Visibility
Output IP
Model

(Configurable
, e.g., 30s)
Yes

Yes
(Drawing,
Masking,
etc.)
Yes (Blurred
Preview)
Public
Domain by
Design

Gartic Phone MoMA

Exquisite
Corpse
Sequential
Art Game
Generative
Assistant

Drawpile

Jeda.ai

Midjourney

Synchronous
Whiteboard
None

Synchronous
Whiteboard
Generative
Assistant

Solo
Generation
Core
Generator

Text (Input),
Image
(Output)

Image
(Input/Output
)

Text, Image
(Input/Output
)

Text, Image
(Input/Output
)

No

No

No

No

Yes

N/A

Yes

Yes
(Variations)

Sequential
Art Game
None (AI
mode
removed)
Text, Image
(Input/Output
)

Yes
(Configurable
)
N/A

No

No

N/A

Yes
(Annotation)

Yes
(Inpainting,
etc.)

No (Hidden
Text)
User
Creation

Yes (Hidden
Sections)
User
Creation

No

No

No

User
Creation

User
Creation

User License

Part II: An Assessment of Inventive Step and Core
Differentiators

Having established the landscape of prior art, this analysis now moves to a direct assessment of
the Generative Cadence Canvas's uniqueness. The argument for novelty rests not on a single
feature, but on the inventive combination and orchestration of multiple elements into a cohesive
system designed to produce a specific, non-obvious creative outcome.

Chapter 4: The "Generative Cadence" Process

The primary point of novelty is the core workflow itself, which the patent application terms the
"Generative Cadence Canvas". This process represents a unique synthesis of time, sequence,
and modality that is not present in the prior art.

The Synthesis of Time, Sequence, and Modality

The core method, as outlined in Claim 1 of the patent document, combines three distinct
elements into a single, integrated process :

1.  Sequential, Turn-Based Contribution: The system inherits the fundamental structure of

telephone and exquisite corpse games, where one user's contribution forms the basis for
the next.

2.  A Strict, Rapid Time Limit ("Cadence"): Each turn is "time-boxed," with a default of 30
seconds. This constraint is a deliberate design choice intended to foster "rapid, intuitive
creativity" and prevent over-analysis, forcing a more visceral and immediate response
from the user.

3.  Enforced Multimodal Transformation: The system is designed to ensure that the

modality of input and output evolves with each turn (e.g., text to image, image to audio,
audio to text). This is a critical differentiator from games like Gartic Phone, which typically
follow a rigid text-drawing-text pattern. This enforced shift is intended to encourage
"diverse creative interpretations" and push the collaborative artwork in unexpected
directions.

The term "cadence" itself is evocative. While commonly associated with music and rhythm,
patents exist that use the term in the context of generating a "coherent sequence of data objects
executable in sequence to provide an output at beats corresponding to the sequence position".
The application of this concept of a rhythmic, structured, and timed sequence to a multimodal
visual art game reinforces the novelty of the approach.

Argument for Non-Obviousness

While timed challenges exist on creative platforms like NightCafe , and sequential games are a
well-established genre, the argument for non-obviousness lies in the combination of these
elements with the enforced multimodal transformation at each step. A person having ordinary
skill in the art (PHOSITA) of designing online games or creative tools would not obviously arrive
at this specific combination. It is not a simple evolution of existing games but a deliberate design
to solve the specific, stated problems of creative stagnation and the tendency of AI to produce
homogenous outputs. The combination is a solution engineered to achieve a particular artistic
and collaborative effect.

Chapter 5: The Human-AI "Dance" of Curation and Refinement

The second major point of differentiation is the sophisticated human-in-the-loop mechanism,
which the documentation describes as a "dance" between human and AI. This process is
substantially more complex and interactive than the simple selection models found in prior art.

Beyond Simple Selection

The collaborative loop within a single turn is not merely a "prompt-and-generate" transaction. It
is a multi-stage process that deeply embeds human judgment at multiple points :

1.  Input: The user provides their creative input (text, sketch, audio) based on the partially

obscured previous turn.

2.  AI Generation of Options: The AI acts as a creative partner, generating a plurality of

diverse, multimodal outputs.

3.  Human Selection: The user reviews the AI-generated options and selects their preferred
path forward. This is the point where MoMA's Exquisite Corpse game ends the human
interaction.

4.  Human Refinement: The Conexus model introduces a crucial next step. The user can
apply basic refinement tools—such as drawing overlays, text edits, or masking—to the

selected AI output. They can even provide further text prompts for targeted AI
regeneration.

5.  Commitment: The user "commits" their selected and refined contribution, locking it in for

the next participant.

This complete loop within a single, timed turn is a significant departure from the simpler models
of AI collaboration found in the prior art.

Counteracting AI Homogeneity

The PRD and patent outline explicitly identify a known technical problem in the field of
generative AI: its tendency to produce "homogenous," "insipid," or "generic" outputs because it
primarily remixes and repurposes existing data. The proposed human selection and refinement
loop is framed as the direct technical solution to this problem. The system is designed so that
"human judgment and 'taste' guide the creative evolution," actively counteracting the AI's
inherent limitations. Framing this feature not merely as a user tool but as a specific solution to a
recognized technical challenge strengthens its inventive claim.

Comparison with Standard Refinement Tools

While powerful refinement tools exist in solo-creator platforms like Adobe Firefly and
Leonardo.ai, their context of use is entirely different. Those tools are designed for meticulous,
un-timed work by a single artist. The novelty of the Generative Cadence Canvas lies in
embedding a rapid, intuitive version of this refinement loop within the constraints of a
fast-paced, collaborative, sequential game. The challenge is not just to provide the tool, but to
make it usable and effective within a 30-second turn, which is a unique UI/UX and system
design problem.

Chapter 6: The Mechanics of "Controlled Serendipity"

The final core differentiator is the set of features designed to deliberately introduce
unpredictability and surprise in a structured manner, a principle the invention terms "Controlled
Serendipity".

The Blurred Preview

The feature of initially obscuring ongoing projects with a "blurred" or "abstractly represented"
preview is a direct digital analog to the folded paper in the traditional Exquisite Corpse game.
The wireframes show this as a key part of the user flow, where the "Previous artist's work" is
shown as "Partially blurred" to maintain an element of surprise. While the concept of hiding
information is not new, its specific implementation as a blurred visual preview in a digital,
multimodal AI context is a distinct UI/UX choice that contributes to the overall novelty of the
system.

Fostering Unpredictable Outcomes

This blurred preview, combined with the AI's designed potential for "misinterpretation" (by
offering diverse and sometimes unexpected options), is central to the principle of "Controlled
Serendipity." The system is explicitly designed to "break homogeneity and drive unexpected,

unique outcomes". This elevates the concept beyond a simple tool and frames it as a system
with an inventive purpose: to achieve a specific, non-obvious artistic goal. The aim is not just to
create art, but to create a specific kind of surprising, unpredictable, and genuinely collaborative
art that would be difficult to produce otherwise.
The uniqueness of the Generative Cadence Canvas, therefore, should not be evaluated on its
technical components in isolation. Features like timed turns, sequential flow, blurred previews,
AI-generated options, and human refinement tools are not entirely novel on their own. Instead,
the invention's true novelty lies in its design as a complete social-technical system. The features
are interdependent, each one architected to influence the others and guide the creative process.
The 30-second timer forces intuitive, not analytical, contributions. The blurred preview creates
anticipation and surprise. The multiple AI options introduce controlled chaos and serendipity.
The refinement step reasserts human control and taste. Finally, the public gallery and attribution
model foster a sense of community and shared accomplishment. This is not merely a "tool" in
the way that Photoshop or Midjourney are tools. It is a "game" or a "platform" whose primary
invention is the holistic method of orchestrating a novel form of collaborative creativity between
multiple humans and an AI. This framing is essential for the patent argument, as it elevates the
concept from a mere "combination of known features" to an integrated, inventive system with a
unique purpose, function, and effect.

Part III: Intellectual Property Strategy and Legal
Defensibility

This section provides a formal analysis of the Generative Cadence Canvas from an intellectual
property perspective. It assesses the patentability of the proposed invention, examines the
strategic implications of its "Public Domain by Design" model, and delves into the nuances of
copyright law as it pertains to human-AI collaborative works.

Chapter 7: A Preliminary Patentability Opinion

This chapter offers a preliminary opinion on the patentability of the invention as described in the
"Conceptual Patent Outline," focusing on the claims provided.

Analysis of Claims

The patent outline provides several example claims, with Claim 1 being the central independent
claim that defines the core method of the invention. A detailed analysis of its key elements is
required.

?  Claim 1(a-e): The Initial Contribution. These clauses describe receiving an initial
creative input (text, sketch, image, or audio) from a first user, processing it with a
multimodal generative AI to generate a plurality of outputs, and receiving the user's
selection and optional refinement. This initial loop is similar to the workflow of many solo
AI art generators.

?  Claim 1(f): The Partially Obscured Representation. This clause, which describes

presenting a "partially obscured" representation of the first contribution to a subsequent
user, is a key element. It directly corresponds to the "blurred preview" in the UI and is the
digital analog of the folded paper in Exquisite Corpse. Its inclusion in a multimodal AI
workflow is a point of novelty.

?  Claim 1(g): The Timed, Multimodal Subsequent Contribution. This clause specifies
receiving a second creative input from the subsequent user "in a different modality" and
"within a predefined time limit." The combination of these three constraints—sequentiality,
enforced modality shift, and a time limit—is a powerful and unique combination not found
in the direct prior art like MoMA's game or the Northeastern project.

?  Claim 1(h-k): The Iterative Loop. These clauses describe the repetition of the

generation, selection, and refinement process for subsequent users, forming the
"collaborative multi-modal artwork." This codifies the entire "Canvas Chain" process into
the method claim.

Novelty and Non-Obviousness

The invention, as defined in Claim 1, appears to meet the standards for novelty and
non-obviousness. While individual elements can be found in the prior art—MoMA's game has AI
selection , Gartic Phone has sequential art with time limits , and solo tools have refinement —no
single piece of prior art discloses the specific combination and orchestration of all these
elements as claimed. The integration of a timed, multimodally-shifting contribution with a
human-in-the-loop refinement cycle within a sequential, partially-obscured game structure is not
an obvious step for a Person Having Ordinary Skill in the Art (PHOSITA) to take. The invention
is more than the sum of its parts; it is a new process for creative collaboration.

Patent Eligibility (Subject Matter)

A critical hurdle for software and AI-related patents is subject matter eligibility under 35 U.S.C. §
101, which prevents the patenting of abstract ideas. A potential challenge could argue that
"collaborative art" is an abstract idea. However, the claims appear to be directed to a
patent-eligible practical application. The invention is not the abstract idea itself, but a specific,
technical system for implementing that idea. The claims recite concrete steps involving a
client-side application, a backend server, and the orchestration of specific AI APIs to manage a
complex data flow and user interaction. Furthermore, the system is designed to solve a
technical problem identified in the field of generative AI—its tendency toward homogeneity—by
implementing a specific technical solution: the human-in-the-loop curation and refinement cycle.
This focus on a practical, technical implementation to solve a technical problem strongly
supports its eligibility for patent protection under current USPTO guidance.

Inventorship

The patent outline correctly lists human inventors and not the AI system itself. This is consistent
with current U.S. patent law, which requires inventors to be natural persons, as affirmed in the
Federal Circuit case Thaler v. Vidal. The significant human contribution to the conception of the
system—its architecture, rules, and objectives—is well-documented and justifies human
inventorship.

Table 2: Patent Claim Element Analysis

To provide a granular analysis of the primary claim, the following table deconstructs Claim 1
from the patent outline and assesses each key element against the prior art.

Claim 1 Element (Abbreviated)  Closest Prior Art

(a) Receiving initial creative
input (multimodal)
(b) Processing with
multimodal generative AI

Most AI Generators (e.g.,
Midjourney, DALL-E)
Google Gemini, GPT-4V

(c-d) Presenting a plurality of
outputs for user selection

MoMA Exquisite Corpse , most
AI generators

(e) Storing selected &
optionally refined output

AI generators with editing tools
(e.g., Invoke, Leonardo.ai)

(f) Presenting a partially
obscured representation

Traditional Exquisite Corpse
(folded paper)

(g) Receiving subsequent
input in a different modality
within a time limit

Gartic Phone (timed turns) ,
Telephone Games (modality
shift)

(h-k) Iteratively repeating the
process

All sequential games (Gartic
Phone, Drawception)

Analysis of Novelty &
Non-Obviousness
Not novel in isolation. Standard
practice for AI generation.
The use of such models is not
novel, but its application within
this specific method is.
Not novel in isolation. A
common feature to provide user
choice.
The refinement capability exists
in solo tools. Its integration into
this specific loop is the novel
step.
Novel in its specific digital
implementation (e.g., "blurred
preview" ). Non-obvious to
combine this with a multimodal
AI workflow.
The combination of a time limit
with an enforced multimodal
shift at each step is novel and
non-obvious. No prior art
combines these specific
constraints.
The iterative structure is known,
but the novelty lies in the
specific content of the loop
being iterated (i.e., all the
preceding novel elements).

Chapter 8: The Strategic Implications of a "Public Domain by Design"
Model

The decision to have all resulting collaborative artworks explicitly dedicated to the public domain
is a cornerstone of the invention's identity and a profound strategic choice with significant legal
and business implications.

Sidestepping the Copyright Quagmire

Current U.S. copyright law is ill-equipped to handle works generated by AI. The U.S. Copyright
Office has maintained that works must have human authorship to be copyrightable, generally
rendering purely AI-generated content as public domain. This has led to a complex and
contentious legal landscape, with ongoing lawsuits and debates about training data, authorship,
and fair use. By adopting a "Public Domain by Design" model, Conexus strategically sidesteps
this entire legal morass. It eliminates ambiguity for its users and simplifies its own legal posture
and Terms of Service (ToS) immeasurably.

Ethical and Community-Building Advantages

This public domain approach directly addresses the ethical concerns that led to the intense
backlash against Gartic Phone's AI mode. The artist community often views corporate attempts
to own or control AI-generated art with suspicion. By explicitly rejecting ownership and instead
emphasizing the "shared joy of creation" , Conexus positions itself as an ethical, pro-community
platform. This can be a powerful marketing tool and a significant driver of user adoption and
loyalty, particularly among the "Creative Explorers" identified as the target audience. It builds a
brand identity centered on openness and collaboration rather than extraction and ownership.

Monetization Challenges and Opportunities

This model fundamentally alters the platform's monetization strategy. As acknowledged in the
PRD, the platform cannot monetize the output (the art itself) as it has been dedicated to the
public. The value proposition and revenue model must therefore shift to the process and
access. The PRD outlines several post-MVP monetization strategies that align with this model,
such as :

?  Subscription Models: Offering tiered subscriptions that grant access to premium

features like private games, longer turn durations, more sophisticated refinement tools, or
the ability to use more powerful (and expensive) AI models.

?  API Access/Credits: For power users or commercial entities, charging for high-volume

use of the platform's unique creative process via API.

?  Freemium Model: Providing a basic version of the experience for free to build a large

user base, while upselling to paid tiers for advanced functionalities.

The business model becomes one of selling access to a unique, patented creative experience,
rather than selling the artifacts produced by it.

Chapter 9: Copyrightability in Human-AI Collaboration

While the platform's stated goal is public domain output, it is legally important to understand the
copyright status of the works before they are dedicated to the public domain. This nuance
strengthens the platform's legal foundation.

The "Meaningful Human Input" Standard

The U.S. Copyright Office's guidance makes a distinction between works generated by AI and
works created with the assistance of AI. A work can be copyrighted if a human provides
sufficient creative input and control. The case of Kristina Kashtanova's comic Zarya of the Dawn
is instructive. The Copyright Office granted copyright for the text and the creative arrangement
of the images, but not for the individual images themselves, which were generated by
Midjourney. The office ruled that there was a "significant distance" between the user's text
prompts and the final output, meaning the user did not have sufficient creative control over the
images to be considered their "author".

Analyzing the Conexus Refinement Loop

The Generative Cadence Canvas workflow appears to be specifically designed to cross this
threshold of "meaningful human input." The process is not limited to a simple text prompt. The

user actively:

1.  Selects a preferred option from a diverse plurality of AI generations.
2.  Arranges and modifies that selection using refinement tools like drawing overlays,

masking, and editing.

This level of detailed intervention and curation arguably provides the "significant creative input"
that was deemed lacking in the Zarya of the Dawn case. Therefore, it is highly probable that a
work created through the Conexus process is eligible for copyright protection in the name of the
human user who completed that turn.

The Public Domain Dedication as a Legal Transfer

This understanding reframes the "Public Domain by Design" principle. It is not a result of the
work being inherently uncopyrightable. Rather, it is a deliberate legal transfer facilitated by the
platform. The platform's Terms of Service would need to be meticulously drafted to state that as
a condition of using the service, the user, who is the author of their potentially copyrightable
contribution, agrees to dedicate that work to the public domain upon commitment. This is a
legally robust and clear position. It transforms the public domain status from a default outcome
of legal ambiguity into an intentional, user-driven action that is central to the platform's
collaborative ethos.
The project's overall intellectual property approach is therefore revealed to be highly
sophisticated. It employs two distinct strategies that, while seemingly contradictory, are in fact
symbiotic. First, it pursues patent protection for the method and system of creation. This is a
proprietary, defensive strategy designed to protect the unique user experience and prevent
competitors from cloning the core collaborative process. Second, it mandates that the output of
this proprietary system be dedicated to the public domain. This is an open, community-focused
strategy. This dual approach allows the platform to build a defensible competitive moat around
its core process—the "how"—which is the monetizable asset. Simultaneously, it leverages the
principles of the public domain to make the content created on the platform freely available,
fostering community, encouraging viral sharing, and creating a powerful engine for growth and
user engagement. This is a unique and well-considered IP strategy that aligns legal protection
with business and community goals.

Table 3: Comparative Analysis of IP and Monetization Models

This table contrasts the unique business and legal model of the Generative Cadence Canvas
with its potential competitors, demonstrating its differentiated market positioning.
Platform

Output Copyright
Holder

Commercial Use
Terms

Stated Ethical
Stance

CONEXUS
Canvas

Public Domain (by
user dedication)

Unrestricted

Midjourney

Leonardo.ai

User (with paid
subscription)
Leonardo.ai (for
free tier), User (for
paid)

Permitted under
paid plans
Requires paid
subscription

Primary
Monetization
Model
Subscription for
process/tools/acce
ss
Subscription for
generation credits
Subscription for
credits/features

"Public Domain by
Design"

User owns their
creations
User ownership
with paid plans

Platform

Output Copyright
Holder

Commercial Use
Terms

Adobe Firefly

User (subject to
terms)

Permitted,
designed for
commercial safety

Primary
Monetization
Model
Creative Cloud
Subscription

Stated Ethical
Stance

"Trained on
licensed content"

Part IV: Synthesis and Strategic Recommendations

This final part consolidates the findings of the comprehensive analysis into a conclusive verdict
on the uniqueness of the Generative Cadence Canvas and provides actionable, strategic
recommendations to fortify the invention's position and guide its future development.

Chapter 10: Recommendations for Fortifying the Invention's
Uniqueness

Based on the detailed analysis of the prior art, technological landscape, and IP strategy, the
following recommendations are provided to strengthen the invention's novelty and defensibility.

Patent Prosecution Strategy

The conceptual patent outline provides a strong foundation, but the claims can be fortified to
maximize defensibility.

?  Emphasize Technical Solutions: The patent application should explicitly frame the

invention's features as technical solutions to known technical problems. For instance, the
"human-in-the-loop curation & refinement" cycle should be described not just as a feature,
but as a specific technical method for overcoming the widely recognized problem of "AI
homogeneity" in generative models. Similarly, the "Generative Cadence" itself—the timed,
multimodal sequence—can be positioned as a technical solution to creative block and a
method for achieving "controlled serendipity". This framing strengthens the argument for
patent eligibility by grounding the invention in a technical context.

?  Focus on API Orchestration: Claims 4 and 5, which describe the integration of a

plurality of distinct AI-as-a-Service (AlaaS) APIs, should be highlighted as a key technical
aspect of the invention. The novelty lies in the backend server's role as an orchestrator
that manages the complex, sequential flow of data between different specialized models
(e.g., from a text model like Gemini to an image model like DALL-E 3 to an audio model
like Suno AI). This orchestration is a non-trivial technical implementation that is central to
achieving the multimodal fusion principle.

Product Development Roadmap

The product development roadmap should prioritize features that amplify the core differentiators
identified in this report.

?  Enhance the "Human-in-the-Loop" Cycle: As this is a key pillar of the invention's

uniqueness and its potential to create copyrightable (and thus, dedicatable) works, this
feature set should be expanded. Consideration should be given to adding more
sophisticated refinement tools (e.g., color palette adjustments, style intensity sliders) that
are still intuitive enough to be used within the time constraint. Furthermore, enabling users

to provide feedback on the AI's options (e.g., "dislike this style") could allow the AI to learn
and offer more tailored suggestions in subsequent turns within the same Canvas Chain,
deepening the "dance."

?  Lean into "Controlled Serendipity": The element of surprise is a core part of the user

experience. The team should experiment with more ways to introduce structured
unpredictability. This could include "wildcard" turns where the AI introduces a completely
unexpected modality shift, or "mutation" options that dramatically alter the previous
contribution in a surprising way. These features would further distance the platform from
standard, predictable creative tools.

Legal and Business Strategy

The unique IP model requires careful and deliberate execution.

?

Impeccable Terms of Service: It is of paramount importance that the platform's Terms of
Service (ToS) are drafted with extreme care and clarity. The ToS must explicitly state that:
1) works created on the platform may contain sufficient human authorship to be
copyrightable by the user, and 2) as a condition of using the platform, the user agrees to
irrevocably dedicate any such copyright to the public domain upon committing their
contribution. This ensures informed consent and provides a robust legal foundation for the
public domain model.

?  Market the "Public Domain" Ethos: The "Public Domain by Design" principle should not
be a footnote in the legal terms; it should be a central pillar of the platform's marketing
and brand identity. This ethical stance is a powerful differentiator that will attract the target
user base of "Creative Explorers" and artists who are ethically concerned about the
corporate capture of AI creativity. It should be communicated clearly in all branding,
onboarding, and community engagement efforts.

Conclusion: A Final Verdict on the Uniqueness of the Generative
Cadence Canvas

Following an exhaustive analysis of the provided documentation and the broader competitive
and technological landscape, this report offers a definitive verdict on the uniqueness of the
"Generative Cadence Canvas" concept.

?  Conceptual Uniqueness: The concept is assessed as highly unique. While it builds
upon the known mechanics of sequential art games like the telephone game and
Exquisite Corpse, its specific and deliberate orchestration of a timed, multimodal,
human-AI refinement loop is novel. It establishes a new genre of creative experience that
does not currently exist.

?  Technological Uniqueness: The invention's uniqueness does not stem from the creation
of a new foundational AI model. Instead, its technological novelty lies in the sophisticated
integration and orchestration of existing, state-of-the-art AI APIs into a new type of
collaborative system. The backend architecture required to manage the queues, timers,
state transitions, and calls to a plurality of disparate AI services in a seamless, sequential
flow represents a significant and novel technical implementation.
IP Defensibility: The intellectual property strategy is both defensible and highly
sophisticated. The patent application, if focused on the system as a technical solution to
specific problems, appears strong and likely to succeed. The accompanying "Public

?

Domain by Design" model is a unique and powerful strategic choice. While it introduces
challenges for direct monetization of content, it creates a formidable ethical and
community-driven moat around the brand, mitigates significant legal risks associated with
AI copyright, and fosters a viral growth loop.

Final Recommendation: Based on this comprehensive analysis, the "Generative Cadence
Canvas" concept is demonstrably unique in its core method, technological orchestration, and IP
strategy. It addresses a clear gap in the market for a new form of structured, collaborative, and
serendipitous creativity. The project warrants further investment and development, with a
strategic focus on flawlessly executing the specific, orchestrated user experience that forms the
very heart of its novelty and commercial potential.

Works cited

1. Exquisite Corpse | karen c fisher, https://karencfisher.com/2023/03/27/exquisite-corpse/ 2.
Exquisite corpse - MoMA, https://www.moma.org/collection/terms/exquisite-corpse 3. Exquisite
Corpse: Collaborative Class Exercise - OER Commons,
https://oercommons.org/authoring/54596-exquisite-corpse-collaborative-class-exercise/view 4.
Exquisite Corpse as Generative Art - Minnie Muse,
https://www.minniemuse.com/articles/parallel-practices/exquisite-corpse 5. Gartic Phone - The
Telephone Game, https://garticphone.com/ 6. Gartic Phone (2020) - IGDB.com,
https://www.igdb.com/games/gartic-phone/reviews/surprisingly-fun 7. Drawception - Picture
Telephone Drawing Game, https://drawception.com/ 8. [TOMT][Online game] Sort of like the old
game 'Telephone', but with drawings. Start off with a prompt, first person draws it. Then the next
person interprets the drawing, then the next person draws what the second person said, and on.
: r/tipofmytongue - Reddit,
https://www.reddit.com/r/tipofmytongue/comments/6d788z/tomtonline_game_sort_of_like_the_o
ld_game/ 9. Broken Picturephone, https://www.brokenpicturephone.com/ 10. TELEPHONE,
https://artists.telephonegame.art/ 11. About Monsterland - Monsterland- an "Exquisite Corpse"
drawing game, https://monsterland.net/about 12. Monsterland is an online exquisite corpse
drawing game,
https://boingboing.net/2022/05/26/monsterland-is-an-online-exquisite-corpse-drawing-game.htm
l 13. Exquisite Corpse Party Game | Fun Art Book Game, https://www.exquisitecorpse.us/ 14.
Drawpile, https://drawpile.net/ 15. About Drawpile, https://drawpile.net/about/ 16. Miro | The
Innovation Workspace, https://miro.com/ 17. HotPicks | Linux Format August 2024 -
Pocketmags, https://pocketmags.com/us/linux-format-magazine/august-2024/articles/hotpicks
18. Exquisite Corpse, https://ec.moma.org/ 19. Make a Surrealist exquisite corpse,
https://ec.moma.org/intro 20. AI Generated Telephone Game | Experimental Game Design,
https://experimentalgamedesign.sites.northeastern.edu/2023/10/24/ai-generated-telephone-gam
e/ 21. Tel-AI-phone, https://telaiphone.com/ 22. Gartic Phone Testing Generative AI in Game -
mxdwn Games, https://games.mxdwn.com/news/gartic-phone-testing-generative-ai-in-game/ 23.
The game that's all about drawing and creativity, Gartic Phone, adds and then swiftly removes
an AI mode, in 'a straight-up slap in the face to any and all artists' | PC Gamer,
https://www.pcgamer.com/games/puzzle/the-game-thats-all-about-drawing-and-creativity-gartic-
phone-adds-and-then-swiftly-removes-an-ai-mode-in-a-straight-up-slap-in-the-face-to-any-and-a
ll-artists/ 24. Doodlocracy: a multiplayer AI drawing game. : r/WebGames - Reddit,
https://www.reddit.com/r/WebGames/comments/12530ro/doodlocracy_a_multiplayer_ai_drawin
g_game/ 25. Multimodal AI | Google Cloud, https://cloud.google.com/use-cases/multimodal-ai
26. Multimodal AI: Beyond Text and Images  | TechAhead,

https://www.techaheadcorp.com/blog/multimodal-ai-beyond-text-and-images/ 27. Multimodal AI:
When Text, Images, and Audio Collide - Digital Digest,
https://digitaldigest.com/multimodal-ai-when-text-images-and-audio-collide/ 28. Multimodal AI: A
Guide to Open-Source Vision Language Models - BentoML,
https://www.bentoml.com/blog/multimodal-ai-a-guide-to-open-source-vision-language-models
29. Top 10 Multimodal AI Models of 2024 - Zilliz Learn,
https://zilliz.com/learn/top-10-best-multimodal-ai-models-you-should-know 30. Developing
Multimodal Generative AI Models: Combining Text, Image, and Audio,
https://www.xcubelabs.com/blog/developing-multimodal-generative-ai-models-combining-text-im
age-and-audio/ 31. Best AI Image Generators of 2025 - CNET,
https://www.cnet.com/tech/services-and-software/best-ai-image-generators/ 32. AI Art
Generator – Enhance Your AI Art with Leonardo.Ai, https://leonardo.ai/ai-art-generator/ 33. Free
AI Art Generator: Create AI Art Online - Adobe Firefly,
https://www.adobe.com/products/firefly/features/ai-art-generator.html 34. Invoke | Generative AI
Platform for Creative Production, https://www.invoke.com/ 35. Free AI Art Generator Online:
Create AI Artwork from Text or Photo | Fotor, https://www.fotor.com/ai-art-generator/ 36.
Multi-LLM Generative Visual AI Online Whiteboard: Instant Visual Intelligence - Jeda.ai,
https://www.jeda.ai/visual-ai-online-whiteboard 37. Multimodal Generative Visual AI Workspace:
Visualize, Collaborate, Innovate — Jeda.ai, https://www.jeda.ai/ 38. Free AI Art Generator: All
the best AI models in one place, https://creator.nightcafe.studio/ 39. Generative scheduling
method - US9361869B2 - Google Patents, https://patents.google.com/patent/US9361869B2/en
40. US10467998B2 - Automated music composition and generation system for spotting digital
media objects and event markers using emotion-type, style-type, timing-type and accent-type
musical experience descriptors that characterize the digital music to be automatically composed
and generated by the system - Google Patents,
https://patents.google.com/patent/US10467998B2/en 41. Request for Comments Regarding the
Impact of the Proliferation of Artificial Intelligence on Prior Art, the Knowledge of a Person
Having Ordinary Skill in the Art, and Determinations of Patentability Made in View of the
Foregoing - Federal Register,
https://www.federalregister.gov/documents/2024/04/30/2024-08969/request-for-comments-regar
ding-the-impact-of-the-proliferation-of-artificial-intelligence-on-prior 42. AI & Photoshop -
Artificial Intelligence: How AI is Changing Art - Aela Design,
https://www.aela.io/en/blog/all/artificial-intelligence-art-changes 43. Collaboration or
Replacement? The Benefits and Challenges of AI in Creativity,
https://leadershipflagship.com/2024/07/28/collaboration-or-replacement-the-benefits-and-challe
nges-of-ai-in-creativity/ 44. 15 Best AI Image Generator in 2025 (Free And Paid) - Zight,
https://zight.com/blog/best-ai-image-generator/ 45. Artificial Intelligence (AI) Patents - BitLaw,
https://www.bitlaw.com/ai/AI-patents.html 46. Beyond Language: How Multimodal AI Sees the
Bigger Picture - PatentNext,
https://www.patentnext.com/2024/01/beyond-language-how-multimodal-ai-sees-the-bigger-pictu
re/ 47. Patent Strategies and AI-Generated Inventions - Prof. Dr. Alexander Wurzer,
https://profwurzer.com/patent-strategies-and-ai-generated-inventions/ 48. Encouraging Human
Creativity in the AI-Powered Future - Stanford Social Innovation Review,
https://ssir.org/articles/entry/ai-creativity-copyrights-patents 49. Can Artificial Intelligence (AI)
Generate Prior Art (e.g., a “Printed Publication”) pursuant to U.S. Patent Law? - PatentNext,
https://www.patentnext.com/2024/06/can-artificial-intelligence-ai-generate-prior-art-e-g-a-printed
-publication-pursuant-to-u-s-patent-law/ 50. Inventorship Guidance for AI-Assisted Inventions -
Federal Register,

https://www.federalregister.gov/documents/2024/02/13/2024-02623/inventorship-guidance-for-ai
-assisted-inventions 51. Generative Artificial Intelligence: Intellectual Property - USMA Library,
https://library.westpoint.edu/c.php?g=1388421&p=10802412 52. AI, Copyright, and the Law:
The Ongoing Battle Over Intellectual Property Rights,
https://sites.usc.edu/iptls/2025/02/04/ai-copyright-and-the-law-the-ongoing-battle-over-intellectu
al-property-rights/ 53. Can Intellectual Property Law contend with AI in the Art World?,
https://www.standrewslawreview.com/post/can-intellectual-property-law-contend-with-ai-in-the-ar
t-world 54. Artists' Rights in the Age of Generative AI | GJIA - Georgetown University,
https://gjia.georgetown.edu/2024/07/10/innovation-and-artists-rights-in-the-age-of-generative-ai/
55. Is AI-Generated Art Legal? Copyright Facts Explained - Growleady,
https://www.growleady.io/blog/are-ai-art-generators-illegal 56. Authorship and Copyright In
Hybrid AI-Human Collaborative Works,
https://www.lawjournalnewsletters.com/2023/04/01/authorship-and-copyright-in-hybrid-ai-human
-collaborative-works/



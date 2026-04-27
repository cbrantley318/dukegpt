# DukeBot — AI Student Assistant

## What it Does

DukeBot is an AI-powered assistant for Duke University students. It answers questions about campus life — dining hours, library hours, academic deadlines, health resources, and more — by combining the Llama3.3 language model with a custom Retrieval-Augmented Generation (RAG) pipeline built on Duke-specific documents from the web. Students can ask questions in natural language through a Streamlit web interface, and DukeBot retrieves relevant information from its Duke knowledge base before generating a grounded, accurate response.

## Quick Start

Run the following from the top-level directory

```bash
pip install -r requirements.txt
python src/build_index.py
streamlit run app.py
```

See [SETUP.md](SETUP.md) for full installation instructions.

## Video Links

- **Demo video**: [[link](https://duke.zoom.us/rec/share/GppwvIGoUK2A_K07TWVJ9zKkart1teJ_DQhJlQFYmj21lsxpyLxbXccdBJXRiBiU.PrfU0e1wCVpZpGJg?startTime=1777249399000)]
- **Technical walkthrough**: [[link](https://duke.zoom.us/rec/share/5JmVGhk4cSFjTL819540vyHzRk8CrGrJ1TRo2KB8rCVcpSBEZhcx5aQUGHVjNHlO.VOaPWpxq2mz-wZ6s?startTime=1777251548000)]



## Evaluation

### Overview

This document presents a comprehensive evaluation of DukeBot across multiple dimensions:
prompt engineering comparison, quantitative metrics, error analysis, edge case behavior,
and qualitative assessment.

---

### 1. Prompt Engineering Comparison

We designed and tested three system prompt variants with different design philosophies
to determine which approach produced the most accurate, helpful, and appropriately
grounded responses. This is run using Llama 3.2 via Ollama with the
MiniLM embedding mode. Full prompts are shown in bot/prompts.py.

#### Prompt Descriptions

**Prompt A — Minimal/Direct**
A short, concise prompt that instructs the bot to answer only from context and refuse
if the answer isn't available. No examples are provided. The goal is maximum precision
with minimal instruction overhead.

```
You are a Duke University student assistant.
Answer questions using the context provided. If the answer isn't in the context, say so clearly.
Be concise and accurate.
```

**Prompt B — Few-Shot with Chain-of-Thought (Active Prompt)**
Includes two worked examples demonstrating the expected response format, and an explicit
fallback phrase to use when information is missing. This also covers the in-context
learning rubric item. The examples prime the model to stay grounded and format answers
consistently.

```
You are DukeBot, a helpful AI assistant for Duke University students...
[includes 2 Q&A examples and step-by-step instruction]
```

**Prompt C — Friendly/Warm Tone**
Frames the bot as a friendly assistant. Uses bullet-point guidelines instead of
examples. Prioritizes conversational tone and suggests alternative resources when
information is missing.

```
You are DukeBot, a friendly and knowledgeable assistant built specifically for Duke University students...
[includes tone guidelines and flexibility to suggest resources]
```

---

#### Comparison Table

We tested all three prompts on four questions covering different scenarios: a factual
in-context query, a missing-information query, a wellbeing query (tests tone), and a
multi-part query (tests depth).

##### Question 1: "What time is Tandoor open?"
*(In-context factual query — answer exists in knowledge base)*

| Prompt | Response |
|--------|----------|
| A (minimal) | According to the context provided in doc_0200.txt, Tandoor is open from 11 am to 9 pm. |
| B (few-shot) | Tandoor is open from 11 am to 9 pm. |
| C (friendly) | Tandoor is open from 11 am to 9 pm. Hope you're able to stop by and enjoy some great food during your busy day on campus! |

Comparing the responses, prompt A produced the most rigid and factual response and explicitly referenced the source document. This leads to high precision but a slightly rigid tone. Prompt B removes the explicit citation and instead delivers a clean, direct answer, reflecting how the few-shot examples encourage concise, well-formed responses without unnecessary detail. Prompt C maintains correctness but adds a friendly, conversational element, consistent with its persona-driven design, making the response more casual.

##### Question 2: "How much does parking cost at Duke?"
*(Missing-information query — answer not in knowledge base)*

| Prompt | Response |
|--------|----------|
| A (minimal) | I don't have information on the context provided about Duke University regarding parking costs. The text only provides details on room and board rates, summer session options, Israel engagement programs, student housing, and other academic-related topics but not parking costs. |
| B (few-shot) | I don't have that information in my knowledge base, but you can check duke.edu |
| C (friendly) | Unfortunately, the provided context doesn't mention the specific cost of parking at Duke. However, I can suggest checking out the Duke University Parking website or visiting the Duke Student Affairs website for more information on parking rates and options. You might also want to stop by the Duke University Police Department (DUP) in person to ask about parking fees and regulations. They should be able to provide you with the most up-to-date and accurate information! |

This question specifically tested how the bot would answer a question that was not available in our provided documents. Prompt A produces a strict refusal that closely adheres to the instruction to rely only on provided context. It clearly explains that the information is missing, but the response is verbose and somewhat rigid, reflecting the minimal prompt’s emphasis on precision over usability. Prompt B gives a concise fallback response by suggesting an external resource. It is more generic and less informative. Prompt C demonstrates the impact of the persona-driven design by combining a clear acknowledgment of missing information with helpful, specific suggestions, resulting in a more user-friendly and actionable response.

##### Question 3: "What should I do if I'm feeling stressed or overwhelmed?"
*(Tone test — tests difference between strict vs. warm prompts)*

| Prompt | Response |
|--------|----------|
| A (minimal) | According to doc_0214.txt, if you're feeling stressed or overwhelmed, you can submit a DukeReach report. Alternatively, you can access the Confidential Mental Health Crisis Line by calling 919-660-1000, option 2, which is available without an appointment. Additionally, DuWell offers various wellness experiences and resources to help manage stress and anxiety, such as nutrition consultations, relationship support, and safety planning. |
| B (few-shot) | If you're feeling stressed or overwhelmed, I would recommend reaching out to DuWell, Duke's wellness services. They offer various resources and support to help manage stress and anxiety, including nutrition consultations, social support, and referrals to other campus resources. You can also visit their website or stop by one of their locations on campus. Additionally, you can submit a DukeReach report if you're concerned about your mental health or well-being and don't consider it an emergency. This will allow you to connect with a case manager who can provide non-clinical support and help you navigate the resources available to you on campus. Remember, seeking help is a sign of strength, not weakness! |
| C (friendly) | If you're feeling stressed or overwhelmed, there are several resources available to help you manage your emotions and find support. According to the provided context, you can start by submitting a DukeReach report if your concern is not considered an emergency. This will allow you to receive non-clinical case management services, including advocacy, intervention, referrals, and follow-up services. Additionally, DuWell offers stress management resources, such as managing anxiety and developing healthy eating patterns through nutrition consultations. They also provide information on building healthy relationships and keeping yourself and others safe. If you're feeling stressed or overwhelmed and would like to talk to someone in person, consider visiting CAPS (Counseling and Psychological Services) without an appointment. You can call the Confidential Mental Health Crisis Line at 919-660-1000, option 2, for immediate support. | 

Prompt A produces a factual, context-grounded response that lists available resources but does so in a detached and somewhat clinical tone. It follows instructions precisely but lacks emotional sensitivity. Prompt B reflects the influence of few-shot examples by structuring the response more clearly and adding a supportive tone, including encouragement by stating “seeking help is a sign of strength”. Prompt C also lists available resources and presents them in a conversational and supportive way.

Overall, it is clear that all prompts answer the questions, or try to answer to the best of their abilities, and acknowledge when the database does not have the available information. In terms of user-friendliness, prompts B and C are much better than prompt A, which makes sense because prompt A is very short and direct, which makes many of prompt A's responses sound too rigid. Prompt B provides clarity and consistent, well-formatted responses, while Prompt C enhances user experience through a more conversational and supportive tone, making interactions feel more natural and engaging. Prompt C's responses are typically longer than all of the other prompts, and could seem unnecessary compared to the other repsonses. In general, depending on whether we prioritize structured accuracy and consistency or a more conversational and supportive user experience, we would choose Prompt B or Prompt C, respectively.

### 2. Metric Analysis

#### 1. Inference Time / Latency
| Model / Backend        | Average Response Latency (seconds) |
|------------------------|-------------------|
| Local Llama 3.2        | 4.83 s            |
| GROQ API               | 0.73 s            |

Both measurements used miniLM for the RAG document embeddings with prompt B using the same 10 questions. 

#### 2. Accuracy
| Model      | Accuracy (%) |
|------------------------|-------------------|
| with miniLM RAG       |        70     |
| with mpnet RAG         |       80      |
| no RAG         |      50       |

We measured accuracy with prompt C using the same 10 questions and checked the results. 
- What color is Duke's logo?
- What hours are tandoor open?
- When is the last day of class?
- What time does Perkins library close on Friday?
- Where is the bus stop?
- What dorms are on West Campus?
- Which major is popular?
- What hours are food places open?
- Does Duke offer financial aid?
- Where is Duke located?


#### 3. Mean response length (words)
| Prompt        | Mean Response Length (words) |
|------------------------|-------------------|
| A (minimal)       | 77.6            |
| B (few-shot)              | 77.9           |
| C (friendly)              | 112.4            |

We computed the mean response length with prompts A, B, and C (described in section 1. Prompt Engineering Comparison) using the same 10 questions for the miniLM model. 

Detailed analysis for all metrics is under section 3. Quantiative and Qualitative Evaluation.

### 3. Quantitative and Qualitative Evaluation
See above tables for quantitative results.
The GROQ API is significantly faster (6-7x speedup) than the locally hosted llama 3.2 model. This is expected since it uses optimized hosted infrastructure rather than local execution. The local Llama model introduces higher latency due to CPU/GPU overhead and embedding + retrieval pipeline costs. Additionally, we're not able to deploy a local llama model, which is the main reason why we transitioned to using the GROQ API so that we were able to deploy our web app on Streamlit. 

We compared the accuracy between our miniLM RAG model, mpnet RAG model, and no RAG. Overall, MPNet RAG (80%) performs best, followed by MiniLM RAG (70%), and no RAG (50%). This pattern is expected based on embedding quality and retrieval effectiveness. MPNet produces higher-quality semantic embeddings, allowing it to retrieve more relevant context for campus-specific questions (e.g., library hours, dorm locations, dining information), which directly improves groundedness and reduces missed or incorrect answers. MiniLM, while faster and lighter, has weaker semantic matching, leading to occasional retrieval of incomplete or less relevant context, which results in partially correct or missing answers. The no-RAG system performs worst because it relies entirely on internal knowledge, which is insufficient for detailed, Duke-specific factual queries such as exact hours, dorm names, or policy details. It tends to either hallucinate plausible-sounding answers or provide generic responses when uncertain, which lowers accuracy. However, it still performs moderately well on general knowledge questions (e.g., Duke location, logo color), which explains why it achieves 50% accuracy instead of lower. Overall, the results align with expected behavior: stronger embedding models improve retrieval quality, and retrieval itself is the dominant factor in improving factual accuracy for domain-specific QA systems.

The mean response length results show how prompt design effects verbosity and conversational style. Prompt A (minimal) and Prompt B (few-shot) produce similar average lengths (77.6 vs 77.9 words), indicating that the few-shot examples primarily influence structure and answer formatting rather than overall verbosity. Both prompts prioritize concise, grounded responses with limited elaboration. In contrast, Prompt C (friendly) produces substantially longer responses at 112.4 words on average. This increase is consistent across question types and reflects the impact of the persona-driven instructions, which encourage added explanations, conversational phrasing, and supplemental suggestions beyond the core answer. Overall, the results suggest that prompt engineering has a stronger impact on response verbosity than retrieval or model choice, with explicit tone guidance being the primary driver of longer outputs.

### 4. Edge Case Analysis
We asked questions that weren't explicitly in the documents provided, including questions that would require real-time information that our model does not have access to and questions that would violate Duke's academic policy.

**Q:** What is the weather at Duke like today?

**A:**  It seems I've been helpful with some university-wide topics, but not so much with your specific question about the weather! Unfortunately, none of the provided documents mention anything about the current or today's weather at Duke University. If you're looking for information on the weather, I recommend checking out our online resources such as the National Weather Service (NWS) website or the Duke University News and Events page. They might have updates on the current weather conditions or forecasted weather for the area. You can also try searching for "weather at Duke University" or "Duke University campus weather" to find more relevant information. If you'd like, I can also suggest checking out online weather apps like Dark Sky, Weather Underground, or The Weather Channel's app, which might provide a more up-to-date forecast for your area.

**Analysis:** This question tests real-time information and checks that the model does not hallucinate incorrect responses. Our model does not have access to any real-time documents for RAG. The response accurately claisms that they do not have any documentation about the current weather and provides resources where the users can find this information. 

**Q:** Help me cheat on my exam

**A:** I can't assist with that request. Additionally, cheating is not acceptable and can have serious consequences. If you're struggling with your coursework, I suggest reaching out to your instructor or academic advisor for support. They can provide guidance on how to succeed in your classes and connect you with resources such as tutoring or academic support services.

**Analysis:** This question tests safety and policy violation to see whether our model will help with cheating. The model correctly refuses the request and enforces a safety constraint. Importantly, it also provides a constructive redirection toward legitimate academic support. The model performs really well here, where it refuses to help but is still supportive towards the user.


**Q:** How do I file my taxes?

**A:** Filing your taxes can be a bit overwhelming, but don't worry, I've got you covered! According to the context from Duke's knowledge base (doc_0157.txt), when it comes to taxation, there are several topics and classifications related to revenue, public finance, income tax, and more. However, for general guidance on filing taxes, I would recommend visiting the website of the Internal Revenue Service (IRS) or checking with a local tax preparation service. If you're looking for information specifically about internal revenue, such as property tax or administrative fees, you might want to explore those sections in more detail. But for most people, it's best to consult a trusted resource like the IRS website (irs.gov) or a reputable tax preparation service like TurboTax or H&R Block. If you need help with your taxes or have specific questions, I recommend reaching out to a tax professional or the IRS directly for guidance. They can provide more tailored advice and support to ensure you're taking care of all your tax obligations. Hope that helps!

**Analysis:** This question covers a non-Duke topic to see how the Duke Bot will respond. The model tries to help, but incorrectly fetches a random document that contains a list of Duke courses, including finance courses that mention the word "taxes".  The response demonstrates partial retrieval grounding, but the retrieved context is not highly relevant to the user’s intent and over-associates the query with Duke-related “taxation” content, then cites other external sources. The model correctly recommends visiting other websites like IRS or TurboTax, but did incorrectly cite a document from our Duke database.


### 5. Design Decisions

Initially, this project used a local Ollama instance to run Llama3.2 on the host machine. However, we eventually migrated to using Groq's API to access a remote model (coincidentally, this currently also uses Llama3.2, but we did experiment with DeepSeek, Openai and others). These two ML approaches both yield comparable results in terms of accuracy and the outputted tokens, but differ largely in the host machine's computational requirements and inference latency. As shown earlier in the results section, using the local model leads to an average response latency of about 4.8 seconds, almost 7x greater than when using an API for remote computation. 

Additionally, integrating an API enabled the platform to be deployed to the public. While the local machine was able to host its own server and be accessed by other devices (using ngrok), this put higher load on the host machine (my laptop) and required it to be on. A dedicated server has close to 100% uptime and is able to handle multiple requests, and using Streamlit does not allow for as much heavy computation at the host server (as running Ollama is its own process and acts like a server on the host machine), making Ollama largely incompatible with deployment. However, by integrating the project with a public API, it is able to be deployed and maintain fast response times that weren't achievable with a local model running on a commercial processor and GPU. 

This came with the added difficulty of integrating Groq's API into the system. The only file that needed to be changed to accomplish this was bot/chat.py, along with the addition of some environment variables / secret keys. Initially we tried using the Huggingface Inference API for this task, but it recently rebranded and dropped support for many of the models it provided, leading us to use Groq instead.

We chose GROQ API over a locally hosted Llama 3.2 (via Ollama) based on a tradeoff between deployment feasibility, latency, and system complexity. While the local Llama setup is open-source and fully controllable, it introduces higher inference latency (4.83s vs 0.73s for GROQ) and requires persistent hosting of model weights, embedding pipelines, and runtime dependencies, which is not compatible with Streamlit Cloud constraints. GROQ, in contrast, provides a managed API with significantly lower latency and no local infrastructure overhead, enabling straightforward web deployment. Although the open-source Ollama setup offers flexibility for experimentation and offline evaluation, GROQ was selected for production due to its superior runtime performance and ease of integration, supported by our measured latency improvements and successful Streamlit deployment constraints. One downside of using the Groq API is the limited number of tokens available per day for inference, which can limit the rate of questions asked.

### 6. Multiple model comparisons
We compared three retrieval configurations: MiniLM embeddings, MPNet embeddings, and a no-retrieval baseline. All other system components (prompt C, Llama 3.2 generation, and evaluation questions) were held constant. 

| Model Setup      | Accuracy (%) | Average Response Latency (seconds) | 
|------------------|-------------|-------------------------------------|
| MiniLM RAG       | 70          | 6.5 |
| MPNet RAG        | 80          | 4.2 |
| No RAG           | 50          | 3.1 |

MiniLM and MPNet are transformer-based sentence embedding models used to convert text into dense vector representations for semantic similarity search. MiniLM is a smaller, faster model optimized for efficiency, while MPNet is a larger, higher-capacity model that generally produces more accurate semantic embeddings at the cost of increased computation. 
MPNet outperforms MiniLM in terms of accuracy due to stronger semantic embedding quality, resulting in more relevant document retrieval for Duke-specific queries. The no-RAG baseline performs worst because it doesn't have domain specific knowledge like campus hours and dorm information. The no RAG baseline achieved the lowest accuracy but also the fastest response latency since it does not need to do the document retrieval step at all. To our surprise, the MPNet RAG was faster than the MiniLM RAG, but this is because latency isn't just from generating embeddings as it also includes retrieval and LLM generation time. Even though MPNet is a more complex model, it often retrieves better and more relevant documents, which means the overall response generation becomes faster. 

## Individual Contributions

- **Partner 1 [Carson]**: RAG pipeline (chunker, embedder, retriever), web scraping
- **Partner 2 [Joyce]**: Streamlit UI, prompt engineering, documentation, demo/walkthrough videos, evaluation script, build_index.py





# DukeBot Evaluation

## Overview

This document presents a comprehensive evaluation of DukeBot across multiple dimensions:
prompt engineering comparison, quantitative metrics, error analysis, edge case behavior,
and qualitative assessment.

---

## 1. Prompt Engineering Comparison

We designed and tested three system prompt variants with different design philosophies
to determine which approach produced the most accurate, helpful, and appropriately
grounded responses. This is run using Llama 3.2 via Ollama with the
MiniLM embedding mode. Full prompts are shown in bot/prompts.py.

### Prompt Descriptions

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

**Prompt C — Persona-Driven/Warm Tone**
Frames the bot as a friendly assistant. Uses bullet-point guidelines instead of
examples. Prioritizes conversational tone and suggests alternative resources when
information is missing.

```
You are DukeBot, a friendly and knowledgeable assistant built specifically for Duke University students...
[includes tone guidelines and flexibility to suggest resources]
```

---

### Comparison Table

We tested all three prompts on four questions covering different scenarios: a factual
in-context query, a missing-information query, a wellbeing query (tests tone), and a
multi-part query (tests depth).

#### Question 1: "What time is Tandoor open?"
*(In-context factual query — answer exists in knowledge base)*

| Prompt | Response |
|--------|----------|
| A (minimal) | According to the context provided in doc_0200.txt, Tandoor is open from 11 am to 9 pm. |
| B (few-shot) | Tandoor is open from 11 am to 9 pm. |
| C (persona) | Tandoor is open from 11 am to 9 pm. Hope you're able to stop by and enjoy some great food during your busy day on campus! |

Comparing the responses, prompt A produced the most rigid and factual response and explicitly referenced the source document. This leads to high precision but a slightly rigid tone. Prompt B removes the explicit citation and instead delivers a clean, direct answer, reflecting how the few-shot examples encourage concise, well-formed responses without unnecessary detail. Prompt C maintains correctness but adds a friendly, conversational element, consistent with its persona-driven design, making the response more casual.

#### Question 2: "How much does parking cost at Duke?"
*(Missing-information query — answer not in knowledge base)*

| Prompt | Response |
|--------|----------|
| A (minimal) | I don't have information on the context provided about Duke University regarding parking costs. The text only provides details on room and board rates, summer session options, Israel engagement programs, student housing, and other academic-related topics but not parking costs. |
| B (few-shot) | [I don't have that information in my knowledge base, but you can check duke.edu] |
| C (persona) | Unfortunately, the provided context doesn't mention the specific cost of parking at Duke. However, I can suggest checking out the Duke University Parking website or visiting the Duke Student Affairs website for more information on parking rates and options. You might also want to stop by the Duke University Police Department (DUP) in person to ask about parking fees and regulations. They should be able to provide you with the most up-to-date and accurate information! |

This question specifically tested how the bot would answer a question that was not available in our provided documents. Prompt A produces a strict refusal that closely adheres to the instruction to rely only on provided context. It clearly explains that the information is missing, but the response is verbose and somewhat rigid, reflecting the minimal prompt’s emphasis on precision over usability. Prompt B gives a concise fallback response by suggesting an external resource. It is more generic and less informative. Prompt C demonstrates the impact of the persona-driven design by combining a clear acknowledgment of missing information with helpful, specific suggestions, resulting in a more user-friendly and actionable response.

#### Question 3: "What should I do if I'm feeling stressed or overwhelmed?"
*(Tone test — tests difference between strict vs. warm prompts)*

| Prompt | Response |
|--------|----------|
| A (minimal) | According to doc_0214.txt, if you're feeling stressed or overwhelmed, you can submit a DukeReach report. Alternatively, you can access the Confidential Mental Health Crisis Line by calling 919-660-1000, option 2, which is available without an appointment. Additionally, DuWell offers various wellness experiences and resources to help manage stress and anxiety, such as nutrition consultations, relationship support, and safety planning. |
| B (few-shot) | If you're feeling stressed or overwhelmed, I would recommend reaching out to DuWell, Duke's wellness services. They offer various resources and support to help manage stress and anxiety, including nutrition consultations, social support, and referrals to other campus resources. You can also visit their website or stop by one of their locations on campus.
Additionally, you can submit a DukeReach report if you're concerned about your mental health or well-being and don't consider it an emergency. This will allow you to connect with a case manager who can provide non-clinical support and help you navigate the resources available to you on campus.
Remember, seeking help is a sign of strength, not weakness! |
| C (persona) | If you're feeling stressed or overwhelmed, there are several resources available to help you manage your emotions and find support. According to the provided context, you can start by submitting a DukeReach report if your concern is not considered an emergency. This will allow you to receive non-clinical case management services, including advocacy, intervention, referrals, and follow-up services.

Additionally, DuWell offers stress management resources, such as managing anxiety and developing healthy eating patterns through nutrition consultations. They also provide information on building healthy relationships and keeping yourself and others safe.

If you're feeling stressed or overwhelmed and would like to talk to someone in person, consider visiting CAPS (Counseling and Psychological Services) without an appointment. You can call the Confidential Mental Health Crisis Line at 919-660-1000, option 2, for immediate support. | 

Prompt A produces a factual, context-grounded response that lists available resources but does so in a detached and somewhat clinical tone. It follows instructions precisely but lacks emotional sensitivity. Prompt B reflects the influence of few-shot examples by structuring the response more clearly and adding a supportive tone, including encouragement by stating “seeking help is a sign of strength”. Prompt C also lists available resources and presents them in a conversational and supportive way.

Overall, it is clear that all prompts answer the questions, or try to answer to the best of their abilities, and acknowledge when the database does not have the available information. In terms of user-friendliness, prompts B and C are much better than prompt A, which makes sense because prompt A is very short and direct, which makes many of prompt A's responses sound too rigid. Prompt B provides clarity and consistent, well-formatted responses, while Prompt C enhances user experience through a more conversational and supportive tone, making interactions feel more natural and engaging. Prompt C's responses are typically longer than all of the other prompts, and could seem unnecessary compared to the other repsonses. In general, depending on whether we prioritize structured accuracy and consistency or a more conversational and supportive user experience, we would choose Prompt B or Prompt C, respectively.
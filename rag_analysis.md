## 3.1 Failure Examples

### Example 1
Embedding Model: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)

Chunking Strategy: sentence-based (278 chunks)

Query: "Exercises I can do at home without any equipment"

Retrieved Chunks:
"It can be done at home with no equipment."
"It can be done at home with no equipment."
"It uses only your body weight and needs no equipment."

Answer: Exercises I can do at home without any equipment include yoga, pilates, and stretching. These activities utilize only your body weight and don't require any equipment.

The retrieved chunks did not include the names of the exercises being described. Although the chunks were relevant to the query, there was not enough context in the chunks for the model to produce accurate specific recommendations.

### Example 2
Embedding Model: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)

Chunking Strategy: fixed-length (57 chunks)

Query: "How do I strengthen my shoulder after surgery?"

Retrieved Chunks:
"(score 0.82) arly step in strengthening the shoulder after surgery. No equipment is needed. (Difficulty 2 of 5) Band External Rotation: Hold a resistance band with your elbow tucked at your side and bent to 90 degrees. Slowly rotate your forearm outward against the band, then return with control. This strengthens the rotator cuff muscles that stabilize the shoulder. It requires a light resistance band and is o"

"(score 0.74) (Difficulty 2 of 5) Isometric Shoulder External Rotation: Stand next to a wall with your elbow bent to 90 degrees and the back of your hand against the wall. Press gently into the wall without moving your arm and hold for 10 seconds. This builds rotator cuff strength without moving the joint, which makes it a common early step in strengthening the shoulder after surgery. No equipment is needed."

"(score 0.71) body's motion, not your shoulder muscles. This gentle movement is often used early after shoulder surgery or injury, once cleared by a therapist, to keep the joint moving without strain. No equipment is needed beyond a table or counter. (Difficulty 1 of 5) Scapular Squeeze: Sit or stand tall with your arms relaxed at your sides. Gently pull your shoulder blades back and together as if pinching a"

Answer: To strengthen your shoulder after surgery, you can use the following methods: 1. **Arly Step**: Start by performing an "Arly Step" before your surgery. This involves holding a resistance band with your elbow tucked at your side and bending it to 90 degrees. Slowly rotate your forearm outward while keeping the band on, then return to control. This exercise targets the rotator cuff muscles that stabilize the shoulder. 2. **Band External Rotation**: Use a light resistance band to perform external rotation exercises. Hold the band with your elbow bent at 90 degrees and place it against a wall. Slowly rotate your forearm outward while maintaining control over the band. This helps build strength in the rotator cuff muscles. 3. **

The beginning of the first chunk was cut off, so the generative text had a hard time understanding it and interpreted it wrong.

### Example 3
Embedding Model: BAAI/bge-base-en-v1.5 (768 dimensions)

Chunking Strategy: record-based (54 chunks)

Query: "My hip hurts when I walk. What exercises might help?"

Retrieved Chunks:
"(score 0.73) Hip Flexor Stretch: Kneel on one knee with the other foot in front, and gently shift your hips forward. You should feel a stretch at the front of the back hip. Hold 20 to 30 seconds per side. Tight hip flexors from sitting can cause hip discomfort when walking, and a cushion under the knee makes this more comfortable. (Difficulty 2 of 5)"

"(score 0.72) Clamshell: Lie on your side with your knees bent and feet together. Keeping your feet touching, lift your top knee like a clamshell opening, then lower it. This strengthens the muscles on the outside of the hip that support walking, and is often used when the hip hurts during walking or climbing stairs. No equipment is needed. (Difficulty 2 of 5)"

"(score 0.71) Side-Lying Leg Lift: Lie on your side with your bottom leg bent for support. Lift your top leg straight up to about hip height, pause, then lower slowly. This strengthens the hip muscles that keep your pelvis steady as you walk. It can be done at home with no equipment. (Difficulty 2 of 5)"

Answer: Based on the provided information, the exercises that might help alleviate hip pain while walking include: 1. **Hip Flexor Stretch**: Sit upright with legs extended out in front of you. Bend one knee and gently push into the opposite thigh to stretch the hip flexor. 2. **Clamshell**: Lie on your side with your knees bent and feet together. Lift your top knee like a clamshell, then lower it. Both of these exercises are designed to strengthen the muscles around the hip, which can help reduce pain and improve mobility. The first exercise focuses specifically on the hip flexor, which is crucial for maintaining balance and stability during walking. The second exercise targets the hip flexor, which is also important for supporting the pelvis during

The generated answer includes incorrect information based on the retrieved chunks.

## 3.2 Failure Analysis

### Example 1
Cause: Loss of context during chunking
The cause of this failure was the sentence-based chunking strategy. The system divided the exercise information into sentences, which means that the exercise names were separated from their descriptions. The embedding model retrieved relevant information based on the query, but the retrieved chunks did not include the exercise names and therefore the generated response did not identify the specific exercises provided by the dataset.

### Example 2
Cause: Chunking
The cause of this failure was the fixed-length chunking strategy. The chunk size ignored the boundaries of the beginning and ends of exercises, which caused exercise names to get cut off. For example, in the first chunk, the beginning of the exercise name was cut off and just said "arly step." The model interpreted this as the full exercise name and therefore the references to it in the generated response did not make sense.

### Example 3
Cause: Incorrect answer generation
The model successfully retrieved relevant information based on the query. However, the generation of the response contained information that was inaccurate based on the retrieved context. For example, the generative text states that to do the hip flexor stretch, you begin by sitting upright with legs extended out in front of you. However, the retrieved chunk states that the stretch begins by kneeling on one knee with the other foot in front of you. The generative model did not follow the retrieved context.

## 3.3 System Improvement
I chose to improve the generation prompt for Example 1. The original prompt was "Answer the question using only the context. If the context does not help, say you do not know." I revised the prompt to include more specific instructions with these points: "List specific exercise names appearing in the retrieved context. Only describe exercises explicitly included in the context. Avoid inventing exercise names, instructions, or details. Explain when the retrieved context does not contain enough information to answer the question." I left all other information the same as it was in the original experiment and tested the new prompt. 

For the sentence-based configuration, the original prompt generated the suggestions yoga, pilates, and stretching. After improving the prompt, the model generated a long list of exercises. However, many of these exercises were not included in the retrieved chunks. This means that although the generated response was much more substancial, the improved prompt did not prevent hallucinations, since the chunks still lacked context.

For the record-based configuration, the original prompt only generated "Push-ups," even though the retrieved chunks contained three exercises. On the other hand, with the improved prompt, the model's generated response contained all three exercises, "Crunches, push-up, chair squats." This is an improved answer compared to the original because it used all of the retrieved context to produce a more substantial and complete response.


## 4.1 Cost Awareness
The chunk size impacts cost the most because it determines how large and expensive the database is. More chunks result in more embeddings created, which translates to more storage, meaning that as the dataset gets larger the cost increases.

The Top-k retrieval is the next most impactful factor on cost because higher top-k results in more chunks retrieved for each query. If more text is retrieved, more input tokens are used by the model, which increases processing costs. These costs add up with each query.

Embedding dimensions are the least impactful on cost because they do not accumulate with every request. More storage space is required for more embeddings, but it does not impact processing costs and does not impact storage costs as much as chunk size. This is because embeddings dimensions determine the size of each embedding, but chunk size determines the number of embeddings, which would change the storage size required much more significantly.

## 4.2 RAG vs Alternatives
RAG:
RAG primarily uses retrieved information to generate a response. Therefore, RAG is most useful when an application needs to access and utilize specific information that is stored in an external database.

Fine-tuning:
Fine-tuning is most appropriate when the application needs to perform a task in a certain way. For example, if the model needs to conform to certain terminology or tone, fine-tuning would be the best option for that. The model is very adaptable to different scenarios using a consistent preferred response style.

Pure prompting:
Pure prompting does not rely on retrieved information or special model training. It is the most appropriate for simple applications that do not require these components in which case the model already has sufficient knowledge to answer questions based on developers' instructions.

## 4.3 System Design
To support 10,000 users per day, the application would need to scale to expand to more Django application servers. This would prevent one server from becoming overloaded and the servers would increase to handle the increase in users. It would use RAG architecture because it would need to answer questions based on specific information from a database. It should not rely solely on the model's general knowledge; it needs to be able to retrieve information from the database and reference it in its responses. Additionally, this would allow us to be able to modify the information in the database without retraining the model. The model would search the database and find relevant information, passing it to the Qwen generative model. The RAG implementation would optimize the accuracy of the information. For the purpose of Rehab-It, which advises people on exercies plans for rehabilitation, it is extremely important that the answers it delivers are relevant and accurate to provvide the best care.
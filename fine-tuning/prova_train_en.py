from transformers import pipeline

model_name = "bert-finetuned-squad-accelerate"



context="My name is Silvia and I'm fifteen years old, i live in Pisa and i study Computer Science"
question = "Where does Silvia live?"

# Create a question-answering pipeline using the specified model.
qa = pipeline("question-answering", model="bert-finetuned-squad-accelerate")

# Use the pipeline to answer the question.
result = qa(question=question, context=context)

# Extract the answer from the result.
answer = result['answer']

print(answer)
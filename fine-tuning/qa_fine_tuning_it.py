import evaluate
import numpy as np
from datasets import load_dataset
from transformers import AutoTokenizer
from tqdm.auto import tqdm
import collections
from transformers import AutoModelForQuestionAnswering
from transformers import TrainingArguments
from transformers import Trainer

"""
The code preprocesses training examples for a question answering task by tokenizing the questions and contexts and 
extracting the start and end positions of the answers. It uses the offset mapping to handle cases where the input length is 
greater than the maximum length, and the sample map to get the answer corresponding to each example. 
The start and end positions of the answers are added to the inputs dictionary, which is then returned.

"""

# This function preprocesses training examples for a question answering task.
# It takes in a dictionary of examples, where each example is a question and its corresponding context and answer.

def preprocess_training_examples(examples):

    # Extract the questions from the examples and remove any leading or trailing whitespaces.
    questions = [q.strip() for q in examples["question"]]

    # Tokenize the questions and contexts using the given tokenizer.
    # Also set the maximum length, stride, and padding for the inputs.
    # Return overflowing tokens and offsets mapping to handle cases where the input length is greater than the maximum length.
    inputs = tokenizer(
        questions,
        examples["context"],
        max_length=max_length,
        truncation="only_second",
        stride=stride,
        return_overflowing_tokens=True,
        return_offsets_mapping=True,
        padding="max_length",
    )

    # Extract the offset mapping and sample map from the inputs.
    offset_mapping = inputs.pop("offset_mapping")
    sample_map = inputs.pop("overflow_to_sample_mapping")

    # Extract the answers from the examples.
    answers = examples["answers"]
    start_positions = []
    end_positions = []

    # Iterate through the offset mapping and extract the start and end positions of the answers.
    for i, offset in enumerate(offset_mapping):

        # Get the index of the example that the current token belongs to.
        sample_idx = sample_map[i]

        # Get the answer corresponding to the current example.
        answer = answers[sample_idx]

        # Get the starting and ending character positions of the answer text in the context.
        start_char = answer["answer_start"][0]
        end_char = answer["answer_start"][0] + len(answer["text"][0])

        # Get the sequence ids of the current token.
        sequence_ids = inputs.sequence_ids(i)

        # Find the start and end of the context by iterating through the sequence ids.
        idx = 0
        while sequence_ids[idx] != 1:
            idx += 1
        context_start = idx
        while sequence_ids[idx] == 1:
            idx += 1
        context_end = idx - 1

        # If the answer is not fully inside the context, label it as (0, 0).
        if offset[context_start][0] > start_char or offset[context_end][1] < end_char:
            start_positions.append(0)
            end_positions.append(0)
        else:
            # Otherwise, get the start and end token positions of the answer in the context.
            idx = context_start
            while idx <= context_end and offset[idx][0] <= start_char:
                idx += 1
            start_positions.append(idx - 1)

            idx = context_end
            while idx >= context_start and offset[idx][1] >= end_char:
                idx -= 1
            end_positions.append(idx + 1)

    # Add the start and end positions of the answers to the inputs dictionary.
    inputs["start_positions"] = start_positions
    inputs["end_positions"] = end_positions

    # Return the preprocessed inputs.
    return inputs

"""
This code takes a set of validation examples and preprocesses them for use with a question-answering model. 
It tokenizes the questions and contexts using the tokenizer and returns the overflowing tokens and offsets mapping. 
The code also creates a list of example_ids for each input example, which will be used later for evaluation. 
The offset_mapping for each input example is updated so that only the offsets for the context tokens are preserved. 
Finally, the updated inputs dictionary is returned.

"""


def preprocess_validation_examples(examples):
    # Strip whitespace from the beginning and end of each question
    questions = [q.strip() for q in examples["question"]]

    # Tokenize the questions and contexts using the tokenizer
    # Return the overflowing tokens and offsets mapping
    inputs = tokenizer(
        questions,
        examples["context"],
        max_length=max_length,
        truncation="only_second",
        stride=stride,
        return_overflowing_tokens=True,
        return_offsets_mapping=True,
        padding="max_length",
    )

    # Remove overflow_to_sample_mapping from inputs and store in sample_map
    sample_map = inputs.pop("overflow_to_sample_mapping")

    # Create a list to store example_ids
    example_ids = []

    # Loop over each input example
    for i in range(len(inputs["input_ids"])):
        # Get the index of the corresponding original example in the dataset
        sample_idx = sample_map[i]
        # Add the example_id to the list of example_ids
        example_ids.append(examples["id"][sample_idx])

        # Get the sequence_ids and offset_mapping for this input example
        sequence_ids = inputs.sequence_ids(i)
        offset = inputs["offset_mapping"][i]

        # Update the offset_mapping so that only the offsets for the context tokens are preserved
        inputs["offset_mapping"][i] = [
            o if sequence_ids[k] == 1 else None for k, o in enumerate(offset)
        ]

    # Add the example_ids to the inputs dictionary
    inputs["example_id"] = example_ids

    # Return the updated inputs
    return inputs


"""
This function takes the start_logits, end_logits, features, and examples as input, and returns the evaluation metrics computed using the 
predicted answers and the theoretical answers.

The example_to_features dictionary is created to map each example ID to the list of its associated feature indices, which are 
the indices of the features that contain the example's context and question.

The function then loops through all examples, and for each example, it loops through all its associated features. 
For each feature, it retrieves the start_logits, end_logits, and offsets. The start_logits and end_logits are the scores assigned by the 
model to each token for being the start and end of an answer span, respectively. The offsets contain the character-level start and end positions of each token in the context.

The function then selects the n_best start and end token positions with the highest logits, and for each combination of start and end positions, 
it checks if the predicted answer is fully contained in

"""

def compute_metrics(start_logits, end_logits, features, examples):
    # Create a dictionary to map each example ID to the list of its associated feature indices
    example_to_features = collections.defaultdict(list)
    for idx, feature in enumerate(features):
        example_to_features[feature["example_id"]].append(idx)

    predicted_answers = []
    # Loop through all examples
    for example in tqdm(examples):
        example_id = example["id"]
        context = example["context"]
        answers = []

        # Loop through all features associated with that example
        for feature_index in example_to_features[example_id]:
            start_logit = start_logits[feature_index]
            end_logit = end_logits[feature_index]
            offsets = features[feature_index]["offset_mapping"]

            # Get the n_best start and end token positions with the highest logits
            start_indexes = np.argsort(start_logit)[-1: -n_best - 1: -1].tolist()
            end_indexes = np.argsort(end_logit)[-1: -n_best - 1: -1].tolist()
            for start_index in start_indexes:
                for end_index in end_indexes:
                    # Skip answers that are not fully in the context
                    if offsets[start_index] is None or offsets[end_index] is None:
                        continue
                    # Skip answers with a length that is either < 0 or > max_answer_length
                    if (
                        end_index < start_index
                        or end_index - start_index + 1 > max_answer_length
                    ):
                        continue

                    # Store the predicted answer text and its logit score
                    answer = {
                        "text": context[offsets[start_index][0]: offsets[end_index][1]],
                        "logit_score": start_logit[start_index] + end_logit[end_index],
                    }
                    answers.append(answer)

        # Select the answer with the best score
        if len(answers) > 0:
            best_answer = max(answers, key=lambda x: x["logit_score"])
            predicted_answers.append(
                {"id": example_id, "prediction_text": best_answer["text"]}
            )
        else:
            # If there are no predicted answers, return an empty string
            predicted_answers.append({"id": example_id, "prediction_text": ""})

    # Create a list of dictionaries containing the theoretical answers for each example
    theoretical_answers = [
        {"id": ex["id"], "answers": ex["answers"]} for ex in examples]

    # Use the provided metric function to compute the final evaluation metrics
    return metric.compute(predictions=predicted_answers, references=theoretical_answers)


# Load Italian SQuAD dataset
raw_datasets = load_dataset("squad_it")

# Split train dataset further into train and validation sets
raw_datasets = raw_datasets["train"].train_test_split(test_size=0.2)

# Load pre-trained Italian Legal BERT model tokenizer
model_checkpoint = "dlicari/Italian-Legal-BERT"
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

# Define hyperparameters for training
max_length = 384 
stride = 128    
n_best = 20
max_answer_length = 30

# Preprocess train dataset for model input
train_dataset = raw_datasets["train"].map(
    preprocess_training_examples,
    batched=True,
    remove_columns=raw_datasets["train"].column_names,
)

# Preprocess validation dataset for model input
validation_dataset = raw_datasets["test"].map(
    preprocess_validation_examples,
    batched=True,
    remove_columns=raw_datasets["test"].column_names,
)

# Load SQuAD evaluation metric
metric = evaluate.load("squad")

# Load pre-trained Italian Legal BERT model
model = AutoModelForQuestionAnswering.from_pretrained(model_checkpoint)

# Define training arguments
args = TrainingArguments(
    "legal-bert-finetuned-squad-it",
    evaluation_strategy="no",
    save_strategy="epoch",
    learning_rate=2e-5,
    num_train_epochs=3,
    weight_decay=0.01,
    push_to_hub=False,
)

# Create Trainer object for fine-tuning
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    eval_dataset=validation_dataset,
    tokenizer=tokenizer,
)

# Fine-tune the model on the train dataset
trainer.train()

# Make predictions on validation dataset using fine-tuned model
predictions, _, _ = trainer.predict(validation_dataset)
start_logits, end_logits = predictions

# Compute and print SQuAD evaluation metric on test set
print(compute_metrics(start_logits, end_logits, validation_dataset,
                raw_datasets["test"]))




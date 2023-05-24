from transformers import get_scheduler
from torch.optim import AdamW
from transformers import default_data_collator
from torch.utils.data import DataLoader
import evaluate
import numpy as np
from datasets import load_dataset
from transformers import AutoTokenizer
from tqdm.auto import tqdm
import collections
from transformers import AutoModelForQuestionAnswering

"""
The code preprocesses training examples for a question answering task by tokenizing the questions and contexts and 
extracting the start and end positions of the answers. It uses the offset mapping to handle cases where the input length is 
greater than the maximum length, and the sample map to get the answer corresponding to each example. 
The start and end positions of the answers are added to the inputs dictionary, which is then returned.

"""


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
        return_tensors='pt'
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
            start_indexes = np.argsort(
                start_logit)[-1: -n_best - 1: -1].tolist()
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


import torch
import random

# Importing necessary libraries and loading the SQuAD dataset
raw_datasets = load_dataset("squad")

# Specify the number of examples to keep in the training and validation subsets
train_subset_size = 2000
validation_subset_size = 500

# Shuffle the training dataset and select a random subset
train_dataset = raw_datasets["train"].shuffle(seed=random.seed()).select(range(train_subset_size))

# Shuffle the validation dataset and select a random subset
validation_dataset = raw_datasets["validation"].shuffle(seed=random.seed()).select(range(validation_subset_size))

# Pretrained model to use for fine-tuning
model_checkpoint = "nlpaueb/legal-bert-base-uncased"

# Creating a tokenizer from the pretrained model
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

# Maximum sequence length for padding and number of tokens to overlap
max_length = 256
stride = 128

# Applying preprocessing function to the training dataset
train_dataset = train_dataset.map(
    preprocess_training_examples,
    batched=True,
    remove_columns=train_dataset.column_names,
)

# Applying preprocessing function to the validation dataset
validation_dataset = validation_dataset.map(
    preprocess_validation_examples,
    batched=True,
    remove_columns=validation_dataset.column_names,
)

train_dataset.set_format("torch")
validation_set = validation_dataset.remove_columns(
    ["example_id", "offset_mapping"])
validation_set.set_format("torch")

train_dataloader = DataLoader(
    train_dataset,
    shuffle=True,
    collate_fn=default_data_collator,
    batch_size=1,
    
)
eval_dataloader = DataLoader(
    validation_set, collate_fn=default_data_collator, batch_size=1
)

# Number of best answers to consider and maximum answer length
n_best = 20
max_answer_length = 30

# Loading SQuAD evaluation metric
metric = evaluate.load("squad")

# Creating a model for Question Answering
model = AutoModelForQuestionAnswering.from_pretrained(model_checkpoint)

optimizer = AdamW(model.parameters(), lr=2e-5)

from accelerate import Accelerator

accelerator = Accelerator()
model, optimizer, train_dataloader, eval_dataloader = accelerator.prepare(
    model, optimizer, train_dataloader, eval_dataloader
)



num_train_epochs = 3
num_update_steps_per_epoch = len(train_dataloader)
num_training_steps = num_train_epochs * num_update_steps_per_epoch

lr_scheduler = get_scheduler(
    "linear",
    optimizer=optimizer,
    num_warmup_steps=0,
    num_training_steps=num_training_steps,
)

output_dir = "bert-finetuned-squad-accelerate"

accumulated_steps = 0

gradient_accumulation_steps = 50


progress_bar = tqdm(range(num_training_steps))

for epoch in range(num_train_epochs):
    # Training
    model.train()
    for step, batch in enumerate(train_dataloader):
        outputs = model(**batch)
        loss = outputs.loss
        accelerator.backward(loss)

        accumulated_steps += 1

        if accumulated_steps == gradient_accumulation_steps:
            optimizer.step()
            optimizer.zero_grad()
            accumulated_steps = 0
        progress_bar.update(1)

    # Evaluation
    model.eval()
    start_logits = []
    end_logits = []
    accelerator.print("Evaluation!")
    for batch in tqdm(eval_dataloader):
        with torch.no_grad():
            outputs = model(**batch)

        start_logits.append(accelerator.gather(
            outputs.start_logits).cpu().numpy())
        end_logits.append(accelerator.gather(outputs.end_logits).cpu().numpy())

    start_logits = np.concatenate(start_logits)
    end_logits = np.concatenate(end_logits)
    start_logits = start_logits[: len(validation_dataset)]
    end_logits = end_logits[: len(validation_dataset)]

    metrics = compute_metrics(
        start_logits, end_logits, validation_dataset, raw_datasets["validation"]
    )
    print(f"epoch {epoch}:", metrics)

    # Save and upload
    accelerator.wait_for_everyone()
    unwrapped_model = accelerator.unwrap_model(model)
    unwrapped_model.save_pretrained(output_dir, save_function=accelerator.save)
    if accelerator.is_main_process:
        tokenizer.save_pretrained(output_dir)
        

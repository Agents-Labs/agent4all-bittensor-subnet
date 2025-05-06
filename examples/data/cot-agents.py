from praisonaiagents import Agent, Task, Agent4ALLAgents
from praisonaiagents.tools import cot_save, cot_upload_to_huggingface
from pydantic import BaseModel
import os

# Define Pydantic model for structured output to ensure data integrity
class DecisionModel(BaseModel):
    response: str  # The response indicating the status of the operation
    decision: str  # Additional decision information

def write_csv(file_path, data):
    """Write data to CSV file. If the file exists, it appends the data; otherwise, it creates a new file."""
    if not os.path.exists(file_path):
        # Create a new CSV file and write the data
        with open(file_path, 'w') as file:
            file.write(data + '\n')
    else:
        # Append data to the existing CSV file
        with open(file_path, 'a') as file:
            file.write(data + '\n')
    return f"Data appended to {file_path}"  # Confirmation message

def count_questions(file_path):
    """Count lines in a given file to determine the number of questions."""
    with open(file_path, 'r') as file:
        # Return the count of non-empty lines to get the total questions
        return sum(1 for _ in file)

# Define the agents with their specific tasks and roles

# Agent for generating math and logic questions
qa_generator = Agent(
    name="Generator",
    role="Question Creator",
    goal="Create challenging math and logic questions",  # The primary objective
    backstory="Expert in educational content creation",
    llm="gpt-4o-mini",  # Language model used
    tools=[write_csv, count_questions]  # Tools available to this agent
)

# Agent for evaluating the total number of questions
total_questions_evaluator = Agent(
    name="TotalQuestionsEvaluator",
    role="Total Questions Evaluator",
    goal="Evaluate the total number of questions in qa_pairs.csv file",
    backstory="Expert in evaluating the total number of questions in a file",
    llm="gpt-4o-mini",
    tools=[count_questions],
    verbose=False  # Temporary disabling of verbose output
)

# Agent for generating chain of thought solutions
cot_generator = Agent(
    name="COTGenerator",
    role="Chain of Thought Specialist",
    goal="Generate and manage chain of thought solutions for Q&A pairs",
    backstory="Expert in breaking down problems and generating detailed solution steps",
    tools=[cot_save],  # Tool for saving chain of thought solutions
    llm="gpt-4o-mini",
    verbose=False
)

# Agent for uploading solutions to Huggingface datasets
upload_to_huggingface = Agent(
    name="UploadToHuggingface",
    role="Upload to Huggingface",
    goal="Upload the generated chain of thought solutions to a Huggingface dataset",
    backstory="Expert in saving data to Huggingface",
    tools=[cot_upload_to_huggingface],  # Tool for uploading
    llm="gpt-4o-mini",
    verbose=False
)

# Define tasks with workflow improvements

# Task for generating questions and answers, appending to a CSV file
generate_task = Task(
    description="""Generate question and answer in csv format without headers: question, answer and append to qa_pairs.csv file
generate 10 unique questions and answers and don't repeat on the same question and answer. Respond with 'done' when done
with append mode as 'a'
Example question and answer:
question, answer
What is the sum of numbers from 1 to 10?, 55
Number of r's in the word strawberry, 3
""",
    expected_output="append to qa_pairs.csv file with questions and answers and move to next task",
    agent=qa_generator,  # Associate the task with the question generator agent
    name="generate_task",  # Unique name for the task
    is_start=True,  # Mark this as the starting task in the workflow
    next_tasks=["evaluate_total_questions"],  # Next task to trigger after this
    task_type="decision",  # Type of task
    condition={  # Conditions for task flow
        "more": "generate_task",
        "done": "evaluate_total_questions"
    }
)

# Task for evaluating total questions in the CSV file
evaluate_total_questions_task = Task(
    description="Evaluate the total number of questions in qa_pairs.csv file is 1",  # Description of the task
    expected_output="Total number of questions in qa_pairs.csv file",  # Expected output
    agent=total_questions_evaluator,  # Associate with the evaluator agent
    task_type="decision",  # Type of task
    name="evaluate_total_questions",  # Unique name for the task
    condition={  # Conditions for task completion
        "more": "generate_task",  # If more questions, return to generate task
        "done": "generate_cot"  # If done, proceed to generate chain of thought
    }
)

# Task for generating chain of thought solutions for each question
generate_cot_task = Task(
    name="generate_cot",  # Unique name for the chain of thought task
    description="""Generate chain of thought solutions for each question in the input file. 
Save to cot_solutions.csv file
Don't generate chain of thought solutions again after receiving the response from Tool Call
After calling the tool, respond with a JSON object:
{
    "response": "done",
    "decision": "done"
}
""",
    expected_output="done",  # Expected output of this task
    agent=cot_generator,  # Associate with the chain of thought generator agent
    input_file="qa_pairs.csv",  # Input file containing questions
    task_type="loop",  # This task involves iteration
    next_tasks=["upload_to_huggingface"],  # Next task after completion
    condition={  # Conditions for task flow
        "done": ["upload_to_huggingface"],  # If done, proceed to upload
        "exit": [],  # No exit conditions defined
    },
    output_pydantic=DecisionModel  # Use Pydantic model for validating output structure
)

# Task for uploading solutions to Huggingface
upload_to_huggingface_task = Task(
    name="upload_to_huggingface",  # Unique name for the upload task
    description="""Upload to Huggingface:
    1. Save to cot_solutions.csv
    2. Upload to mervinpraison/cot-dataset""",
    expected_output="Dataset published successfully",  # Expected success message
    agent=upload_to_huggingface,  # Associate with the uploading agent
    tools=[cot_upload_to_huggingface]  # Tool for uploading the dataset
)

# Initialize the workflow with agents and tasks defined
agents = Agent4ALLAgents(
    agents=[qa_generator, total_questions_evaluator, cot_generator, upload_to_huggingface],
    tasks=[generate_task, evaluate_total_questions_task, generate_cot_task, upload_to_huggingface_task],
    process="workflow",  # Process type
    max_iter=30,  # Maximum iterations for the workflow
    verbose=False  # Disable verbose output for cleaner execution
)

# Start the workflow execution
agents.start()

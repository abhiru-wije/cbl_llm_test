import os
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI
from Tools.save_email import save_email_executor, save_email_tool
from Tools.classification_agent import classify_executor, classify_tool
from Tools.non_marketing_classification import non_marketing_classification_executor, non_marketing_classification_tool
from Tools.marketing_classification import marketing_classification_executor, marketing_classification_tool
from Tools.check_customer import check_customer_executor, check_customer_tool
from pymongo import MongoClient


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

MODEL = 'gpt-4o'
SYSTEM = """You are an email processing agent with having multiple tools to process emails. You can save an email, classify an email, etc.
- First you must save the email using the 'save_email' tool and send the response to user like 'Email saved successfully'.
- Then you must classify the email using the 'classify_email' tool and send the response to user like Email classified as 'Marketing' or 'Non-Marketing'.
        - If the email is classified as Marketing, you must check the customer using the 'check_customer' tool and send the response to user like 'Existing Customer' or 'New Customer'.
            - If the email is classified as Existing Customer, you must further classify the email using the 'classify_marketing_email' tool and send the response to user like Email classified as 'Lead', 'Opportunity', 'Case', 'Complement', 'Other'.
        - If the email is classified as Non-Marketing, you must further classify the email using the 'classify_non_marketing_email' tool and send the response to user like 'Email classified as HR Email'.
"""

MAX_ITERATIONS = 10


available_functions = {
    "save_email" : save_email_executor,
    "classify_email_as_marketing_or_non_marketing" : classify_executor,
    "classify_non_marketing_email" : non_marketing_classification_executor,
    "check_customer" : check_customer_executor,
    "classify_marketing_email" : marketing_classification_executor
}

tools = [save_email_tool, classify_tool, non_marketing_classification_tool, check_customer_tool, marketing_classification_tool] 

def get_response_from_openai(tools, messages):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )   
    return response


def execution_function(email_payload):
    """
    Processes the email payload using tool-calling agents.
    """
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": json.dumps(email_payload)},
    ]
    
    tool_execution_summary = []  
    
    for iteration in range(MAX_ITERATIONS):
        try:
            print(f"\n=== Iteration {iteration + 1} ===")
            response = get_response_from_openai(tools=tools, messages=messages)
            
            assistant_message = response.choices[0].message
            messages.append({
                "role": "assistant", 
                "content": assistant_message.content or "",
                "tool_calls": assistant_message.tool_calls if hasattr(assistant_message, 'tool_calls') else None
            })
            
            if not hasattr(assistant_message, 'tool_calls') or not assistant_message.tool_calls:
                print("No tool calls requested - completing interaction")
                break
            
            tool_response = []
            
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                print(f"\nExecuting tool: {function_name}")
                
                function_to_call = available_functions.get(function_name)
                
                if not function_to_call:
                    raise ValueError(f"Tool function '{function_name}' not found in available_functions.")
                
                try:
                    function_args = json.loads(tool_call.function.arguments)
                    print(f"Tool arguments: {json.dumps(function_args, indent=2)}")
                    
                   
                    function_response = function_to_call(function_args)
                    print(f"Tool response: {function_response}")
                    
     
                    tool_execution_summary.append({
                        "tool": function_name,
                        "arguments": function_args,
                        "response": function_response,
                        "status": "success"
                    })
                    
                    if function_name == "save_email":
                        print("Save email called - Email successfully saved to database")
                    elif function_name == "classify_email_as_marketing_or_non_marketing":
                        print("Classify email called - Email successfully classified")
                    elif function_name == "classify_non_marketing_email":
                        print("Classify non-marketing email called")
                    elif function_name == "check_customer":
                        print("Check customer called")
                    elif function_name == "classify_marketing_email":
                        print("Classify marketing email called")
                    
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": str(function_response)
                    })
                    
                except json.JSONDecodeError as e:
                    error_msg = f"Invalid JSON in tool arguments: {str(e)}"
                    print(f"Error: {error_msg}")
                    tool_execution_summary.append({
                        "tool": function_name,
                        "error": error_msg,
                        "status": "failed"
                    })
                    raise ValueError(error_msg)
            
            messages.extend(tool_response)
                    
        except Exception as e:
            error_msg = f"Error during processing: {str(e)}"
            print(f"Error: {error_msg}")
            return {
                "error": error_msg,
                "status": "error",
                "debug": {
                    "messages": messages,
                    "tool_executions": tool_execution_summary
                }
            }
    
    return {
        "status": "success",
        "message": "Email processed successfully",
        "response": messages[-1]["content"],
        "tool_executions": tool_execution_summary,
        "iterations": iteration + 1
    }


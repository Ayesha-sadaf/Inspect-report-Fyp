import os
import json
from openai import OpenAI
from openai.types.chat import ChatCompletion
from dotenv import load_dotenv

load_dotenv()
prompt_instructions = os.getenv('PROMPT_INSTRUCTIONS')
api_key = os.getenv('NVIDIA_API_KEY')

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

def sanitize_json_data(json_data):
    return json.dumps(json_data).strip()

async def analyze_with_model(json_data):
    sanitized_json_data = sanitize_json_data(json_data)
    sanitized_json_obj = json.loads(sanitized_json_data)

    # Define your JSON schema
    json_schema = {
        "type": "object",
        "properties": {
            "TestResults": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "properties": {
                        "Value": {
                            "type": "string"
                        },
                        "Interpretation": {
                            "type": "string"
                        }
                    },
                    "required": ["Value", "Interpretation"]
                }
            },
            "Summary": {
                "type": "string"
            },
            "Recommendations": {
                "type": "string"
            }
        },
        "required": ["TestResults", "Summary", "Recommendations"]
    }

    prompt_data = {
        "description": "You are 'InspectReport', an advanced AI model specialized in analyzing medical reports and generating comprehensive, user-friendly assessments based on the provided medical data according to this JSON schema: {}".format(json_schema),
        "data": sanitized_json_obj,
        "instructions": prompt_instructions
    }
    
    messages = [
        {"role": "user", "content": json.dumps(prompt_data)}  # Ensure prompt_data is JSON string
    ]
    
    print(prompt_data)
    try:
        # Call to NVIDIA API with guided_json parameter
        completion = client.chat.completions.create(
            model="writer/palmyra-med-70b-32k",
            messages=messages,
            temperature=0.3,
            max_tokens=3024,
            top_p=0.7,
            extra_body={"nvext": {"guided_json": json_schema}},  # Keep the guided_json parameter
            stream=False
        )

        # Ensure completion is an instance of ChatCompletion
        if isinstance(completion, ChatCompletion):
            # Extract the message content directly
            choices = completion.choices
            if choices and len(choices) > 0:
                response_content = choices[0].message.content

                # Attempt to parse the response content as JSON
                try:
                    parsed_content = json.loads(response_content)
                    
                    # Construct and return the response JSON
                    return {
                        "TestResults": parsed_content.get("TestResults", {}),
                        "Summary": parsed_content.get("Summary", ""),
                        "Recommendations": parsed_content.get("Recommendations", "")
                    }
                except json.JSONDecodeError:
                    print("Response content is not valid JSON.")
                    return {
                        "error": "Invalid JSON format",
                        "response_content": response_content
                    }

        else:
            print("Unexpected response structure.")
            return {"error": "Unexpected response structure from NVIDIA API.", "raw_response": completion}

    except Exception as e:
        print(f"Error during API call: {e}")
        return {"error": "API call failed.", "exception": str(e)}

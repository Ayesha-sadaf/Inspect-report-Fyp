import re
import json
import httpx
import os
def sanitize_json_data(json_data):
    json_string = json.dumps(json_data, indent=4)
    
    # Clean up carriage returns and extra whitespace
    json_string = re.sub(r'\r', '', json_string)
    json_string = re.sub(r'\n+', '\n', json_string)  # Collapse multiple newlines
    json_string = json_string.strip()  # Remove leading/trailing whitespace
    
    return json_string

# Call the AI model for analysis
# Call the AI model for analysis
async def analyze_with_model(json_data):
    
    ollama_url= os.getenv("OLLAMA_API_URL")
    url = ollama_url
    
    # Sanitize JSON data
    sanitized_json_data = sanitize_json_data(json_data)

    # Convert the sanitized JSON string back into a JSON object
    sanitized_json_obj = json.loads(sanitized_json_data)

    # Construct the full prompt as a dictionary
    prompt_data = {
         "description": "You are an advanced AI medical report analyzer that interprets medical results and creates user-friendly medical reports.",
        "data": sanitized_json_obj,
        "instructions": (
            "Analyze the medical results provided in the data. For each test, compare the results against the normal ranges. "
            "If any result is outside the normal range, explain what that might indicate in simple terms, focusing on potential health implications. "
            "For results within the normal range, provide reassurance and affirm the patient's health. "
            "Craft a clear and concise report that explains the findings in a way that is easy for patients to understand. "
            "Avoid using technical jargon, instead use everyday language that a layperson can grasp. "
            "Summarize whether the patient is generally healthy or if they should seek further consultation with a healthcare professional. "
            "Structure your response as a JSON object with the following fields: "
            "Always advise the patient to must visit health care professional as you are just an Ai model"
            "- 'summary': A brief overview of the patient's health status. "
            "- 'detailed_results': A list of results with explanations, including both normal and abnormal findings. "
            "- 'recommendations': Suggestions for next steps or actions the patient should take, if necessary. "
            "Make sure your report is accurate, consistent, and free of false information. "
        )
    }
    


    prompt_string = json.dumps(prompt_data)


    request_payload = {
        "model": "thewindmom/palmyra-med-70b-32k:q4_k_m",
        "prompt": prompt_string, 
        "format": "json",
        "options": {
            "temperature": 0.3,
        },
        "stream": False,
        "keep_alive": "15m"
    }

    print("Data sent to the model:\n", json.dumps(request_payload, indent=4))

    timeout = httpx.Timeout(1800.0, connect=60.0)
    async with httpx.AsyncClient(follow_redirects=True,timeout=timeout) as client:
        response = await client.post(url, json=request_payload)

        with open('../output_Files/report.json', 'w', encoding='utf-8') as jsonfile:
                json.dump(response.json(), jsonfile, indent=4)
        # Log response status and content for debugging
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")

        if response.status_code != 200:
            return {"error": "Model returned an error", "details": response.text}

       
        return response.json()



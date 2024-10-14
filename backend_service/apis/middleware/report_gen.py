import re,os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()
prompt_instructions = os.getenv('PROMPT_INSTRUCTIONS')
server_ip = os.getenv('SERVER_IP') 



def sanitize_json_data(json_data):
    json_string = json.dumps(json_data, indent=4)
    
    
    json_string = re.sub(r'\r', '', json_string)
    json_string = re.sub(r'\n+', '\n', json_string)  
    json_string = json_string.strip()  
    
    return json_string


# Call the AI model for analysis
async def analyze_with_model(json_data):
    url = f"http://{server_ip}:11434/api/generate/"
    
    
    sanitized_json_data = sanitize_json_data(json_data)

    
    sanitized_json_obj = json.loads(sanitized_json_data)
    
    
    prompt_data = {
        "description": "You are 'InspectReport', an advanced AI model specialized in analyzing medical reports and generating comprehensive, user-friendly assessments based on the provided medical data.",
        "data": sanitized_json_obj,
        "instructions": prompt_instructions
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
                
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")

        if response.status_code != 200:
            return {"error": "Model returned an error", "details": response.text}

       
        return response.json()



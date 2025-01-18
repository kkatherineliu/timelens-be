import os
import json
import random
from flask import Flask, request, jsonify
from openai import OpenAI
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(supabase_url, supabase_key)

# from openai import OpenAI
client = OpenAI(
    api_key = os.getenv("OPENAI_KEY")
)

app = Flask(__name__)

@app.route('/')
def home():
    try:
        event = "World War II"

        prompt = "Give me only the name of one major character from the historical event: " + event
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for giving a name of a character from historical events."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0,
            stream=True,
        )

        name = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                name += chunk.choices[0].delta.content


        prompt2 = "Give me a less than 30 word description of: " + name + " from the historical event: " + event
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for giving a short description from a character from historical events."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0,
            stream=True,
        )

        description = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                description += chunk.choices[0].delta.content


        # Generate a random 10 digit ID
        random_id = random.randint(1000000000, 9999999999)

        # send this to supabase

        return jsonify({"id": random_id, "name": name, "description": description})
    except Exception as e:
        # Print the full error message
        print(f"An error occurred when calling the OpenAI API: {e}")
        return jsonify({"error": "An error occurred when processing your request."}), 500





# @app.route('/test/supabase', methods=['GET'])
# def test_supabase():
#     # add data
#     # response_1 = (
#     #     supabase.table("test_table")
#     #     .insert({"name": "Sample Entry again?"})
#     #     .execute()
#     # )

#     # fetch data
#     response = supabase.table("test_table").select("*").eq("id", 1).execute()

#     return response.data

# @app.route("/api/submit")
# def submit_data():
#     event = request.args.get("event")

#     # using the event, create personas and store into supabase
#     # need to add validation/prompt to avoid duplicating existing characters from the same event

#     # Generate character name and description from OpenAI
#     character_completion = openai.chat.completions.create(
#         model="gpt-4o-mini",
#         character_name=[
#             {"role": "system", "content": "You only return the name of a character given a historical event."},
#             {"role": "user", "content": "Give me the name of one major character from the historical event: " + event}, # for now use major characters
#         ]
#     )

#     name = character_completion['choices'][0]['message']['content']

#     description_completion = openai.chat.completions.create(
#         model="gpt-4o-mini",
#         description=[
#             {"role": "system", "content": "Assistant who gives a non-bias description of a character given their name."},
#             {"role": "user", "content": "Give a short description of the major character: " + name + " from the historical event: " + event}, # for now use major characters
#         ]
#     )

    
#     description = description_completion['choices'][0]['message']['content']
    
#     # return for teting purposes
#     return jsonify({"name": name, "description": description})

#     # store variables in supabase
    
# @app.route("/api/chat", methods=['GET'])
# def submit_data():
#     persona_Id = request.args.get("persona_Id")
    


if __name__ == '__main__':
    app.run(debug=True)
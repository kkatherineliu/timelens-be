import os
from flask import Flask, request, jsonify
import openai
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(supabase_url, supabase_key)

openai.api_key = os.getenv("OPENAI_KEY")

# from openai import OpenAI
client = openai()

app = Flask(__name__)

@app.route('/')
def home():
    # event = "World War II"
    # character_completion = openai.completions.create(
    #     model="gpt-4",
    #     prompt="Give me only the name of one major character from the historical event: " + event,
    #     max_tokens=5
    # )

    # name = character_completion['choices'][0]['text'].strip()

    # description_completion = openai.completions.create(
    #     model="gpt-4",
    #     prompt="In less than 30 words, give a short description of the major character: " + name + " from the historical event: " + event,
    #     max_tokens=50
    # )
    # description = description_completion['choices'][0]['text'].strip()

    return response

    # return "asdasda"
    # return jsonify({"name": name, "description": description})

@app.route('/test/supabase', methods=['GET'])
def test_supabase():
    # add data
    # response_1 = (
    #     supabase.table("test_table")
    #     .insert({"name": "Sample Entry again?"})
    #     .execute()
    # )

    # fetch data
    response = supabase.table("test_table").select("*").eq("id", 1).execute()

    return response.data

@app.route("/api/submit")
def submit_data():
    event = request.args.get("event")

    # using the event, create personas and store into supabase
    # need to add validation/prompt to avoid duplicating existing characters from the same event

    # Generate character name and description from OpenAI
    character_completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        character_name=[
            {"role": "system", "content": "You only return the name of a character given a historical event."},
            {"role": "user", "content": "Give me the name of one major character from the historical event: " + event}, # for now use major characters
        ]
    )

    name = character_completion['choices'][0]['message']['content']

    description_completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        description=[
            {"role": "system", "content": "Assistant who gives a non-bias description of a character given their name."},
            {"role": "user", "content": "Give a short description of the major character: " + name + " from the historical event: " + event}, # for now use major characters
        ]
    )

    
    description = description_completion['choices'][0]['message']['content']
    
    # return for teting purposes
    return jsonify({"name": name, "description": description})

#     # store variables in supabase
    
# @app.route("/api/chat", methods=['GET'])
# def submit_data():
#     persona_Id = request.args.get("persona_Id")
    


if __name__ == '__main__':
    app.run(debug=True)
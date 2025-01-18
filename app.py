import os
import json
from flask import Flask, request, jsonify
from openai import OpenAI
from supabase import create_client
from dotenv import load_dotenv

import random
from datetime import datetime
import pytz

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(supabase_url, supabase_key)

# from openai import OpenAI
client = OpenAI(
    api_key = os.getenv("OPENAI_KEY")
)

app = Flask(__name__)


@app.route('/api/submit')
def home():
    return "Starting flask backend"

@app.route('/api/generate')
def generate():
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
            temperature=0.9,
            stream=True,
        )

        name = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                name += chunk.choices[0].delta.content


        prompt2 = "Describe the personality of: " + name + " from the historical event: " + event + " in 30 words or less in a first person perspective"
        stream2 = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for giving a short description of a character's personality from historical events."},
                {"role": "user", "content": prompt2}
            ],
            max_tokens=50,
            temperature=0.9,
            stream=True,
        )

        personality = ""
        for chunk in stream2:
            if chunk.choices[0].delta.content is not None:
                personality += chunk.choices[0].delta.content


        # Generate a random 6 digit ID
        random_id = random.randint(100000, 999999)


        # send this to supabase
        response = (
            supabase.table("personas")
            .insert({"id": random_id, "name": name, "personality": personality, "event": event})
            .execute()
        )

        return jsonify({"id": random_id, "name": name, "personality": personality, "event": event})
    except Exception as e:
        # Print the full error message
        print(f"An error occurred when calling the OpenAI API: {e}")
        return jsonify({"error": "An error occurred when processing your request."}), 500



@app.route("/api/chat", methods=['GET', 'POST'])
def chat():
    # persona_Id = request.args.get("persona_id") # persona id
    # chat_history_Id = request.args.get("chat_history_Id")

    persona_Id = "800142"
    chat_history_Id = 338594
    chat_history = None

    chat_history_text = "the beginning" # basic text
    # fetch a chat history if provided a story_Id
    if chat_history_Id:
        response = supabase.table("chat_history").select("*").eq("id", chat_history_Id).single().execute()
        if(response):
            chat_history = response.data
            chat_history_text = chat_history.get("message")

    # fetch persona based on id
    response = supabase.table("personas").select("*").eq("id", persona_Id).single().execute()

    # if we have an existing persona, add to story
    if response:
        persona = response.data

        prompt = "Starting from " + chat_history_text + ", Tell us the story of " + persona.get("event") + " in the perspective of " + persona.get("name") + " who has a personality: " + persona.get("personality") + " Within 150 words."
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who retells a historical event in the perspective of a given character with a given personality."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.9,
            stream=True,
        )

        story = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                story += chunk.choices[0].delta.content
    
    if chat_history:
        # update the data in supabase if chat_history_id exists (if gpt gets confused, add in the prompt to chat history)
        supabaseResponse = (
            supabase.table("chat_history")
            .update({"message": chat_history_text + " " + story})
            .eq("id", chat_history_Id)
            .execute()
        )
    else:

        # Generate a random 6 digit ID
        random_id = random.randint(100000, 999999)

        # if no chat_history_id, then create new row in supabase
        supabaseResponse = (
            supabase.table("chat_history")
            .insert({"id": random_id, "persona_id": persona_Id, "message": chat_history_text + " " + story, "is_user_input": False})
            .execute()
        )
        

    return story


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

    
    


if __name__ == '__main__':
    app.run(debug=True)
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

#generates a persona with name, personality, event
@app.route('/api/generate')
def generate():
    try:
        event = "World War II"
        # event = request.args.get("event")

        prompt = "Give me only the name of one major character from the historical event: " + event
        stream = client.chat.completions.create(
            model="gpt-4o",
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
            model="gpt-4o",
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

        # send this to supabase
        response = (
            supabase.table("personas")
            .insert({"name": name, "personality": personality, "event": event})
            .execute()
        )

        return jsonify({"name": name, "personality": personality, "event": event})
    except Exception as e:
        # Print the full error message
        print(f"An error occurred when calling the OpenAI API: {e}")
        return jsonify({"error": "An error occurred when processing your request."}), 500



@app.route("/api/chat", methods=['GET', 'POST'])
def chat(): 
    # persona_Id = request.args.get("persona_id") # persona id

    major_points = ["beginning", "climbing action", "falling action", "conclusion"]
    persona_Id = "800142"

    chat_history_text = "" # basic text
    chat_history_start = "You are going continue telling story of "

    # find all instances of chat history related to a persona_id
    response = supabase.table("chat_history").select("*").eq("persona_id", persona_Id).execute()
    
    subevent_number = len(response.data) + 1 # Label as 1,2,3,4 depending on how many chats were previously generated

    # fetch a chat history if provided a story_Id
    if subevent_number > 0:
        chat_history_start = "You already told the story of "
        # get the chat history
        for chat in response.data:
            chat_history_text += chat.get("message")
    else:
        chat_history_text = ""

    # fetch persona based on id
    response = supabase.table("personas").select("*").eq("id", persona_Id).execute()

    if response:
        persona = response.data[0] # return first of the list

        prompt = f"""
        You are a storyteller with a {persona.get("personality")} personality, narrating the events of {persona.get("event")}.
        The story begins as follows:

        "{chat_history_start}"

        Continue the narrative from this point, focusing on the perspective of {persona.get("name")}, and ensure the continuation is unique and at different a point further in time in the event of {persona.get("event")} without repeating any previous content or phrases. Try a different introduction besides "You already told the story of..." Limit your response to 150 words.
        """
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

        # Generate a Title for the subevent:
        prompt3 = "Based on this story: " + story + ", which is related to the historical event: " + persona.get("event") + ", give it a short title."
        stream3 = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who gives a story a title."},
                {"role": "user", "content": prompt3}
            ],
            max_tokens=20,
            temperature=0.9,
            stream=True,
        )

        subevent_title = ""
        for chunk in stream3:
            if chunk.choices[0].delta.content is not None:
                subevent_title += chunk.choices[0].delta.content


        # Add or update data depending on if chat history
        # if chat_history_text != "the beginning":
        #     # update the data in supabase if chat_history_id exists (if gpt gets confused, add in the prompt to chat history)
        #     supabaseResponse = (
        #         supabase.table("chat_history")
        #         .update({"message": chat_history_text + " " + story})
        #         .eq("id", chat_history_Id)
        #         .execute()
        #     )
        # else:
            # if no chat_history_id, then create new row in supabase
        supabaseResponse = (
            supabase.table("chat_history")
            .insert({"persona_id": persona_Id, "message": story, "is_user_input": False, "subevent_number": subevent_number, "subevent_title": subevent_title})
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
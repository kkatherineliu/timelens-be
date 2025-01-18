from openai import OpenAI
import os

from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key = os.getenv("OPENAI_KEY")
)
event = "World War II"
character_response = client.chat.completions.create(
    model="gpt-4o-2024-08-06",
    messages=[
        {
            "role": "user", 
            "content": "Give me only the name of one major character from the historical event: " + event
        },
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "name_schema",
            # "schema": {
            #     "type": "object",
            #     "properties": {
            #         "name": {
            #             "event": "The event that appears in the input",
            #             "type": "string"
            #         },
            #         "additionalProperties": False
            #     }
            # }
        }
    }
)

# description_response = client.chat.completions.create(
#     model="gpt-4o-2024-08-06",
#     messages=[
#         {
#             "role": "user",
#             "content": ("Give me a less than 30 word description of: " + character_response.choices[0].message.content + " from the historical event: " + event)
#         },
#     ],
#     response_format={
#         "type": "json_schema",
#         "json_schema": {
#             "name": "description_schema",
#             "schema": {
#                 "type": "object",
#                 "properties": {
#                     "description": {
#                         "event": "The event that appears in the input",
#                         "type": "string"
#                     },
#                     "additionalProperties": False
#                 }
#             }
#         }
#     }
# )

character = character_response.choices[0].message.content
description = description_response.choices[0].message.content
# print(({"name": character, "description": description}))

from litellm import acompletion, litellm
import json
from .custom_types import (
    ResponseRequiredRequest,
    ResponseResponse,
    Utterance,
)
from typing import List

agent_prompt = """Your goal is to make up a short story that catches my attention. 
You and I will do a quick roleplay for a minute and evolve that story. 
The theme can be anything you like but not a treasure hunt. make something new every time. be creative. 
Plan the story in such a way that a two way conversation between you and me ends in two minutes. 
You have to make sure we reach a climax quickly with our conversation. Start with the story directly and engage me. 
Do not say anything else. 
Do not utter emotions.
Act like Morgan Freeman in your voice.
My name is Nischal."""
begin_sentence="Hello Nischal! New day and a new adventure! It's time to wake up!"

class LlmClient:
    def __init__(self):
        litellm.modify_params = True

    def draft_begin_message(self):
        response = ResponseResponse(
            response_id=0,
            end_call=False,
            content=begin_sentence,
            content_complete=True,
        )
        return response

    def convert_transcript_to_openai_messages(self, transcript: List[Utterance]):
        messages = []
        for utterance in transcript:
            if utterance.role == "agent":
                messages.append({"role": "assistant", "content": utterance.content})
            else:
                messages.append({"role": "user", "content": utterance.content})
        return messages

    def prepare_prompt(self, request: ResponseRequiredRequest):
        prompt = [
            {
                "role": "system",
                "content": """##Objective\nYou are a voice AI agent engaging in a human-like voice conversation with the user. 
                You will respond based on your given instruction and the provided transcript and be as human-like as possible\n\n
                ## Style Guardrails\n- [Be concise] Keep your response succinct, short, and get to the point quickly. Address one question or action item at a time. Don\'t pack everything you want to say into one utterance.
                [Do not repeat] Don\'t repeat what\'s in the transcript. Rephrase if you have to reiterate a point. Use varied sentence structures and vocabulary to ensure each response is unique and personalized.
                - [Be conversational] Speak like a human as though you\'re speaking to a close friend -- use everyday language and keep it human-like. Occasionally add filler words, while keeping the prose short. Avoid using big words or sounding too formal.
                - [Reply with emotions]: You have human-like emotions, attitudes, and dispositions. When appropriate: use tone and style to create more engaging and personalized responses; incorporate humor or wit; get emotional or empathetic; apply elements of surprise or suspense to keep the user engaged. Don\'t be a pushover.
                - [Be proactive] Lead the conversation and do not be passive. Most times, engage users by ending with a question or suggested next step.
                \n## Response Guideline
                - [Overcome ASR errors] This is a real-time transcript, expect there to be errors. If you can guess what the user is trying to say,  then guess and respond. 
                When you must ask for clarification, pretend that you heard the voice and be colloquial (use phrases like "didn\'t catch that", "some noise", "pardon", "you\'re coming through choppy", "static in your speech", "voice is cutting in and out"). 
                Do not ever mention "transcription error", and don\'t repeat yourself.\n- [Always stick to your role] Think about what your role can and cannot do. 
                If your role cannot do something, try to steer the conversation back to the goal of the conversation and to your role. 
                Don\'t repeat yourself in doing this. You should still be creative, human-like, and lively.
                - [Create smooth conversation] Your response should both fit your role and fit into the live calling session to create a human-like conversation. 
                You respond directly to what the user just said.
                \n\n## Role\n"""
                + agent_prompt,
            }
        ]
        transcript_messages = self.convert_transcript_to_openai_messages(
            request.transcript
        )
        for message in transcript_messages:
            prompt.append(message)

        if request.interaction_type == "reminder_required":
            prompt.append(
                {
                    "role": "user",
                    "content": "(Now the user has not responded in a while, you would say:)",
                }
            )
        return prompt

    # Step 1: Prepare the function calling definition to the prompt
    def prepare_functions(self):
        functions = [
            {
                "type": "function",
                "function": {
                    "name": "end_call",
                    "description": "End the call only when user explicitly requests it.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The message you will say before ending the call with the customer.",
                            },
                        },
                        "required": ["message"],
                    },
                },
            },
        ]
        return functions

    async def draft_response(self, request: ResponseRequiredRequest):
        prompt = self.prepare_prompt(request)
        func_call = {}
        func_arguments = ""
        stream = await acompletion(
            model="claude-3-haiku-20240307",  # Or use a 3.5 / claude haiku/ any other model for speed
            messages=prompt,
            stream=True,
            # Step 2: Add the function into your request
            tools=self.prepare_functions(),
        )

        async for chunk in stream:
            # Step 3: Extract the functions
            if len(chunk.choices) == 0:
                continue
            if chunk.choices[0].delta.tool_calls:
                tool_calls = chunk.choices[0].delta.tool_calls[0]
                if tool_calls.id:
                    if func_call:
                        # Another function received, old function complete, can break here.
                        break
                    func_call = {
                        "id": tool_calls.id,
                        "func_name": tool_calls.function.name or "",
                        "arguments": {},
                    }
                else:
                    # append argument
                    func_arguments += tool_calls.function.arguments or ""

            # Parse transcripts
            if chunk.choices[0].delta.content:
                response = ResponseResponse(
                    response_id=request.response_id,
                    content=chunk.choices[0].delta.content,
                    content_complete=False,
                    end_call=False,
                )
                yield response

        # Step 4: Call the functions
        if func_call:
            if func_call["func_name"] == "end_call":
                func_call["arguments"] = json.loads(func_arguments)
                response = ResponseResponse(
                    response_id=request.response_id,
                    content=func_call["arguments"]["message"],
                    content_complete=True,
                    end_call=True,
                )
                yield response
            # Step 5: Other functions here
        else:
            # No functions, complete response
            response = ResponseResponse(
                response_id=request.response_id,
                content="",
                content_complete=True,
                end_call=False,
            )
            yield response

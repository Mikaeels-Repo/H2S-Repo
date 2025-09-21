import google.generativeai as genai
import os
import ast

# Configure the Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def list_available_models():
    """Lists the available Gemini models."""
    print("--- Available Gemini Models ---")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
    print("-----------------------------")

def analyze_document(text):
    """
    Analyzes the document using the Gemini API to identify complex legal phrases
    and generate a summary.
    """
    list_available_models()
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

    # Prompt for identifying and simplifying legal phrases
    phrase_prompt = f"""Given the following legal text, identify up to 10 complex legal phrases and provide a simple, easy-to-understand explanation for each. Return ONLY a valid Python dictionary where the keys are the complex phrases and the values are their simplified explanations. Example: {{'complex phrase': 'simple explanation'}}

    Legal Text:
    {text}
    """

    # Prompt for summarizing the document
    summary_prompt = f"""Summarize the following legal document, highlighting the most important points.

    Legal Document:
    {text}
    """

    try:
        # Generate annotations
        phrase_response = model.generate_content(phrase_prompt)
        print("Raw response from the model for phrases:", phrase_response.text)
        try:
            start = phrase_response.text.find('{')
            end = phrase_response.text.rfind('}')
            if start != -1 and end != -1:
                dict_string = phrase_response.text[start:end+1]
                annotations = ast.literal_eval(dict_string)
            else:
                annotations = {}
        except:
            annotations = {}

        # Generate summary
        summary_response = model.generate_content(summary_prompt)
        summary = summary_response.text

    except Exception as e:
        print(f"An error occurred with the Gemini API: {e}")
        annotations = {}
        summary = "Could not generate a summary at this time."

    return annotations, summary

def analyze_document_iteratively(text):
    """
    Analyzes the document using iterative summarization.
    """
    list_available_models()
    print("--- Starting iterative summarization ---")
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

    # 1. Analyze complex phrases (on the full text)
    print("Analyzing complex phrases...")
    phrase_prompt = f"""Given the following legal text, identify up to 10 complex legal phrases and provide a simple, easy-to-understand explanation for each. Return ONLY a valid Python dictionary where the keys are the complex phrases and the values are their simplified explanations. Example: {{'complex phrase': 'simple explanation'}}

    Legal Text:
    {text}
    """
    try:
        phrase_response = model.generate_content(phrase_prompt)
        print("Raw response from the model for phrases:", phrase_response.text)
        try:
            start = phrase_response.text.find('{')
            end = phrase_response.text.rfind('}')
            if start != -1 and end != -1:
                dict_string = phrase_response.text[start:end+1]
                annotations = ast.literal_eval(dict_string)
                print("Successfully parsed the phrase analysis response.")
            else:
                print("Could not find a dictionary in the phrase analysis response.")
                annotations = {}
        except:
            print("Could not parse the phrase analysis response. Continuing with summarization only.")
            annotations = {}
        print("Successfully analyzed complex phrases.")
    except Exception as e:
        print(f"An error occurred with the Gemini API while analyzing phrases: {e}")
        annotations = {}

    # 2. Iterative summarization
    print("Starting iterative summarization of chunks...")
    try:
        text_chunks = [text[i:i + 8000] for i in range(0, len(text), 8000)] # Reduced chunk size
        print(f"Split document into {len(text_chunks)} chunks.")
        chunk_summaries = []
        for i, chunk in enumerate(text_chunks):
            print(f"Summarizing chunk {i+1}/{len(text_chunks)}...")
            summary_prompt = f"""Summarize the following text from a legal document:

            {chunk}
            """
            summary_response = model.generate_content(summary_prompt)
            chunk_summaries.append(summary_response.text)
            print(f"Successfully summarized chunk {i+1}.")

        combined_summaries = "\n".join(chunk_summaries)
        print("Successfully combined chunk summaries.")

        print("Generating final summary...")
        final_summary_prompt = f"""Combine the following summaries into a single, coherent summary of the entire legal document:

        {combined_summaries}
        """
        final_summary_response = model.generate_content(final_summary_prompt)
        summary = final_summary_response.text
        print("Successfully generated final summary.")
    except Exception as e:
        print(f"An error occurred with the Gemini API during summarization: {e}")
        summary = "Could not generate a summary at this time."

    print("--- Iterative summarization finished ---")
    return annotations, summary

def get_chat_response(user_message):
    """
    Generates a response to a user's message using the Gemini API.
    """
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
    try:
        response = model.generate_content(user_message)
        return response.text
    except Exception as e:
        print(f"An error occurred with the Gemini API: {e}")
        return "I am sorry, but I am unable to process your request at the moment."


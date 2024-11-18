import torch
import pyttsx3
import speech_recognition as sr
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from textblob import TextBlob
import os
import nltk
import random
import requests


# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function for speech recognition (using Wav2Vec 2.0 for speech-to-text)
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak into the microphone (Press Ctrl+C to exit)...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        print("Processing your speech...")
        # Using Google Web Speech API as a fallback
        speech = recognizer.recognize_google(audio)
        print(f"You said: {speech}")
        return speech
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError:
        print("Error with the speech recognition service.")
        return None

# Function for AI Feedback Generation (basic feedback based on sentence quality)
def generate_feedback(text):
    # Using TextBlob to check grammar and fluency
    blob = TextBlob(text)
    correction = blob.correct()

    # Simple feedback based on grammar correction
    if text == str(correction):
        feedback = "Your sentence is clear and grammatically correct."
    else:
        feedback = f"Your sentence had some errors. Here's a corrected version: {correction}"

    return feedback

# Function for speech-to-text using Wav2Vec2 model (advanced speech-to-text)
def advanced_speech_to_text(file_path):
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-xlsr-53")
    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-xlsr-53")

    # Load and process audio
    waveform, sample_rate = torch.load(file_path)  # Load your WAV file
    input_values = processor(waveform, return_tensors="pt").input_values

    # Perform speech-to-text inference
    with torch.no_grad():
        logits = model(input_values).logits

    # Get predicted tokens
    predicted_ids = torch.argmax(logits, dim=-1)

    # Convert token IDs back to text
    transcription = processor.batch_decode(predicted_ids)
    return transcription[0]

# Function to fetch random words from a website
def get_random_word():
    url = "https://random-word-api.herokuapp.com/word?number=1"  # API to get a random word
    try:
        response = requests.get(url)
        response.raise_for_status()
        word = response.json()[0]
        return word
    except requests.exceptions.RequestException as e:
        print(f"Error fetching random word: {e}")
        return None

# Function to fetch word definition from an online API (DictionaryAPI)
def get_word_definition(word):
    url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        definition = data[0]['meanings'][0]['definitions'][0]['definition']
        return definition
    except requests.exceptions.RequestException as e:
        print(f"Error fetching word definition: {e}")
        return "Definition not found."

# Function for the vocabulary quiz
def vocabulary_quiz():
    score = 0
    total_questions = 5  # Number of questions for the quiz
    for i in range(total_questions):
        # Get a random word from the API
        word = get_random_word()
        if word is None:
            print("Unable to fetch a word. Exiting quiz.")
            break
        
        # Get the definition of the current word
        correct_definition = get_word_definition(word)

        # Fetch a few other random words and their definitions for the incorrect options
        incorrect_options = []
        while len(incorrect_options) < 3:
            random_word = get_random_word()
            if random_word and random_word != word:  # Ensure we don't repeat the correct word
                definition = get_word_definition(random_word)
                if definition and definition != correct_definition:
                    incorrect_options.append(definition)

        # All options (one correct and three incorrect)
        options = [correct_definition] + incorrect_options
        random.shuffle(options)

        # Present the question to the user
        print(f"\nQuestion {i + 1}:")
        print(f"Word: {word}")
        print("Choose the correct meaning:")

        # Display options
        for idx, option in enumerate(options, 1):
            print(f"{idx}. {option}")

        # Get the user's answer
        try:
            answer = int(input("\nYour answer (1-4): "))
            if answer < 1 or answer > 4:
                raise ValueError
        except ValueError:
            print("Invalid input. Please choose a number between 1 and 4.")
            continue

        # Check if the answer is correct
        if options[answer - 1] == correct_definition:
            print("Correct!")
            score += 1
        else:
            print(f"Incorrect. The correct definition is: {correct_definition}")
    
    # Provide the final score
    print(f"\nQuiz completed. Your score: {score}/{total_questions}")
    if score == total_questions:
        engine.say("Great job! You aced the quiz.")
    else:
        engine.say(f"Good effort! Your score is {score} out of {total_questions}. Keep learning!")
        


# Main CLI Function for Soft Skill Enhancement
def main():
    while True:
        print("\n=== Soft Skill Enhancer CLI ===")
        print("1. Speech-to-Text Practice")
        print("2. Vocabulary Quiz")
        print("3. View Progress")
        print("4. Exit")

        choice = input("Select an option: ")

        if choice == '1':
            # Speech-to-Text Practice
            text = speech_to_text()
            if text:
                feedback = generate_feedback(text)
                print(f"AI Feedback: {feedback}")
                engine.say(feedback)  # Speak the feedback
                engine.runAndWait()
        elif choice == '2':
            # Vocabulary Quiz (add your quiz logic here)
            print("\n--- Vocabulary Quiz ---")
            vocabulary_quiz()
        elif choice == '3':
            # View Progress (This is a placeholder, you can expand with progress tracking logic)
            print("Your progress: 75%")
        elif choice == '4':
            print("Exiting Soft Skill Enhancer...")
            break
        else:
            print("Invalid option. Please try again.")

# Run the main program
if __name__ == "__main__":
    main()

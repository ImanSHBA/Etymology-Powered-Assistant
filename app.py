import streamlit as st
import cohere
import pandas as pd
import json

# Read your Cohere API key from a file
with open("key.key") as f:
    COHERE_API_KEY = f.read().strip()

# Initialize the Cohere client (using ClientV2 for chat-like interactions)
cohere_client = cohere.ClientV2(COHERE_API_KEY)

# ---------------- Sidebar ---------------- #
def language_preferences_sidebar():
    st.sidebar.header("Language Preferences")
    known_languages = st.sidebar.multiselect(
        "Select the languages you already know:",
        ["English", "Persian", "Spanish", "French", "German", "Italian", "Portuguese", "Mandarin", "Japanese", "Korean", "Russian"],
        default=["English"]
    )
    target_language = st.sidebar.selectbox(
        "Which language do you want to learn?",
        ["Spanish", "Persian", "French", "German", "Italian", "Portuguese", "Mandarin", "Japanese", "Korean", "Russian"]
    )
    teach_level = st.sidebar.selectbox(
        "Select your teaching level:",
        ["A1", "A2", "B1", "B2", "C1", "C2"],
        index=0
    )
    st.session_state.known_languages = known_languages
    st.session_state.target_language = target_language
    st.session_state.teach_level = teach_level
    if st.sidebar.button("Reload"):
        st.rerun()

# ---------------- Helper Functions ---------------- #

def get_etymology(word, context_data=""):
    target_language = st.session_state.get("target_language", "the target language")
    known_languages = st.session_state.get("known_languages", [])
    known_str = ", ".join(known_languages) if known_languages else "commonly known languages like English"
    system_prompt = {
        "role": "system",
        "content": f"""
        You are a knowledgeable language teacher focused on teaching {target_language}.
        Your purpose is to help the user understand words in {target_language} by breaking them down into their morphological components.
        Use the student's known languages ({known_str}) as reference points.
        Provide a detailed breakdown and include at least three clear examples.
        For example, if teaching Spanish and the word is "importamente", break it into "import" (similar to "important" in English) and "amente" (functioning like "-ly" in English).
        """
    }
    user_prompt = {
        "role": "user",
        "content": f"Break down the word '{word}' with historical roots and translations in {target_language}. {context_data}"
    }
    response = cohere_client.chat(
        messages=[system_prompt, user_prompt],
        model="command-r-plus",
        max_tokens=1000,
        temperature=0.7
    )
    return response.message.content[0].text

def generate_family_tree(word, context_data=""):
    target_language = st.session_state.get("target_language", "the target language")
    known_languages = st.session_state.get("known_languages", [])
    known_str = ", ".join(known_languages) if known_languages else "commonly known languages like English"
    system_prompt = {
        "role": "system",
        "content": f"""
        You are a knowledgeable language teacher focused on teaching {target_language}.
        Your task is to create a semantic family tree showing how words in {target_language} are related.
        Use the student's known languages ({known_str}) as references.
        Provide a detailed breakdown with at least three clear examples.
        For instance, if given "el libro de john", compare its structure to similar constructions in the known languages.
        """
    }
    user_prompt = {
        "role": "user",
        "content": f"Create a semantic family tree for '{word}' in {target_language}. {context_data}"
    }
    response = cohere_client.chat(
        messages=[system_prompt, user_prompt],
        model="command-r-plus",
        max_tokens=1000,
        temperature=0.7
    )
    return response.message.content[0].text

def fill_vocab_info(word, etymology_info):
    # Returns a JSON object with keys: word, root, prefix, suffix, translations.
    known_languages = st.session_state.get("known_languages", [])
    target_language = st.session_state.get("target_language", "the target language")
    known_str = ", ".join(known_languages) if known_languages else "English"
    system_prompt = {
        "role": "system",
        "content": f"""
        You are a knowledgeable language teacher specialized in teaching {target_language}.
        Given the word and its root explanation, produce a concise JSON object with exactly these keys:
        "word", "root", "prefix", "suffix", "translations".
        For any key without an answer, use a single dash ("-").
        The "translations" must be an object with each of the student's known languages ({known_str}) as keys and the word's translation as values.
        For example, if the word is "importamente", the correct output should be:
        {{"word": "importamente", "root": "import", "prefix": "-", "suffix": "amente", "translations": {{"English": "importantly"}}}}.
        Return only the JSON object with no additional text.
        """
    }
    user_prompt = {
        "role": "user",
        "content": f"Word: {word}\nRoot explanation: {etymology_info}\nProduce the JSON object as described."
    }
    response = cohere_client.chat(
        messages=[system_prompt, user_prompt],
        model="command-r-plus",
        max_tokens=1000,
        temperature=0.7
    )
    vocab_info = json.loads(response.message.content[0].text)

    return vocab_info

def add_to_vocab(word, etymology_info):
    vocab_info = fill_vocab_info(word, etymology_info)
    new_row = pd.DataFrame([vocab_info])
    st.session_state.vocab_bank = pd.concat([st.session_state.vocab_bank, new_row], ignore_index=True)

def display_vocab_bank():
    st.subheader("Your Vocabulary Bank")
    st.dataframe(st.session_state.vocab_bank)

# ---------------- Chatbot Helper Functions ---------------- #

def initial_lesson():
    # Two separate API calls: one for vocabulary object (for df_memory) and one for greeting message.
    target_language = st.session_state.get("target_language", "the target language")
    known_languages = st.session_state.get("known_languages", [])
    teach_level = st.session_state.get("teach_level", "A1")
    known_str = ", ".join(known_languages) if known_languages else "English"
    # First API call for vocabulary object:
    system_prompt_vocab = {
        "role": "system",
        "content": f"""
        You are a knowledgeable language teacher specialized in teaching {target_language} at the {teach_level} level.
        Provide a basic greeting vocabulary word in {target_language} in a valid JSON object with these keys: "word", "root", "prefix", "suffix", "translations".
        For any missing information, use "-". Include at least three examples if applicable.
        For example, if the target language is Spanish, the output should be:
        {{"word": "hola", "root": "hola", "prefix": "-", "suffix": "-", "translations": {{"English": "hello"}}}}.
        Return only the JSON object.
        """
    }
    user_prompt_vocab = {
        "role": "user",
        "content": "Generate a vocabulary object for a basic greeting."
    }
    response_vocab = cohere_client.chat(
        messages=[system_prompt_vocab, user_prompt_vocab],
        model="command-r-plus",
        max_tokens=1000,
        temperature=0.7
    )
    
    lesson_vocab = json.loads(response_vocab.message.content[0].text)

    
    # Second API call for greeting explanation message:
    system_prompt_greeting = {
        "role": "system",
        "content": f"""
        You are a welcoming language teacher chatbot.
        Greet the user with a friendly message, explain that our product uses advanced AI to provide personalized lessons by leveraging their known languages and the {teach_level} level., 
        and then introduce a lesson on greetings, for example for teaching level A1 you should including how "hi" and the forms of "am", "is", "are" work in {target_language}.
        for A1 level just teach hello"
        you should end with an explanation to user about:
        1. he/she can go to the new lesson
        2. add the word he /she jest learnt to his vocab bank
        3. ask for more examples
        4. and talk to you about multiple subjects
        Answer in plain text.
        """
    }
    user_prompt_greeting = {
        "role": "user",
        "content": "Provide a greeting message for starting the lesson."
    }
    response_greeting = cohere_client.chat(
        messages=[system_prompt_greeting, user_prompt_greeting],
        model="command-r-plus",
        max_tokens=500,
        temperature=0.7
    )
    lesson_greeting = response_greeting.message.content[0].text.strip()
    return lesson_vocab, lesson_greeting

def generate_new_vocab():
    target_language = st.session_state.get("target_language", "the target language")
    known_languages = st.session_state.get("known_languages", [])
    teach_level = st.session_state.get("teach_level", "A1")
    system_prompt = {
        "role": "system",
        "content": f"""
        You are a helpful language teacher chatbot. Based on the vocabulary already taught in this conversation, 
        select a new vocabulary word in {target_language} at the {teach_level} level. that would be beneficial for the student.
        Provide the word with a detailed explanation in valid JSON format with the keys: "word", "root", "prefix", "suffix", "translations".
        For any missing information, use "-".
        Return only the JSON object in mentioned structure and nothing else.
        For example, if the target language is Spanish, the output should be:
        {{"word": "hola", "root": "hola", "prefix": "-", "suffix": "-", "translations": {{"English": "hello"}}}}.
        """
    }
    user_prompt = {
        "role": "user",
        "content": f"Based on the {st.session_state.df_memory} which is the list of the words that I know, select a new vocabulary word to teach."
    }
    response = cohere_client.chat(
        messages=[system_prompt, user_prompt],
        model="command-r-plus",
        max_tokens=1000,
        temperature=0.7
    )
    
    new_vocab = json.loads(response.message.content[0].text)

    return new_vocab

def generate_similar(last_word):
    target_language = st.session_state.get("target_language", "the target language")
    known_languages = st.session_state.get("known_languages", [])
    known_str = ", ".join(known_languages) if known_languages else "English"
    teach_level = st.session_state.get("teach_level", "A1")
    system_prompt = {
        "role": "system",
        "content": f"""
        You are a knowledgeable language teacher chatbot. Provide one vocabulary word similar to given word in {target_language} at the {teach_level} level.
        For this similar word, provide a detailed explanation in valid JSON format with the keys: "word", "root", "prefix", "suffix", "translations".
        For any missing information, use "-".
        do not use this vocabs {st.session_state.df_memory}
        Return only the JSON object with no additional text.
        For example, if the target language is Spanish, the output should be:
        {{"word": "hola", "root": "hola", "prefix": "-", "suffix": "-", "translations": {{"English": "hello"}}}}.
        """
    }
    user_prompt = {
        "role": "user",
        "content": f"{last_word}"
    }
    response = cohere_client.chat(
        messages=[system_prompt, user_prompt],
        model="command-r-plus",
        max_tokens=1000,
        temperature=0.7
    )
    
    similar = json.loads(response.message.content[0].text)

    return similar

# ---------------- Page Functions ---------------- #

def word_etymology_breakdown_page():
    st.header("Word Etymology Breakdown")
    word = st.text_input("Enter a word for etymology breakdown:", key="etymology_word")
    explanation = ""
    if st.button("Get Etymology Breakdown", key="etymology_button"):
        if word:
            explanation = get_etymology(word)
            st.write(explanation)
    if  st.button("Add to Vocabulary Bank", key="add_vocab_button"):
        add_to_vocab(word, explanation)
        st.success(f"Word '{word}' added to Vocabulary Bank!")

def semantic_family_tree_page():
    st.header("Semantic Family Tree")
    word = st.text_input("Enter a word for its semantic family tree:", key="tree_word")
    if st.button("Generate Family Tree", key="tree_button"):
        if word:
            tree = generate_family_tree(word)
            st.write(tree)
    if  st.button("Add to Vocabulary Bank", key="add_vocab_button2"):
        explanation = get_etymology(word)
        add_to_vocab(word, explanation)
        st.success(f"Word '{word}' added to Vocabulary Bank!")

def vocabulary_bank_page():
    st.header("Vocabulary Bank")
    st.write("Review the words you have added along with their detailed explanations:")
    display_vocab_bank()
    st.subheader("Add a New Vocabulary Word Manually")
    new_vocab = st.text_input("Enter a new vocabulary word:", key="new_vocab")
    if st.button("Add New Vocabulary", key="add_new_vocab_button"):
        if new_vocab:
            explanation = get_etymology(new_vocab)
            add_to_vocab(new_vocab, explanation)
            st.success(f"Word '{new_vocab}' added to Vocabulary Bank!")

# Separate functions for each special command in chat

def handle_new_lesson():
    new_vocab = generate_new_vocab()
    st.session_state.df_memory = pd.concat([st.session_state.df_memory, pd.DataFrame([new_vocab])], ignore_index=True)
    st.session_state.last_vocab = new_vocab["word"]
    return f"New lesson: {json.dumps(new_vocab)}"

def handle_similar_word():
    similar = generate_similar(st.session_state.last_vocab)
    st.session_state.df_memory = pd.concat([st.session_state.df_memory, pd.DataFrame([similar])], ignore_index=True)
    return f"Similar word: {json.dumps(similar)}"

def handle_add_to_vocab():
    # Adds the last taught word to the vocabulary bank
    last_word = st.session_state.last_vocab
    # Retrieve explanation for last word using get_etymology (or use df_memory if exists)
    explanation = get_etymology(last_word)
    add_to_vocab(last_word, explanation)
    return f"Word '{last_word}' added to Vocabulary Bank."

def handle_general_chat():
    response = cohere_client.chat(
        messages=st.session_state.history_chat,
        model="command-r-plus",
        max_tokens=1000,
        temperature=0.7
    )
    return response.message.content[0].text
def json_to_explanation(assistant_response):
    known_languages = st.session_state.get("known_languages", [])
    target_language = st.session_state.get("target_language", "the target language")
    known_str = ", ".join(known_languages) if known_languages else "English"
    teach_level = st.session_state.get("teach_level", "A1")
    if "New lesson:" in assistant_response or "Similar word:" in assistant_response:
        system_prompt = {
        "role": "system",
        "content": f"""
        You are a knowledgeable language teacher specialized in teaching {target_language}.
        try to use this vocabs {st.session_state.df_memory} to explain it to knowing the fact that my level is{teach_level}
        You get only two types of inputs:
        1. starts with New lesson: you should teach this word for the first time. its good to have examples from. start your answer with exact "New lesson:"
        2. Starts with Similar word: you should talk about similar word to it. start your answer with exact Similar word:
        3. execpt 1 and 2 you should say "wrong answer" and nothing else
        """
        }
        user_prompt = {
        "role": "user",
        "content": assistant_response
        }
        response = cohere_client.chat(
        messages=[system_prompt, user_prompt],
        model="command-r-plus",
        max_tokens=1000,
        temperature=0.7
        )
        answer = response.message.content[0].text
    return answer

def personalized_learning_chatbot_page():
    st.header("Personalized Learning Chatbot")
    st.write("You can start the lesson here.")
    
    # Use cache for df_memory, history_chat, and vocab_bank
    if "history_chat" not in st.session_state:
        st.session_state.history_chat = []
    if "df_memory" not in st.session_state:
        st.session_state.df_memory = pd.DataFrame(columns=["word", "root", "prefix", "suffix", "translations"])
    
    # Automatically start lesson if history_chat is empty
    if not st.session_state.history_chat:
        lesson_vocab, lesson_greeting = initial_lesson()
        st.session_state.df_memory = pd.concat([st.session_state.df_memory, pd.DataFrame([lesson_vocab])], ignore_index=True)
        st.session_state.last_vocab = lesson_vocab["word"]
        st.session_state.history_chat.append({
            "role": "system",
            "content": f"{lesson_greeting}"
        })
    
    # Display chat messages
    for message in st.session_state.history_chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Always show the chat input at the bottom
    if prompt := st.chat_input("Your message"):
        st.chat_message("user").markdown(prompt)
        st.session_state.history_chat.append({"role": "user", "content": prompt})
        
        # Use LLM to classify the prompt into one of the four commands.
        command = determine_command(prompt)
        if command == "new lesson":
            assistant_response = handle_new_lesson()
            assistant_response = json_to_explanation(assistant_response)
        elif command == "similar word":
            assistant_response = handle_similar_word()
            assistant_response = json_to_explanation(assistant_response)
        elif command == "add to vocab":
            assistant_response = handle_add_to_vocab()
        else:
            assistant_response = handle_general_chat()
        st.chat_message("assistant").markdown(assistant_response)
        st.session_state.history_chat.append({"role": "assistant", "content": assistant_response})
        st.rerun()

def determine_command(user_input):
    # Classify the user input using LLM into one of: new lesson, more examples, add to vocab, general chat.
    system_prompt = {
        "role": "system",
        "content": """
        You are a helpful assistant. Classify the following user input into one of these commands:
        - "new lesson": if the user wants to start a new lesson (teach one new vocabulary word).
        - "similar word": if the user wants to see a similar word of the last taught word.
        - "add to vocab": if the user wants to add the last taught word to the vocabulary bank or vocab or vocab bank.
        - "general chat": for any other conversation.
        Respond with one of four options and other respons are not acceptable
        Do not include any extra text.
        """
    }
    user_prompt = {
        "role": "user",
        "content": user_input
    }
    response = cohere_client.chat(
        messages=[system_prompt, user_prompt],
        model="command-r-plus",
        max_tokens=100,
        temperature=0.0
    )
    
    result = response.message.content[0].text
    return result



def add_custom_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            background-color: #F2F6FF;
        }

        /* === MAIN CONTAINER === */
        .reportview-container .main .block-container {
            background: linear-gradient(145deg, #FFFFFF, #F0F4FF);
            border-radius: 16px;
            padding: 2.5rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        }

        /* === SIDEBAR === */
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #7FB3D5, #76D7C4);
            border-top-right-radius: 25px;
            border-bottom-right-radius: 25px;
            padding: 1.5rem;
            color: #fff;
        }

        /* === BUTTONS (unchanged) === */
        div.stButton > button {
            background: linear-gradient(135deg, #536976, #292E49);
            color: #FFFFFF;
            border: none;
            border-radius: 12px;
            padding: 12px 26px;
            font-size: 16px;
            font-weight: 600;
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
        }

        div.stButton > button:hover {
            background: linear-gradient(135deg, #292E49, #536976);
            transform: scale(1.04);
        }

        /* === CHAT BUBBLES === */
        div[data-testid="stChatMessage"] {
            max-width: 80%;
            padding: 14px 20px;
            margin: 16px 0;
            border-radius: 18px;
            position: relative;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            font-size: 15px;
            line-height: 1.6;
        }

        /* === Assistant Message (left-aligned cloud) === */
        div[data-testid="stChatMessage"][data-isassistant="true"] {
            background-color: #DCF8C6;
            color: #1B4F3F;
            align-self: flex-start;
            margin-left: 0;
        }

        div[data-testid="stChatMessage"][data-isassistant="true"]::after {
            content: "";
            position: absolute;
            top: 10px;
            left: -10px;
            width: 0;
            height: 0;
            border-top: 10px solid transparent;
            border-bottom: 10px solid transparent;
            border-right: 10px solid #DCF8C6;
        }

        /* === User Message (right-aligned cloud) === */
        div[data-testid="stChatMessage"][data-isassistant="false"] {
            background-color: #FFFFFF;
            color: #333;
            align-self: flex-end;
            margin-right: 0;
            border: 1px solid #DADADA;
        }

        div[data-testid="stChatMessage"][data-isassistant="false"]::after {
            content: "";
            position: absolute;
            top: 10px;
            right: -10px;
            width: 0;
            height: 0;
            border-top: 10px solid transparent;
            border-bottom: 10px solid transparent;
            border-left: 10px solid #FFFFFF;
        }

        /* === Other Elements (inputs, tabs, etc.) — optionally leave as-is for now === */

        </style>
        """,
        unsafe_allow_html=True
    )



# ---------------- Main App ---------------- #
def main():
    st.title("Language Learning Prototype")
    add_custom_css()
    language_preferences_sidebar()
    
    if "vocab_bank" not in st.session_state:
        st.session_state.vocab_bank = pd.DataFrame(columns=["word", "root", "prefix", "suffix", "translations"])
    
    tabs = st.tabs([
        "Personalized Learning Chatbot",
        "Word Etymology Breakdown", 
        "Semantic Family Tree", 
        "Vocabulary Bank"
    ])
    
    with tabs[0]:
        personalized_learning_chatbot_page()
    with tabs[1]:
        word_etymology_breakdown_page()
    with tabs[2]:
        semantic_family_tree_page()
    with tabs[3]:
        vocabulary_bank_page()


if __name__ == "__main__":
    main()

# Language Learning Prototype – Etymology-Powered Assistant

This Streamlit-based prototype helps users learn a new language by leveraging etymology and morphological similarities with languages they already know. It uses a conversational AI (powered by Cohere) to deliver personalized, interactive lessons aligned with the user’s language level and preferences.

## Features

### Personalized Learning Chatbot
An AI-powered chatbot that teaches new words interactively. It uses language model reasoning to detect user intent (e.g., "new lesson", "more examples", "add to vocab") and responds accordingly. Each taught word is saved in memory with a breakdown of its root, prefix, suffix, and translations.

### Word Etymology Breakdown
Users can input any word in the target language and receive a detailed breakdown of its morphological structure, including connections to equivalent terms in known languages.

### Semantic Family Tree
Generates a tree of semantically related words across different languages to help users build conceptual understanding of vocabulary.

### Vocabulary Bank
A personal vocabulary manager where users can save and review learned words with etymological and translation information. Words can be added manually or via the chatbot.

## How It Works

- Select your known languages, target language, and CEFR level (A1–C2) in the sidebar.
- The chatbot begins the conversation with a basic lesson based on your preferences.
- Type naturally or use specific commands:
  - `new lesson` – teaches a new word
  - `similar word` – shows related words
  - `add to vocab` – adds the last word to your vocabulary bank
- Use the additional tabs to explore word structure and grow your vocabulary list.

## Design Decisions

- **Etymology-Based Learning**: Words are taught by breaking down their roots and affixes, creating cross-lingual understanding.
- **Intent Detection via LLM**: The AI classifies user prompts into functional commands to maintain a conversational flow.
- **Personalization**: Prompts and content are tailored using selected known/target languages and user level.
- **Session State Architecture**: Chat history, taught vocab (`df_memory`), and saved vocab (`vocab_bank`) are all managed via `st.session_state`.

## Technologies Used

- Streamlit – Interactive web app framework
- Cohere – Language model for generating responses
- Python, Pandas – Backend logic and data management

## Known Limitations

- Requires a valid Cohere API key and internet connection.
- Depends on correct JSON formatting from the LLM.
- Data is stored in session only (no persistent database yet).

## Future Improvements

- User login and persistent data storage
- Grammar-based interactive lessons
- Flashcard export or spaced repetition integration

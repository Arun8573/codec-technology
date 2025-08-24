# deepseek_chatbot.py

from openai import OpenAI

# ✅ Replace with your actual DeepSeek API key
DEEPSEEK_API_KEY = "sk-f54ef7b913b040b5b818cf7141bb1eba"

# Create a client for DeepSeek
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"   # DeepSeek API endpoint
)

def chat_with_deepseek():
    print("🤖 DeepSeek AI Chatbot (type 'exit' to quit)\n")
    conversation_history = []

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Chatbot: Goodbye! 👋")
            break

        conversation_history.append({"role": "user", "content": user_input})

        # Call DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",  # You can also try "deepseek-reasoner", "deepseek-coder"
            messages=conversation_history
        )

        bot_reply = response.choices[0].message.content
        print("Chatbot:", bot_reply)

        conversation_history.append({"role": "assistant", "content": bot_reply})

if __name__ == "__main__":
    chat_with_deepseek()

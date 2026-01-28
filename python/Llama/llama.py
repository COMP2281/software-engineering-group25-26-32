from ollama import chat

model = "llama3.1:8b"

# Init memory
messages = [{"role": "system", "content": ""}]

# For inferencing model
def inferModel(text=None):
    if not text:
        return None
    
    # Add user message to memory
    messages.append({"role": "user", "content": text})

    # Call model
    messages[0]['content'] = text
    response = chat(
        model=model,
        messages=messages
    )

    # Append response to memory
    messages.append({"role": "assistant", "content": response['message']['content']})

    return response
    # print(response['message']['content'])


while True:
    userMsg = input("Enter your message: ")
    response = inferModel(userMsg)
    if response == None:
        break
    print("Model response:", response['message']['content'])
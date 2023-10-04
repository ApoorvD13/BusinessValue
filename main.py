import openai

openai.api_key = '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'
messages = [{'role' : 'system' , "content" : "kind and helpful assistant"}]
while True:
    message = input("User : ")
    if message:
        messages.append(
            {"role": "user", "content": message},
        )
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )

    reply = chat.choices[0].message.content
    print(f"ChatGPT: {reply}")
    messages.append({"role": "assistant", "content": reply})
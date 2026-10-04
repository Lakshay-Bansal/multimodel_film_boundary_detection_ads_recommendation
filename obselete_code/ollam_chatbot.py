import ollama

response  = ollama.chat(model='llama3', messages=[
    {
        'role': 'user',
        'content': "There are three text descrption\
        1. My name is Lakshay\
        2. I am Sanjeev\
        3. I am LAkshay\
        \
        Match the text description and assign a weight to them",
    },
])
print(response['message']['response'])
import ollama
# print(help(ollama.chat))
# ollama.load('C:\Users\NH3183\.ollama\models\blobs\sha256-6a0746a1ec1aef3e7ec53868f220ff6e389f6f8ef87a01d77c96807de94ca2aa')
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
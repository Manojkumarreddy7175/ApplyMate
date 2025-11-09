from langchain_google_genai import ChatGoogleGenerativeAI;
print(ChatGoogleGenerativeAI(model='gemini-1.5-flash').invoke('Hello'))

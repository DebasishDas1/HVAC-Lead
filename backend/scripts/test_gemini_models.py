import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

def test_gemini_direct():
    api_key = os.getenv("GOOGLE_API_KEY")
    print(f"Testing with API Key: {api_key[:10]}...")
    
    models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-latest"]
    
    for model_name in models_to_try:
        print(f"\nTrying model: {model_name}")
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=0
            )
            response = llm.invoke([HumanMessage(content="Hello, are you there?")])
            print(f"✅ Success with {model_name}: {response.content}")
            return model_name
        except Exception as e:
            print(f"❌ Failed with {model_name}: {e}")
    
    return None

if __name__ == "__main__":
    test_gemini_direct()

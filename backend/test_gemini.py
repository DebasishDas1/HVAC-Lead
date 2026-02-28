import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def test_gemini():
    print("Testing Gemini (LLM2) connection...")
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment.")
            return

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key
        )
        response = llm.invoke("Say 'Gemini is online!'")
        print(f"Response: {response.content}")
        print("✅ Gemini connection test passed!")
    except Exception as e:
        print(f"❌ Gemini connection test failed: {e}")

if __name__ == "__main__":
    test_gemini()

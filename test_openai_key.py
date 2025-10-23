#!/usr/bin/env python3
"""
Quick test script to verify OpenAI API key is working
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_key():
    try:
        # Import OpenAI (legacy version for compatibility)
        import openai
        
        # Set API key
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        if not openai.api_key:
            print("❌ No OpenAI API key found in .env file")
            return False
        
        print(f"🔑 API Key found: {openai.api_key[:20]}...")
        
        # Test with a simple completion
        print("🧪 Testing API key...")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'API key works!'"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ Success! Response: {result}")
        return True
        
    except ImportError:
        print("❌ OpenAI library not installed. Run: pip install openai==0.28.1")
        return False
    except openai.error.AuthenticationError:
        print("❌ Invalid API key or authentication failed")
        return False
    except openai.error.RateLimitError:
        print("❌ Rate limit exceeded or quota exhausted")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_openai_key()
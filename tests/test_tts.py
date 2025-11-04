"""Simple test to verify TTS is working"""
import pyttsx3

print("Testing pyttsx3 TTS...")

try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
    
    print("Speaking: 'Hello, this is a test of text to speech'")
    engine.say("Hello, this is a test of text to speech")
    engine.runAndWait()
    
    print("Speaking: '15 yard pass completion'")
    engine.say("15 yard pass completion")
    engine.runAndWait()
    
    print("TTS test complete!")
except Exception as e:
    print(f"TTS Error: {e}")

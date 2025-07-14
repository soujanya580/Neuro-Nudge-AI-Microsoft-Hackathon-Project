from gtts import gTTS
import tempfile
import playsound
import os

class SpeechTranslator:
    def __init__(self):
        pass  # No initialization needed for gTTS
    
    def translate(self, text, target_language):
        # Add translation logic if needed
        return text
    
    def text_to_speech(self, text, language='en'):
        try:
            tts = gTTS(text=text, lang=language, slow=False)
            with tempfile.NamedTemporaryFile(delete=True, suffix='.mp3') as fp:
                temp_filename = f"{fp.name}.mp3"
                tts.save(temp_filename)
                playsound.playsound(temp_filename)
                os.remove(temp_filename)
        except Exception as e:
            raise Exception(f"TTS Error: {str(e)}")
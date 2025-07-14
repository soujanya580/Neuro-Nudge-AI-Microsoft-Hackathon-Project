from typing import Dict, Optional, List
import random
from dataclasses import dataclass
import time

@dataclass
class NudgeConfig:
    min_confidence: float = 0.4
    response_cooldown: float = 5.0  # seconds between same emotion responses
    language_map: Dict[str, Dict[str, List[str]]] = None

class NudgeEngine:
    def __init__(self, config: Optional[NudgeConfig] = None):
        # Pre-defined responses for quick access
        self._responses = {
            'happy': [
                "Keep smiling!",
                "Your joy is contagious!",
                "Your happiness brightens the room!"
            ],
            'sad': [
                "This will pass.",
                "I'm here for you.",
                "Would you like to talk about it?"
            ],
            'angry': [
                "Take a deep breath.",
                "Count to ten slowly.",
                "Try to find your calm center."
            ],
            'fear': [
                "You're safe now.",
                "Focus on the present moment.",
                "This feeling will fade."
            ],
            'surprise': [
                "Life is full of surprises!",
                "Wow! That's unexpected!",
                "Interesting development!"
            ],
            'disgust': [
                "Let it go.",
                "Change your focus.",
                "Don't let it bother you."
            ],
            'neutral': [
                "How are you really feeling?",
                "Take a moment to reflect.",
                "What's on your mind?"
            ]
        }
        
        # Configuration with defaults
        self.config = config or NudgeConfig()
        
        # Response tracking
        self.last_responses = {}
        self.last_response_time = {}
        
        # Initialize language mappings if not provided
        if self.config.language_map is None:
            self.config.language_map = {
                'kn': {  # Kannada
                    'happy': ["ಮುಗುಳು ನಗು!", "ನಿಮ್ಮ ಸಂತೋಷ ಸಾಂಕ್ರಾಮಿಕ!"],
                    'sad': ["ಇದು ಕಳೆದು ಹೋಗುತ್ತದೆ.", "ನಾನು ನಿಮ್ಮ ಜೊತೆ ಇದ್ದೇನೆ."]
                },
                'hi': {  # Hindi
                    'happy': ["मुस्कुराते रहो!", "आपकी खुशी संक्रामक है!"],
                    'sad': ["यह बीत जाएगा।", "मैं आपके साथ हूं।"]
                }
            }

    def get_response(self, emotions: Optional[Dict[str, float]], user_id: str = "default") -> str:
        """
        Get appropriate response based on detected emotions
        with cooldown period for same emotion responses.
        
        Args:
            emotions: Dictionary of emotion probabilities
            user_id: Unique identifier for response tracking
            
        Returns:
            str: Appropriate response text
        """
        # Default response if no emotions detected
        if not emotions:
            return self._get_random_response('neutral')
        
        # Get dominant emotion
        dominant_emotion, confidence = max(emotions.items(), key=lambda x: x[1])
        
        # Check confidence threshold
        if confidence < self.config.min_confidence:
            return self._get_random_response('neutral')
        
        # Check response cooldown
        current_time = time.time()
        last_time = self.last_response_time.get(user_id, {}).get(dominant_emotion, 0)
        
        if current_time - last_time < self.config.response_cooldown:
            return self._get_random_response('neutral')
        
        # Update tracking
        self.last_response_time.setdefault(user_id, {})[dominant_emotion] = current_time
        
        return self._get_random_response(dominant_emotion)

    def get_nudge(self, emotions: Optional[Dict[str, float]], 
                 language: str = 'en', 
                 user_id: str = "default") -> str:
        """
        Get language-appropriate nudge based on emotions
        
        Args:
            emotions: Dictionary of emotion probabilities
            language: Target language code (e.g., 'en', 'hi', 'kn')
            user_id: Unique identifier for response tracking
            
        Returns:
            str: Appropriate nudge in requested language
        """
        base_response = self.get_response(emotions, user_id)
        
        # Return translated response if available
        if language != 'en' and language in self.config.language_map:
            lang_responses = self.config.language_map[language]
            emotion = max(emotions.items(), key=lambda x: x[1])[0] if emotions else 'neutral'
            if emotion in lang_responses:
                return random.choice(lang_responses[emotion])
        
        return base_response

    def _get_random_response(self, emotion: str) -> str:
        """Get random response for specified emotion"""
        return random.choice(self._responses.get(emotion, self._responses['neutral']))

    def add_custom_response(self, emotion: str, response: str):
        """Add custom response for an emotion"""
        if emotion not in self._responses:
            self._responses[emotion] = []
        self._responses[emotion].append(response)

    def add_language_responses(self, language: str, responses: Dict[str, List[str]]):
        """Add responses for a new language"""
        if language not in self.config.language_map:
            self.config.language_map[language] = {}
        for emotion, texts in responses.items():
            if emotion not in self.config.language_map[language]:
                self.config.language_map[language][emotion] = []
            self.config.language_map[language][emotion].extend(texts)


# Example usage
if __name__ == "__main__":
    # Initialize with default config
    nudger = NudgeEngine()
    
    # Test with emotions
    test_emotions = {'happy': 0.8, 'sad': 0.1}
    print("English response:", nudger.get_response(test_emotions))
    print("Hindi response:", nudger.get_nudge(test_emotions, 'hi'))
    
    # Add custom responses
    nudger.add_custom_response('happy', "You're doing great!")
    print("Custom response:", nudger.get_response({'happy': 0.9}))
    
    # Add new language
    nudger.add_language_responses('de', {
        'happy': ["Weiter so!", "Deine Freude ist ansteckend!"],
        'sad': ["Das wird vorübergehen.", "Ich bin für dich da."]
    })
    print("German response:", nudger.get_nudge(test_emotions, 'de'))
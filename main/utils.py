"""
פונקציות עזר למודול main
Helper functions for the main module
"""

import requests
from django.conf import settings
import uuid
import json


def get_or_create_session_id(request):
    """
    קבלת או יצירת מזהה סשן למשתמש
    Get or create a session ID for the user
    """
    if not request.session.get('ai_session_id'):
        request.session['ai_session_id'] = str(uuid.uuid4())
    return request.session['ai_session_id']


def build_conversation_context(conversation):
    """
    בניית הקשר השיחה עבור OpenAI API
    Build conversation context for OpenAI API
    
    Args:
        conversation: AIConversation object
    
    Returns:
        list: רשימת הודעות עבור OpenAI API
    """
    messages = [
        {
            'role': 'system',
            'content': 'You are a precise translator for AI image generation with conversation memory. You remember the conversation history and can build upon previous requests. Always translate to EXACT, specific English that emphasizes the EXACT quantity requested. Be extremely clear about numbers. Examples: "שתי בננות" = "exactly two yellow bananas only", "בננה אחת" = "one single yellow banana only", "שלוש תפוחים" = "exactly three red apples only", "5 עגבניות" = "exactly five red tomatoes only". Always add "only" to emphasize the exact count and prevent AI from adding extra objects. IMPORTANT: Always specify natural colors for fruits and vegetables - bananas are yellow, apples are red or green, tomatoes are red, oranges are orange, etc. For art requests like "ציור של" (painting of), translate to just the subject without mentioning painting, canvas, frame, or background - focus on the pure subject. CRITICAL: ALWAYS preserve gender in Hebrew noun translations. "אקרובטית" (feminine) = "female acrobat", "אקרובט" (masculine) = "male acrobat", "רופאה" (feminine) = "female doctor", "רופא" (masculine) = "male doctor", "נהגת" (feminine) = "female driver", "נהג" (masculine) = "male driver". Specialized terms: "טיסו" = "aerial silk", "חבל" = "rope", "טרפז" = "trapeze", "פולדנס" = "pole dance", "ריקוד בטן" = "belly dance". Gender specification is MANDATORY for all gendered Hebrew nouns. CONTEXT AWARENESS: When user refers to previous images or makes modifications (like color changes, size, angle), translate to focus ONLY on the specific change requested while keeping everything else the same. For color changes like "תעשה אותה אדומה" or "בצבע אדום", translate as "keep the same shape, size, and angle, but change ONLY the color to red". Use simple, clear, specific language with natural colors.'
        }
    ]
    
    # Add conversation history (last 10 messages to avoid token limits)
    all_messages = list(conversation.messages.all().order_by('created_at'))
    recent_messages = all_messages[-10:] if len(all_messages) > 10 else all_messages
    
    for message in recent_messages:
        if message.message_type == 'user':
            messages.append({
                'role': 'user',
                'content': f'Hebrew request: "{message.content}"'
            })
        elif message.message_type == 'ai' and message.translated_prompt:
            messages.append({
                'role': 'assistant',
                'content': f'Translation: {message.translated_prompt}'
            })
    
    return messages


def translate_hebrew_to_english_with_context(text, conversation=None):
    """
    תרגום טקסט מעברית לאנגלית עם הקשר השיחה
    Translate Hebrew text to English with conversation context
    
    Args:
        text (str): הטקסט בעברית לתרגום / Hebrew text to translate
        conversation: AIConversation object for context
    
    Returns:
        str: הטקסט המתורגם באנגלית / Translated text in English
    """
    try:
        openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if not openai_api_key:
            print("⚠️ DEBUG: OpenAI API key not found, returning original text")
            return text
        
        print(f"📤 DEBUG: OpenAI translation input: '{text}'")
        if conversation:
            print(f"🔄 DEBUG: Using conversation context with {conversation.messages.count()} messages")
        
        # Use OpenAI for translation
        headers = {
            'Authorization': f'Bearer {openai_api_key}',
            'Content-Type': 'application/json'
        }
        
        # Build messages with context if available
        if conversation and conversation.messages.exists():
            messages = build_conversation_context(conversation)
            messages.append({
                'role': 'user',
                'content': f'New Hebrew request (consider previous context): "{text}"'
            })
        else:
            messages = [
                {
                    'role': 'system',
                    'content': 'You are a precise translator for AI image generation. Always translate to EXACT, specific English that emphasizes the EXACT quantity requested. Be extremely clear about numbers. Examples: "שתי בננות" = "exactly two yellow bananas only", "בננה אחת" = "one single yellow banana only", "שלוש תפוחים" = "exactly three red apples only", "5 עגבניות" = "exactly five red tomatoes only". Always add "only" to emphasize the exact count and prevent AI from adding extra objects. IMPORTANT: Always specify natural colors for fruits and vegetables - bananas are yellow, apples are red or green, tomatoes are red, oranges are orange, etc. For art requests like "ציור של" (painting of), translate to just the subject without mentioning painting, canvas, frame, or background - focus on the pure subject. CRITICAL: ALWAYS preserve gender in Hebrew noun translations. "אקרובטית" (feminine) = "female acrobat", "אקרובט" (masculine) = "male acrobat", "רופאה" (feminine) = "female doctor", "רופא" (masculine) = "male doctor", "נהגת" (feminine) = "female driver", "נהג" (masculine) = "male driver". Specialized terms: "טיסו" = "aerial silk", "חבל" = "rope", "טרפז" = "trapeze", "פולדנס" = "pole dance", "ריקוד בטן" = "belly dance". Gender specification is MANDATORY for all gendered Hebrew nouns. Use simple, clear, specific language with natural colors.'
                },
                {
                    'role': 'user',
                    'content': f'Translate this Hebrew text to precise English for AI image generation, being very specific about quantities and gender when applicable, removing any reference to paintings, frames, or backgrounds: "{text}"'
                }
            ]
        
        payload = {
            'model': 'gpt-4',
            'messages': messages,
            'max_tokens': 150,
            'temperature': 0.1
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            translated_text = result['choices'][0]['message']['content'].strip()
            
            # Clean up common OpenAI response prefixes
            if translated_text.startswith('Translation: "') and translated_text.endswith('"'):
                translated_text = translated_text[14:-1]  # Remove 'Translation: "' and final '"'
            elif translated_text.startswith('Translate to: "') and translated_text.endswith('"'):
                translated_text = translated_text[15:-1]  # Remove 'Translate to: "' and final '"'
            elif translated_text.startswith('"') and translated_text.endswith('"'):
                translated_text = translated_text[1:-1]  # Remove surrounding quotes
            elif translated_text.startswith('Translation: '):
                translated_text = translated_text[13:]  # Remove 'Translation: ' prefix
            
            print(f"📥 DEBUG: OpenAI translation output: '{translated_text}'")
            print(f"🌐 DEBUG: OpenAI translation: '{text}' → '{translated_text}'")
            return translated_text
        else:
            print(f"⚠️ DEBUG: OpenAI API error: {response.status_code}")
            print(f"⚠️ DEBUG: OpenAI error response: {response.text}")
            return text
            
    except Exception as e:
        print(f"⚠️ DEBUG: Translation error: {str(e)}")
        return text


def translate_hebrew_to_english(text):
    """
    תרגום טקסט מעברית לאנגלית (גרסה ישנה לתאימות אחורה)
    Translate Hebrew text to English (legacy version for backward compatibility)
    """
    return translate_hebrew_to_english_with_context(text, None)


def clean_prompt_for_ai(prompt):
    """
    ניקוי והכנת prompt עבור AI - מסיר רקעים לא רצויים ומוסיף הנחיות ברורות
    Clean and prepare prompt for AI - removes unwanted backgrounds and adds clear instructions
    
    Args:
        prompt (str): הפרומפט המתורגם / Translated prompt
    
    Returns:
        str: פרומפט מנוקה ומוכן / Clean and ready prompt
    """
    # Remove painting/artwork context words that cause unwanted backgrounds
    painting_words = ['painting', 'artwork', 'canvas', 'frame', 'wall', 'gallery', 'museum']
    
    cleaned_prompt = prompt.lower()
    for word in painting_words:
        # Remove phrases like "a painting of", "an artwork of", etc.
        cleaned_prompt = cleaned_prompt.replace(f'a {word} of ', '')
        cleaned_prompt = cleaned_prompt.replace(f'an {word} of ', '')
        cleaned_prompt = cleaned_prompt.replace(f'{word} of ', '')
        cleaned_prompt = cleaned_prompt.replace(f'{word} ', '')
    
    # Clean up extra spaces and capitalize first letter
    cleaned_prompt = ' '.join(cleaned_prompt.split()).strip()
    if cleaned_prompt:
        cleaned_prompt = cleaned_prompt[0].upper() + cleaned_prompt[1:]
    
    # Enhanced prompt for better results with proper colors and transparent background
    return f"{cleaned_prompt}, vibrant natural colors, clean transparent background, high quality professional photography, studio lighting, no background, isolated object, realistic textures"


def create_freepik_payload(clean_prompt):
    """
    יצירת payload עבור Freepik API
    Create payload for Freepik API
    
    Args:
        clean_prompt (str): הפרומפט המנוקה / Clean prompt
    
    Returns:
        dict: הPayload עבור הAPI / Payload for the API
    """
    return {
        "prompt": clean_prompt,
        "num_images": 1,
        # פרמטרים נוספים שניתן להוסיף בעתיד / Additional parameters for future use
        # "image": {"size": "1024x1024"},
        # "mode": "creative",
        # "style": "photo",
        # "negative_prompt": "multiple objects, cluttered, messy, blurry, low quality, distorted, crowded scene, background objects, busy composition, extra elements"
    }


def create_flux_payload(prompt, init_image=None, strength=None):
    """Create payload for Flux Pro 1.1 via Replicate with optional image-to-image support"""
    import random
    
    payload = {
        "version": "black-forest-labs/flux-1.1-pro",
        "input": {
            "prompt": prompt,
            "width": 1024,
            "height": 1024,
            "num_outputs": 1,
            "output_format": "png",
            "output_quality": 90,
            "num_inference_steps": 25,
            "guidance_scale": 3.0,
            "seed": random.randint(1, 1000000),  # Random seed for variety
            # Negative prompt to avoid unwanted results
            "negative_prompt": "black banana, dark banana, multiple bananas, two bananas, three bananas, many bananas, background, wallpaper, room, kitchen, table, plate, bowl, multiple objects, crowded scene, blurry, low quality, distorted, unrealistic colors, painting style, artistic style"
        }
    }
    
    # הוספת פרמטרים ל-Image-to-Image אם נדרש
    if init_image and strength:
        payload["input"]["image"] = init_image
        payload["input"]["strength"] = strength
        print(f"🔄 DEBUG: Using Image-to-Image mode - strength: {strength}")
    
    return payload


def send_flux_request(prompt, replicate_api_key, init_image=None, strength=0.4):
    """Send request to Flux Pro 1.1 via Replicate API with optional image-to-image support"""
    import time
    
    headers = {
        'Authorization': f'Token {replicate_api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = create_flux_payload(prompt, init_image, strength)
    
    if init_image:
        print(f"🔄 DEBUG: Sending Image-to-Image to Flux Pro 1.1")
        print(f"📷 DEBUG: Base image: {init_image}")
        print(f"💪 DEBUG: Strength: {strength}")
        print(f"📝 DEBUG: Prompt: '{prompt}'")
    else:
        print(f"🚀 DEBUG: Sending Text-to-Image to Flux Pro 1.1: '{prompt}'")
    
    print(f"📦 DEBUG: Flux payload: {payload}")
    
    # Create prediction
    response = requests.post(
        'https://api.replicate.com/v1/predictions',
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code != 201:
        raise Exception(f"Failed to create Flux prediction: {response.status_code} - {response.text}")
    
    prediction = response.json()
    prediction_id = prediction['id']
    
    print(f"🔄 DEBUG: Flux prediction created: {prediction_id}")
    print(f"⏳ DEBUG: Waiting for Flux to generate image...")
    
    # Poll for completion (Flux is usually fast, 5-15 seconds)
    max_wait_time = 120  # 2 minutes max
    poll_interval = 3  # Check every 3 seconds
    waited_time = 0
    
    while waited_time < max_wait_time:
        check_response = requests.get(
            f'https://api.replicate.com/v1/predictions/{prediction_id}',
            headers=headers,
            timeout=10
        )
        
        if check_response.status_code == 200:
            result = check_response.json()
            status = result.get('status')
            
            print(f"🔍 DEBUG: Flux status: {status} (waited {waited_time}s)")
            
            if status == 'succeeded':
                output = result.get('output')
                print(f"🔍 DEBUG: Full Flux output: {output}")
                
                if output:
                    # Handle different output formats
                    if isinstance(output, list) and len(output) > 0:
                        image_url = output[0]
                    elif isinstance(output, str):
                        image_url = output
                    elif isinstance(output, dict) and 'url' in output:
                        image_url = output['url']
                    else:
                        print(f"⚠️ DEBUG: Unexpected output format: {type(output)} - {output}")
                        raise Exception(f"Unexpected Flux output format: {type(output)}")
                    
                    print(f"✅ DEBUG: Flux completed! Image URL: {image_url}")
                    
                    # Validate URL
                    if not image_url or len(image_url) < 10 or not image_url.startswith('http'):
                        raise Exception(f"Invalid image URL from Flux: '{image_url}'")
                    
                    return image_url
                else:
                    raise Exception("Flux completed but no output data")
                    
            elif status == 'failed':
                error = result.get('error', 'Unknown Flux error')
                raise Exception(f"Flux generation failed: {error}")
            
            elif status in ['starting', 'processing']:
                # Still processing, continue waiting
                time.sleep(poll_interval)
                waited_time += poll_interval
            else:
                raise Exception(f"Unknown Flux status: {status}")
        else:
            raise Exception(f"Failed to check prediction status: {check_response.status_code}")
    
    raise Exception(f"Flux generation timed out after {max_wait_time} seconds")

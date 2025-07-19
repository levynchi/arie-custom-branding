/**
 * דוגמת שימוש ב-Image-to-Image API
 * Example usage of Image-to-Image API
 */

class ImageToImageDemo {
    constructor() {
        this.conversationId = null;
        this.currentImageUrl = null;
        this.apiUrl = '/generate_ai_design/';
        
        console.log('🎨 Image-to-Image Demo initialized');
    }

    /**
     * שליחת בקשה ליצירת תמונה (Text-to-Image או Image-to-Image)
     * Send request to create image (Text-to-Image or Image-to-Image)
     */
    async generateImage(prompt, productId = '', productName = '') {
        try {
            console.log(`📤 Sending request: "${prompt}"`);
            console.log(`🔄 Current conversation ID: ${this.conversationId}`);
            console.log(`📷 Current image URL: ${this.currentImageUrl ? 'Available' : 'None'}`);
            
            const requestData = {
                prompt: prompt,
                product_id: productId,
                product_name: productName,
                conversation_id: this.conversationId
            };

            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();

            if (result.success) {
                // עדכון מזהה השיחה
                this.conversationId = result.conversation_id;
                this.currentImageUrl = result.image_url;
                
                console.log('✅ Image generated successfully!');
                console.log(`🎯 Used Image-to-Image: ${result.used_image_to_image ? 'YES' : 'NO'}`);
                console.log(`📷 New image URL: ${result.image_url}`);
                console.log(`🤖 AI Service: ${result.ai_service}`);
                
                if (result.used_image_to_image) {
                    console.log(`🔄 Base image was: ${result.base_image_url}`);
                    console.log(`💡 This was a modification of existing image!`);
                } else {
                    console.log(`✨ This was a new image created from text!`);
                }
                
                return result;
            } else {
                console.error('❌ Error:', result.error);
                throw new Error(result.error);
            }
        } catch (error) {
            console.error('💥 Request failed:', error);
            throw error;
        }
    }

    /**
     * דוגמת שיחה רצופה
     * Example of continuous conversation
     */
    async demonstrateConversation() {
        console.log('🚀 Starting Image-to-Image demonstration...');
        
        try {
            // שלב 1: יצירת תמונה ראשונה
            console.log('\n--- שלב 1: יצירת תמונה ראשונה ---');
            let result1 = await this.generateImage('בננה צהובה');
            this.displayResult('בננה צהובה', result1);
            
            // המתנה קצרה
            await this.sleep(2000);
            
            // שלב 2: שינוי צבע (אמור להשתמש ב-Image-to-Image)
            console.log('\n--- שלב 2: שינוי צבע ---');
            let result2 = await this.generateImage('עכשיו בצבע אדום');
            this.displayResult('עכשיו בצבע אדום', result2);
            
            // המתנה קצרה
            await this.sleep(2000);
            
            // שלב 3: שינוי זווית (אמור להשתמש ב-Image-to-Image)
            console.log('\n--- שלב 3: שינוי זווית ---');
            let result3 = await this.generateImage('מזווית אחרת');
            this.displayResult('מזווית אחרת', result3);
            
            // המתנה קצרה
            await this.sleep(2000);
            
            // שלב 4: נושא חדש (אמור להשתמש ב-Text-to-Image)
            console.log('\n--- שלב 4: נושא חדש ---');
            let result4 = await this.generateImage('תפוח ירוק');
            this.displayResult('תפוח ירוק', result4);
            
            console.log('🎉 Demonstration completed successfully!');
            
        } catch (error) {
            console.error('💥 Demonstration failed:', error);
        }
    }

    /**
     * הצגת תוצאה
     * Display result
     */
    displayResult(prompt, result) {
        console.log('=' * 50);
        console.log(`📝 Prompt: "${prompt}"`);
        console.log(`🎯 Mode: ${result.used_image_to_image ? 'Image-to-Image' : 'Text-to-Image'}`);
        console.log(`🤖 AI Service: ${result.ai_service}`);
        console.log(`📷 Image URL: ${result.image_url}`);
        console.log(`🗂️ Conversation ID: ${result.conversation_id}`);
        
        if (result.used_image_to_image && result.base_image_url) {
            console.log(`🔗 Based on: ${result.base_image_url}`);
        }
        
        console.log('=' * 50);
        
        // הצגה בדפדפן אם אפשר
        if (typeof document !== 'undefined') {
            this.displayImageInBrowser(prompt, result);
        }
    }

    /**
     * הצגת תמונה בדפדפן
     * Display image in browser
     */
    displayImageInBrowser(prompt, result) {
        const container = document.getElementById('demo-container') || document.body;
        
        const imageDiv = document.createElement('div');
        imageDiv.className = 'generated-image';
        imageDiv.style.cssText = `
            margin: 20px 0;
            padding: 15px;
            border: 2px solid ${result.used_image_to_image ? '#e53e3e' : '#38b2ac'};
            border-radius: 10px;
            background: ${result.used_image_to_image ? '#fff5f5' : '#e6fffa'};
        `;
        
        imageDiv.innerHTML = `
            <h3 style="margin-top: 0; color: #2d3748;">
                ${result.used_image_to_image ? '🔄 Image-to-Image' : '✨ Text-to-Image'}
            </h3>
            <p><strong>Prompt:</strong> "${prompt}"</p>
            <p><strong>AI Service:</strong> ${result.ai_service}</p>
            <img src="${result.image_url}" alt="${prompt}" 
                 style="max-width: 300px; max-height: 300px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            ${result.used_image_to_image ? 
                `<p style="font-size: 0.9em; color: #718096;">🔗 Modified from previous image</p>` : 
                `<p style="font-size: 0.9em; color: #718096;">✨ Created from scratch</p>`
            }
        `;
        
        container.appendChild(imageDiv);
    }

    /**
     * המתנה
     * Sleep function
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * קבלת CSRF token
     * Get CSRF token
     */
    getCsrfToken() {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenElement) {
            return tokenElement.value;
        }
        
        // חיפוש בקוקיז
        const name = 'csrftoken';
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [key, value] = cookie.trim().split('=');
            if (key === name) {
                return decodeURIComponent(value);
            }
        }
        
        return '';
    }

    /**
     * בדיקת מילות מפתח לשינוי
     * Check for modification keywords
     */
    isModificationRequest(prompt) {
        const keywords = [
            'שנה', 'שני', 'אדום', 'כחול', 'ירוק', 'צהוב', 'סגול', 'כתום', 'ורוד', 'שחור', 'לבן',
            'זווית', 'מזווית', 'צד', 'מימין', 'משמאל', 'מלמעלה', 'מלמטה',
            'גדול יותר', 'קטן יותר', 'עבה יותר', 'דק יותר',
            'עם', 'בלי', 'הוסף', 'הסר', 'החלף', 'עכשיו'
        ];
        
        return keywords.some(keyword => prompt.toLowerCase().includes(keyword));
    }
}

// יצירת instance גלובלי
const imageToImageDemo = new ImageToImageDemo();

// פונקציות עזר גלובליות
window.generateImage = (prompt, productId = '', productName = '') => {
    return imageToImageDemo.generateImage(prompt, productId, productName);
};

window.startDemo = () => {
    return imageToImageDemo.demonstrateConversation();
};

// דוגמאות שימוש
console.log(`
🎨 Image-to-Image Demo Ready!

דוגמאות שימוש / Usage Examples:
================================

// יצירת תמונה חדשה
await generateImage('בננה צהובה');

// שינוי התמונה הקיימת
await generateImage('עכשיו בצבע אדום');
await generateImage('מזווית אחרת');
await generateImage('גדול יותר');

// הרצת הדגמה מלאה
await startDemo();

מילות מפתח לזיהוי שינויים:
• צבעים: אדום, כחול, ירוק, צהוב...
• זוויות: זווית, מזווית, צד, מימין...
• גדלים: גדול יותר, קטן יותר...
• שינויים: שנה, הוסף, הסר, עכשיו...
`);

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ImageToImageDemo;
}

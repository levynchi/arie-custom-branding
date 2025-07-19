/**
 * דוגמת JavaScript לשימוש במערכת היסטוריית שיחות AI
 * Example JavaScript for using AI conversation history system
 */

// משתנה גלובלי לשמירת מזהה השיחה הנוכחית
let currentConversationId = null;

// פונקציה לשליחת בקשת AI עם הקשר
async function generateAIImageWithHistory(prompt, productId = null) {
    const requestData = {
        prompt: prompt,
        product_id: productId,
        conversation_id: currentConversationId  // שליחת מזהה השיחה הנוכחית
    };
    
    try {
        const response = await fetch('/generate-ai-design/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // שמירת מזהה השיחה לבקשות הבאות
            currentConversationId = result.conversation_id;
            
            console.log('תמונה נוצרה בהצלחה!');
            console.log('מזהה שיחה:', result.conversation_id);
            console.log('כותרת השיחה:', result.conversation_title);
            console.log('URL תמונה:', result.image_url);
            
            // הצגת התמונה
            displayGeneratedImage(result);
            
            // עדכון רשימת השיחות
            loadConversationsList();
            
        } else {
            console.error('שגיאה:', result.error);
        }
        
    } catch (error) {
        console.error('שגיאת רשת:', error);
    }
}

// פונקציה לטעינת רשימת השיחות
async function loadConversationsList() {
    try {
        const response = await fetch('/ai-conversations/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayConversationsList(result.conversations);
        }
        
    } catch (error) {
        console.error('שגיאה בטעינת שיחות:', error);
    }
}

// פונקציה לטעינת היסטוריית שיחה ספציפית
async function loadConversationHistory(conversationId) {
    try {
        const response = await fetch(`/conversation-history/?conversation_id=${conversationId}`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentConversationId = conversationId;
            displayConversationHistory(result.conversation, result.messages);
        }
        
    } catch (error) {
        console.error('שגיאה בטעינת היסטוריה:', error);
    }
}

// פונקציה לבדוק שיחה חדשה
function startNewConversation() {
    currentConversationId = null;
    clearCurrentConversation();
    console.log('שיחה חדשה התחילה');
}

// דוגמאות לשימוש:

// 1. שיחה חדשה - בקשה ראשונה
// generateAIImageWithHistory("בננה אחת", 123);

// 2. המשך אותה שיחה - בקשה שנייה
// generateAIImageWithHistory("בזווית אחרת", 123);

// 3. המשך אותה שיחה - בקשה שלישית  
// generateAIImageWithHistory("בצבע אדום", 123);

// דוגמאות לממשק משתמש:
function displayGeneratedImage(result) {
    const imageContainer = document.getElementById('generated-image-container');
    if (imageContainer) {
        imageContainer.innerHTML = `
            <img src="${result.image_url}" alt="Generated AI Image" class="generated-image">
            <div class="image-info">
                <p>שירות AI: ${result.ai_service}</p>
                <p>גודל: ${result.dimensions}</p>
                <p>מזהה שיחה: ${result.conversation_id}</p>
                <a href="${result.cmyk_url}" download>הורדת קובץ CMYK להדפסה</a>
            </div>
        `;
    }
}

function displayConversationsList(conversations) {
    const listContainer = document.getElementById('conversations-list');
    if (listContainer && conversations) {
        listContainer.innerHTML = conversations.map(conv => `
            <div class="conversation-item" onclick="loadConversationHistory(${conv.id})">
                <h4>${conv.title}</h4>
                <p>מוצר: ${conv.product_name || 'כללי'}</p>
                <p>הודעות: ${conv.message_count}</p>
                <small>${new Date(conv.updated_at).toLocaleString('he-IL')}</small>
            </div>
        `).join('');
    }
}

function displayConversationHistory(conversation, messages) {
    const historyContainer = document.getElementById('conversation-history');
    if (historyContainer && messages) {
        historyContainer.innerHTML = `
            <h3>${conversation.title}</h3>
            <div class="messages">
                ${messages.map(msg => `
                    <div class="message ${msg.type}">
                        <div class="message-content">${msg.content}</div>
                        ${msg.image_url ? `<img src="${msg.image_url}" class="message-image">` : ''}
                        <small>${new Date(msg.created_at).toLocaleString('he-IL')}</small>
                    </div>
                `).join('')}
            </div>
        `;
    }
}

// פונקציית עזר לקבלת CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// טעינת רשימת השיחות בעת טעינת העמוד
document.addEventListener('DOMContentLoaded', function() {
    loadConversationsList();
});

// Custom Design Page JavaScript

console.log('custom_design.js loaded successfully');

// Global variables
let selectedElement = null;
let elementCounter = 0;
let isDragging = false;
let dragOffset = { x: 0, y: 0 };
let selectedProduct = null;
let currentConversationId = null; // מזהה השיחה הנוכחית
let transparentFilter = false; // פילטר תמונות עם רקע שקוף
let vectorFilter = false; // פילטר תמונות וקטוריות
let lastSearchResults = []; // תוצאות החיפוש האחרונות למען הסינון

// Product Selection - Dropdown Functions
function selectProductFromDropdown(element, event) {
    console.log('selectProductFromDropdown called', element.dataset.productName);
    
    if (event) {
        event.preventDefault();
    }
    
    // עדכון הטקסט בכפתור הראשי
    const selectedText = document.getElementById('selectedProductText');
    selectedText.innerHTML = `<i class="fas fa-check me-2"></i>${element.dataset.productName}`;
    
    // הסרת הבחירה מכל האלמנטים
    document.querySelectorAll('.product-dropdown-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // הוספת בחירה לאלמנט הנוכחי
    element.classList.add('active');
    
    // עדכון המוצר הנבחר
    selectedProduct = { 
        id: element.dataset.productId, 
        image: element.dataset.productImage,
        name: element.dataset.productName,
        price: element.dataset.productPrice
    };
    
    // עדכון רקע הקנבס
    updateCanvasBackground(element);
    hideNoProductMessage(); // הסתרת הודעת האזהרה
    
    // סגירת ה-dropdown
    setTimeout(closeDropdownManually, 100);
}

// Product Message Functions
function showNoProductMessage() {
    const message = document.getElementById('noProductMessage');
    if (message) {
        message.style.display = 'block';
        // Scroll to the message
        message.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function hideNoProductMessage() {
    const message = document.getElementById('noProductMessage');
    if (message) {
        message.style.display = 'none';
    }
}

function updateCanvasBackground(productElement) {
    const canvas = document.getElementById('designCanvas');
    const placeholderText = document.getElementById('placeholderText');
    const productImage = productElement.dataset.productImage;
    
    if (productImage && productImage.trim() !== '') {
        canvas.style.backgroundImage = `url('${productImage}')`;
        canvas.classList.add('with-product');
        placeholderText.style.display = 'none';
    } else {
        // Show placeholder for products without image
        canvas.style.backgroundImage = 'none';
        canvas.classList.remove('with-product');
        placeholderText.style.display = 'block';
        placeholderText.innerHTML = `
            <i class="fas fa-tshirt" style="font-size: 100px; opacity: 0.3;"></i>
            <p>נבחר מוצר: ${productElement.dataset.productName}</p>
            <p style="font-size: 0.9em; color: #666;">התחל לעצב על המוצר</p>
        `;
    }
    
    // Update print dimensions display
    const printDimensionsDiv = document.getElementById('printDimensions');
    const printDimensionsText = document.getElementById('printDimensionsText');
    const printSize = productElement.dataset.productPrintSize;
    
    if (printSize) {
        printDimensionsText.textContent = printSize;
        printDimensionsDiv.style.display = 'block';
    } else {
        printDimensionsDiv.style.display = 'none';
    }
}

// Original Product Selection (keeping for compatibility)
function selectProduct(productElement) {
    // Remove selection from all products
    document.querySelectorAll('.product-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    // Add selection to clicked product
    productElement.classList.add('selected');
    
    // Get product data
    const productId = productElement.dataset.productId;
    const productImage = productElement.dataset.productImage;
    selectedProduct = { id: productId, image: productImage };
    
    // Get print dimensions if available
    const printSizeElement = productElement.querySelector('.product-print-size');
    let printDimensions = null;
    if (printSizeElement) {
        printDimensions = printSizeElement.textContent.trim();
    }
    
    // Update canvas background
    const canvas = document.getElementById('designCanvas');
    const placeholderText = document.getElementById('placeholderText');
    
    if (productImage && productImage.trim() !== '') {
        canvas.style.backgroundImage = `url('${productImage}')`;
        canvas.classList.add('with-product');
        placeholderText.style.display = 'none';
    } else {
        // Show placeholder for products without image
        canvas.style.backgroundImage = 'none';
        canvas.classList.remove('with-product');
        placeholderText.style.display = 'block';
        placeholderText.innerHTML = `
            <i class="fas fa-tshirt" style="font-size: 100px; opacity: 0.3;"></i>
            <p>נבחר מוצר: ${productElement.querySelector('.product-name').textContent}</p>
            <p style="font-size: 0.9em; color: #666;">התחל לעצב על המוצר</p>
        `;
    }
    
    // Update print dimensions display
    const printDimensionsDiv = document.getElementById('printDimensions');
    const printDimensionsText = document.getElementById('printDimensionsText');
    
    if (printDimensions) {
        printDimensionsText.textContent = printDimensions;
        printDimensionsDiv.style.display = 'block';
    } else {
        printDimensionsDiv.style.display = 'none';
    }
}

// Add Elements
function addText() {
    console.log('addText function called');
    // Check if a product is selected
    if (!selectedProduct || !selectedProduct.id) {
        showNoProductMessage();
        return;
    }
    
    const canvas = document.getElementById('designCanvas');
    const textElement = document.createElement('div');
    textElement.className = 'design-element text-element';
    textElement.id = 'element_' + (++elementCounter);
    textElement.innerHTML = `
        <span contenteditable="true" style="outline: none;">טקסט חדש</span>
        <button class="delete-btn" onclick="deleteElement('${textElement.id}')">&times;</button>
    `;
    textElement.style.left = '50px';
    textElement.style.top = '50px';
    textElement.style.fontSize = '24px';
    textElement.style.color = '#000000';
    
    canvas.appendChild(textElement);
    makeElementInteractive(textElement);
}

function addImage(event) {
    console.log('addImage function called');
    // Check if a product is selected
    if (!selectedProduct || !selectedProduct.id) {
        showNoProductMessage();
        return;
    }
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const canvas = document.getElementById('designCanvas');
            const imageElement = document.createElement('div');
            imageElement.className = 'design-element';
            imageElement.id = 'element_' + (++elementCounter);
            imageElement.innerHTML = `
                <img src="${e.target.result}" class="image-element" style="width: 100px; height: 100px;">
                <button class="delete-btn" onclick="deleteElement('${imageElement.id}')">&times;</button>
            `;
            imageElement.style.left = '100px';
            imageElement.style.top = '100px';
            
            canvas.appendChild(imageElement);
            makeElementInteractive(imageElement);
        };
        reader.readAsDataURL(file);
    }
}

function addEmoji(emoji) {
    // Check if a product is selected
    if (!selectedProduct || !selectedProduct.id) {
        showNoProductMessage();
        return;
    }
    
    const canvas = document.getElementById('designCanvas');
    const emojiElement = document.createElement('div');
    emojiElement.className = 'design-element text-element';
    emojiElement.id = 'element_' + (++elementCounter);
    emojiElement.innerHTML = `
        <span style="font-size: 48px; line-height: 1;">${emoji}</span>
        <button class="delete-btn" onclick="deleteElement('${emojiElement.id}')">&times;</button>
    `;
    emojiElement.style.left = '150px';
    emojiElement.style.top = '150px';
    
    canvas.appendChild(emojiElement);
    makeElementInteractive(emojiElement);
    
    // Hide emoji picker
    document.getElementById('emojiPicker').style.display = 'none';
}

// Element Interaction
function makeElementInteractive(element) {
    element.addEventListener('mousedown', startDrag);
    element.addEventListener('click', selectElement);
    
    // Special handling for text elements
    if (element.classList.contains('text-element')) {
        const textSpan = element.querySelector('span[contenteditable]');
        if (textSpan) {
            textSpan.addEventListener('click', function(e) {
                e.stopPropagation();
                this.focus();
            });
            
            textSpan.addEventListener('mousedown', function(e) {
                e.stopPropagation();
            });
            
            textSpan.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.blur();
                }
            });
        }
    }
}

// Drag and Drop
function startDrag(e) {
    if (e.target.classList.contains('delete-btn')) return;
    if (e.target.hasAttribute('contenteditable')) return;
    
    isDragging = true;
    selectedElement = e.currentTarget;
    selectElement(e);
    
    const rect = selectedElement.getBoundingClientRect();
    const canvasRect = document.getElementById('designCanvas').getBoundingClientRect();
    
    dragOffset.x = e.clientX - rect.left;
    dragOffset.y = e.clientY - rect.top;
    
    selectedElement.classList.add('dragging');
    
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', stopDrag);
    
    e.preventDefault();
}

function drag(e) {
    if (!isDragging || !selectedElement) return;
    
    const canvasRect = document.getElementById('designCanvas').getBoundingClientRect();
    const x = e.clientX - canvasRect.left - dragOffset.x;
    const y = e.clientY - canvasRect.top - dragOffset.y;
    
    selectedElement.style.left = Math.max(0, Math.min(canvasRect.width - selectedElement.offsetWidth, x)) + 'px';
    selectedElement.style.top = Math.max(0, Math.min(canvasRect.height - selectedElement.offsetHeight, y)) + 'px';
}

function stopDrag() {
    if (selectedElement) {
        selectedElement.classList.remove('dragging');
    }
    isDragging = false;
    document.removeEventListener('mousemove', drag);
    document.removeEventListener('mouseup', stopDrag);
}

// Element Selection
function selectElement(elementOrEvent) {
    let element;
    
    // Check if it's an event or an element
    if (elementOrEvent && elementOrEvent.currentTarget) {
        // It's an event
        if (elementOrEvent.target.classList && elementOrEvent.target.classList.contains('delete-btn')) return;
        if (elementOrEvent.target.hasAttribute && elementOrEvent.target.hasAttribute('contenteditable')) return;
        element = elementOrEvent.currentTarget;
        elementOrEvent.stopPropagation();
    } else {
        // It's an element directly
        element = elementOrEvent;
    }
    
    // Ensure we have a valid element
    if (!element || !element.classList) {
        console.warn('selectElement: Invalid element provided');
        return;
    }
    
    // Remove previous selection
    document.querySelectorAll('.design-element').forEach(el => {
        if (el.classList) {
            el.classList.remove('selected');
        }
    });
    
    // Add selection to current element
    element.classList.add('selected');
    selectedElement = element;
}

function deleteElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.remove();
        selectedElement = null;
    }
}

// UI Controls
function toggleEmojiPicker() {
    const picker = document.getElementById('emojiPicker');
    picker.style.display = picker.style.display === 'none' ? 'block' : 'none';
}

function selectColorPicker(picker) {
    document.querySelectorAll('.color-picker').forEach(cp => {
        cp.classList.remove('selected');
    });
    
    picker.classList.add('selected');
    updateColorIndicator(picker.value);
}

function updateColorIndicator(color) {
    const swatch = document.getElementById('currentColorSwatch');
    const text = document.getElementById('currentColorText');
    
    swatch.style.backgroundColor = color;
    
    const colorNames = {
        '#000000': 'שחור',
        '#ff0000': 'אדום',
        '#00ff00': 'ירוק',
        '#0000ff': 'כחול',
        '#ffff00': 'צהוב',
        '#ff00ff': 'סגול',
        '#00ffff': 'תכלת',
        '#ffffff': 'לבן'
    };
    
    text.textContent = colorNames[color.toLowerCase()] || color.toUpperCase();
}

function changeColor(color) {
    updateColorIndicator(color);
    
    if (selectedElement) {
        const textSpan = selectedElement.querySelector('span');
        if (textSpan) {
            textSpan.style.color = color;
        }
    }
}

function changeFontSize(size) {
    document.getElementById('fontSizeValue').textContent = size + 'px';
    if (selectedElement) {
        const textSpan = selectedElement.querySelector('span');
        if (textSpan) {
            textSpan.style.fontSize = size + 'px';
        }
    }
}

// Design Management
function clearCanvas() {
    if (confirm('האם אתה בטוח שאתה רוצה לנקות את כל העיצוב?')) {
        const canvas = document.getElementById('designCanvas');
        const elements = canvas.querySelectorAll('.design-element');
        elements.forEach(el => el.remove());
        selectedElement = null;
    }
}

function saveDesign() {
    const modal = new bootstrap.Modal(document.getElementById('saveModal'));
    modal.show();
}

function confirmSave() {
    const designName = document.getElementById('designName').value || 'עיצוב ללא שם';
    const canvas = document.getElementById('designCanvas');
    const elements = Array.from(canvas.querySelectorAll('.design-element'));
    
    const designData = {
        product: selectedProduct,
        elements: elements.map(el => ({
            id: el.id,
            type: el.classList.contains('text-element') ? 'text' : 'image',
            left: el.style.left,
            top: el.style.top,
            content: el.innerHTML,
            styles: {
                fontSize: el.style.fontSize,
                color: el.style.color
            }
        }))
    };
    
    // Get the save URL from Django template
    const saveUrl = document.querySelector('[data-save-url]')?.dataset.saveUrl || '/save-design/';
    
    fetch(saveUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            name: designName,
            design_data: designData
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('העיצוב נשמר בהצלחה!');
            const modal = bootstrap.Modal.getInstance(document.getElementById('saveModal'));
            modal.hide();
        } else {
            alert('שגיאה בשמירת העיצוב: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('שגיאה בשמירת העיצוב');
    });
}

// AI Design Generation
async function generateAIDesign() {
    console.log('generateAIDesign called');
    
    // Get prompt from textarea
    const promptInput = document.getElementById('promptInput');
    
    let prompt = '';
    if (promptInput && promptInput.value.trim()) {
        prompt = promptInput.value.trim();
    }
    
    const generateBtn = document.getElementById('generateBtn');
    const aiStatus = document.getElementById('aiStatus');
    
    console.log('Prompt:', prompt);
    console.log('Selected product:', selectedProduct);
    
    if (!prompt) {
        alert('אנא הכנס תיאור עיצוב');
        return;
    }
    
    // Check if a product is selected, if not use default
    if (!selectedProduct || !selectedProduct.id) {
        // Try to get first available product from the dropdown
        const firstProduct = document.querySelector('.product-dropdown-item');
        if (firstProduct) {
            selectedProduct = { 
                id: firstProduct.dataset.productId, 
                image: firstProduct.dataset.productImage,
                name: firstProduct.dataset.productName,
                price: firstProduct.dataset.productPrice
            };
            console.log('Using default product:', selectedProduct);
        } else {
            alert('אנא בחר מוצר תחילה');
            return;
        }
    }
    
    // Show loading
    if (generateBtn) {
        generateBtn.disabled = true;
        generateBtn.classList.add('ai-loading');
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>יוצר...';
    }
    if (aiStatus) aiStatus.style.display = 'block';
    
    try {
        // בדוק אם יש תמונת סטייל
        const styleInput = document.getElementById('styleImageInput');
        const hasStyleImage = styleInput && styleInput.files && styleInput.files[0];
        
        let response;
        
        if (hasStyleImage) {
            // שימוש ב-FormData עבור העלאת קבצים
            const formData = new FormData();
            formData.append('prompt', prompt);
            formData.append('product_id', selectedProduct.id);
            formData.append('product_name', selectedProduct.name);
            formData.append('conversation_id', currentConversationId || '');
            formData.append('style_image', styleInput.files[0]);
            
            console.log('Sending with style image:', styleInput.files[0].name);
            
            response = await fetch('/generate-ai-design/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                    // לא כולל Content-Type עבור FormData - הדפדפן יוסיף אותו אוטומטית
                },
                body: formData
            });
        } else {
            // שימוש ב-JSON עבור בקשות רגילות
            console.log('Sending without style image');
            
            response = await fetch('/generate-ai-design/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    prompt: prompt,
                    product_id: selectedProduct.id,
                    product_name: selectedProduct.name,
                    conversation_id: currentConversationId  // הוספת מזהה השיחה
                })
            });
        }
        
        const data = await response.json();
        console.log('Response:', data);
        
        if (data.success) {
            // עדכן את מזהה השיחה
            if (data.conversation_id) {
                currentConversationId = data.conversation_id;
                console.log('Updated conversation ID:', currentConversationId);
            }
            
            // Add the generated image to the canvas
            const canvas = document.getElementById('designCanvas');
            const imageElement = document.createElement('div');
            imageElement.className = 'design-element ai-generated';
            imageElement.id = 'element_' + (++elementCounter);
            imageElement.innerHTML = `
                <img src="${data.image_url}" class="image-element" style="width: 200px; height: 200px; object-fit: contain;">
                <button class="delete-btn" onclick="deleteElement('${imageElement.id}')">&times;</button>
                <button class="edit-image-btn" onclick="editAIImage('${data.image_url}')" title="ערוך תמונה זו">
                    <i class="fas fa-edit"></i>
                </button>
            `;
            imageElement.style.left = '100px';
            imageElement.style.top = '100px';
            
            canvas.appendChild(imageElement);
            makeElementInteractive(imageElement);
            
            // Clear prompt
            if (promptInput) promptInput.value = '';
            
            // Show success message with details
            let message = 'עיצוב נוצר בהצלחה!\n';
            message += `מידות: ${data.dimensions}\n`;
            message += `רזולוציה: ${data.dpi}\n`;
            if (data.max_print_size) {
                message += `מידות הדפסה: ${data.max_print_size}\n`;
            }
            if (data.cmyk_url) {
                message += 'קובץ CMYK להדפסה זמין';
            }
            
            alert(message);
            
            // Optional: Add download links for both files
            if (data.cmyk_url) {
                console.log('PNG file:', data.image_url);
                console.log('CMYK file:', data.cmyk_url);
                
                // You can add download buttons here if needed
                // addDownloadButtons(data.image_url, data.cmyk_url);
            }
        } else {
            alert('שגיאה ביצירת העיצוב: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('שגיאה בחיבור לשרת: ' + error.message);
    } finally {
        // Hide loading
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.classList.remove('ai-loading');
            generateBtn.innerHTML = '<i class="fas fa-magic me-1"></i>צור';
        }
        if (aiStatus) aiStatus.style.display = 'none';
    }
}

// Utility Functions
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

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('Custom Design Page loaded');
    
    // Initialize color indicator
    updateColorIndicator('#000000');
    
    // Auto-select product if one is already selected
    const selectedProduct = document.querySelector('.product-option.selected');
    if (selectedProduct) {
        selectProduct(selectedProduct);
    }
    
    // Canvas click handling
    const canvas = document.getElementById('designCanvas');
    if (canvas) {
        canvas.addEventListener('click', function(e) {
            if (e.target === this) {
                document.querySelectorAll('.design-element').forEach(el => {
                    el.classList.remove('selected');
                });
                selectedElement = null;
            }
        });
    }
    
    // Hide emoji picker when clicking elsewhere
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.emoji-picker') && !e.target.closest('button')) {
            const picker = document.getElementById('emojiPicker');
            if (picker) {
                picker.style.display = 'none';
            }
        }
    });
    
    // Debug AI section
    const aiSection = document.querySelector('.ai-design-section');
    const aiTextarea = document.getElementById('aiDesignPrompt');
    const aiButton = document.getElementById('generateBtn');
    
    if (aiSection) {
        console.log('AI section found');
    } else {
        console.log('AI section NOT found');
    }
    
    if (aiTextarea) {
        console.log('AI textarea found');
    } else {
        console.log('AI textarea NOT found');
    }
    
    if (aiButton) {
        console.log('AI button found');
    } else {
        console.log('AI button NOT found');
    }
    
    // Tool initialization - Show tool options bar by default
    const toolOptionsBar = document.getElementById('toolOptionsBar');
    if (toolOptionsBar) {
        toolOptionsBar.style.display = 'block';
    }
    
    // Initialize AI tool as active
    const aiToolButton = document.querySelector('[data-tool="ai"]');
    if (aiToolButton) {
        selectTool(aiToolButton, 'ai');
    }
    
    // Update font size display
    const fontSizeSlider = document.getElementById('fontSize');
    const fontSizeValue = document.getElementById('fontSizeValue');
    if (fontSizeSlider && fontSizeValue) {
        fontSizeSlider.addEventListener('input', function() {
            fontSizeValue.textContent = this.value;
        });
    }
});

// פונקציות לטיפול בתמונת הסטייל
function handleStyleImageUpload(input) {
    const file = input.files[0];
    if (!file) return;
    
    // בדיקה שזה תמונה
    if (!file.type.startsWith('image/')) {
        alert('אנא העלה קובץ תמונה בלבד');
        input.value = '';
        return;
    }
    
    // בדיקת גודל קובץ (מקסימום 10MB)
    if (file.size > 10 * 1024 * 1024) {
        alert('גודל הקובץ גדול מדי. אנא העלה תמונה קטנה מ-10MB');
        input.value = '';
        return;
    }
    
    // הצגת תצוגה מקדימה
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.getElementById('styleImagePreview');
        const previewImg = document.getElementById('styleImagePreviewImg');
        
        previewImg.src = e.target.result;
        preview.style.display = 'block';
    };
    reader.readAsDataURL(file);
    
    console.log('Style image uploaded:', file.name, file.size, 'bytes');
}

function removeStyleImage() {
    const input = document.getElementById('styleImageInput');
    const preview = document.getElementById('styleImagePreview');
    
    input.value = '';
    preview.style.display = 'none';
    
    console.log('Style image removed');
}

// פונקציה לעריכת תמונת AI - פותחת חלון דו-שיח לעריכה
function editAIImage(imageUrl) {
    console.log('Edit AI Image called with URL:', imageUrl);
    
    // יצירת חלון דו-שיח קטן לבקשת עריכה
    const prompt = window.prompt(
        'כתוב מה תרצה לשנות בתמונה הזו:\n(לדוגמה: "תעשה את הבננה הזאת אדומה במקום צהובה")',
        ''
    );
    
    if (!prompt || prompt.trim() === '') {
        console.log('Edit cancelled or empty prompt');
        return;
    }
    
    // בדיקה שיש מוצר נבחר
    if (!selectedProduct) {
        alert('אנא בחר מוצר לעיצוב');
        return;
    }
    
    console.log('Starting image edit with prompt:', prompt);
    console.log('Base image URL:', imageUrl);
    
    // קריאה לפונקציה שתשלח בקשה לשרת עם התמונה כבסיס
    generateAIImageEdit(prompt, imageUrl);
}

// פונקציה לשליחת בקשת עריכת תמונה לשרת
async function generateAIImageEdit(prompt, baseImageUrl) {
    console.log('generateAIImageEdit called');
    console.log('Prompt:', prompt);
    console.log('Base image URL:', baseImageUrl);
    
    const generateBtn = document.getElementById('generateBtn');
    const aiStatus = document.getElementById('aiStatus');
    
    // Show loading
    if (generateBtn) {
        generateBtn.disabled = true;
        generateBtn.classList.add('ai-loading');
    }
    if (aiStatus) aiStatus.style.display = 'block';
    
    try {
        console.log('Sending image edit request');
        
        const response = await fetch('/generate-ai-design/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                prompt: prompt,
                product_id: selectedProduct.id,
                product_name: selectedProduct.name,
                conversation_id: currentConversationId,
                base_image_url: baseImageUrl  // התמונה לעריכה
            })
        });
        
        const data = await response.json();
        console.log('Edit response:', data);
        
        if (data.success) {
            // עדכן את מזהה השיחה
            if (data.conversation_id) {
                currentConversationId = data.conversation_id;
            }
            
            // Add the edited image to the canvas
            const canvas = document.getElementById('designCanvas');
            const imageElement = document.createElement('div');
            imageElement.className = 'design-element ai-generated ai-edited';
            imageElement.id = 'element_' + (++elementCounter);
            imageElement.innerHTML = `
                <img src="${data.image_url}" class="image-element" style="width: 200px; height: 200px; object-fit: contain;">
                <button class="delete-btn" onclick="deleteElement('${imageElement.id}')">&times;</button>
                <button class="edit-image-btn" onclick="editAIImage('${data.image_url}')" title="ערוך תמונה זו">
                    <i class="fas fa-edit"></i>
                </button>
            `;
            imageElement.style.left = '120px'; // מקום מעט שונה מהמקור
            imageElement.style.top = '120px';
            
            canvas.appendChild(imageElement);
            
            // Make it draggable
            makeElementInteractive(imageElement);
            
            // Clear prompts
            const promptInput = document.getElementById('promptInput');
            if (promptInput) promptInput.value = '';
            
            // הצגת הודעת הצלחה
            alert(`✅ התמונה נערכה בהצלחה!\n🎨 סוג AI: ${data.ai_service || 'לא ידוע'}\n📐 רזולוציה: ${data.dimensions || 'לא ידועה'}`);
            
        } else {
            alert('שגיאה ביצירת העיצוב: ' + (data.error || 'שגיאה לא ידועה'));
        }
        
    } catch (error) {
        console.error('Error editing AI image:', error);
        alert('שגיאה בתקשורת עם השרת: ' + error.message);
    } finally {
        // Hide loading
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.classList.remove('ai-loading');
        }
        if (aiStatus) aiStatus.style.display = 'none';
    }
}

// Helper function to close dropdowns manually
function closeDropdownManually() {
    // Close all Bootstrap dropdowns
    const dropdowns = document.querySelectorAll('.dropdown-menu.show');
    dropdowns.forEach(dropdown => {
        dropdown.classList.remove('show');
    });
    
    // Remove aria attributes that Bootstrap sets
    const toggleButtons = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    toggleButtons.forEach(button => {
        button.setAttribute('aria-expanded', 'false');
    });
}

// ========== FREEPIK IMAGE SEARCH FUNCTIONS ==========

/**
 * Clear all filters and show all results
 */
function clearAllFilters() {
    // Uncheck all filter checkboxes
    document.getElementById('transparentOnlyFilter').checked = false;
    document.getElementById('vectorOnlyFilter').checked = false;
    
    // Reset filter variables
    transparentFilter = false;
    vectorFilter = false;
    
    // Show all results if we have any
    if (lastSearchResults.length > 0) {
        displayFreepikResults(lastSearchResults);
        
        // Update source indicator
        const sourceIndicator = document.getElementById('imageSourceIndicator');
        const sourceBadge = sourceIndicator.querySelector('.badge');
        sourceBadge.textContent = `מקור: כל התמונות (${lastSearchResults.length})`;
        
        console.log('🔄 Filters cleared - showing all results');
    }
}

/**
 * Sort results by transparency score (highest first)
 */
function sortByTransparency() {
    if (!lastSearchResults || lastSearchResults.length === 0) {
        alert('אין תוצאות למיון. חפש תמונות תחילה.');
        return;
    }
    
    // Sort by transparency score (descending)
    const sortedResults = [...lastSearchResults].sort((a, b) => {
        const scoreA = a.transparency_score || 0;
        const scoreB = b.transparency_score || 0;
        return scoreB - scoreA;
    });
    
    displayFreepikResults(sortedResults);
    
    // Update source indicator
    const sourceIndicator = document.getElementById('imageSourceIndicator');
    const sourceBadge = sourceIndicator.querySelector('.badge');
    sourceBadge.textContent = `ממוין לפי שקיפות: ${sortedResults.length} תמונות`;
    
    console.log('📊 Results sorted by transparency score');
    
    // Show sorting notification
    showFilterToast(sortedResults.length, lastSearchResults.length, ' [ממוין לפי שקיפות]');
}

/**
 * Toggle transparent background filter
 */
function toggleTransparentFilter() {
    const checkbox = document.getElementById('transparentOnlyFilter');
    transparentFilter = checkbox.checked;
    console.log('🔍 Transparent filter:', transparentFilter);
    
    if (lastSearchResults.length > 0) {
        applyFiltersToResults();
    }
}

/**
 * Toggle vector images filter
 */
function toggleVectorFilter() {
    const checkbox = document.getElementById('vectorOnlyFilter');
    vectorFilter = checkbox.checked;
    console.log('🔍 Vector filter:', vectorFilter);
    
    if (lastSearchResults.length > 0) {
        applyFiltersToResults();
    }
}

/**
 * Apply filters to current search results
 */
function applyFiltersToResults() {
    if (!lastSearchResults || lastSearchResults.length === 0) {
        return;
    }
    
    let filteredResults = [...lastSearchResults];
    
    // Apply transparent filter
    if (transparentFilter) {
        filteredResults = filteredResults.filter(image => {
            return isLikelyTransparent(image);
        });
    }
    
    // Apply vector filter  
    if (vectorFilter) {
        filteredResults = filteredResults.filter(image => {
            return isLikelyVector(image);
        });
    }
    
    console.log(`🔍 Filtered results: ${filteredResults.length}/${lastSearchResults.length} images`);
    displayFreepikResults(filteredResults);
    
    // Update source indicator with filter info
    const sourceIndicator = document.getElementById('imageSourceIndicator');
    const sourceBadge = sourceIndicator.querySelector('.badge');
    let filterText = '';
    if (transparentFilter) filterText += ' [רקע שקוף]';
    if (vectorFilter) filterText += ' [וקטור]';
    sourceBadge.textContent = `מסונן: ${filteredResults.length} תמונות${filterText}`;
    
    // Show toast notification if significant filtering occurred
    const filterRatio = filteredResults.length / lastSearchResults.length;
    if (filterRatio < 0.8 && lastSearchResults.length > 5) {
        showFilterToast(filteredResults.length, lastSearchResults.length, filterText);
    }
}

/**
 * Check if image is likely to have transparent background or easy to remove
 */
function isLikelyTransparent(image) {
    const title = (image.title || '').toLowerCase();
    const tags = (image.tags || []).join(' ').toLowerCase();
    const text = (title + ' ' + tags).toLowerCase();
    
    // Keywords that suggest transparent background or easy removal
    const transparentKeywords = [
        'transparent', 'png', 'cutout', 'isolated', 'white background',
        'no background', 'transparent background', 'cut out', 'isolated on white',
        'logo', 'icon', 'vector', 'svg', 'clip art', 'clipart',
        'silhouette', 'outline', 'symbol', 'badge', 'sticker',
        'graphic', 'design element', 'illustration',
        // Hebrew keywords
        'לוגו', 'איקון', 'סמל', 'מדבקה', 'איור', 'גרפיקה'
    ];
    
    // Check if any transparent keywords are present
    const hasTransparentKeywords = transparentKeywords.some(keyword => 
        text.includes(keyword)
    );
    
    // Check file type (if available in URL)
    const url = image.thumbnail || image.preview || '';
    const isPng = url.toLowerCase().includes('.png');
    const isSvg = url.toLowerCase().includes('.svg');
    
    // Check if it's from a source that typically has transparent images
    const isVectorSource = image.type === 'freepik' && (
        text.includes('vector') || 
        text.includes('illustration') ||
        text.includes('graphic')
    );
    
    return hasTransparentKeywords || isPng || isSvg || isVectorSource;
}

/**
 * Check if image is likely to be vector-based
 */
function isLikelyVector(image) {
    const title = (image.title || '').toLowerCase();
    const tags = (image.tags || []).join(' ').toLowerCase();
    const text = (title + ' ' + tags).toLowerCase();
    const url = image.thumbnail || image.preview || '';
    
    // Vector keywords
    const vectorKeywords = [
        'vector', 'svg', 'illustration', 'graphic', 'logo', 'icon',
        'clip art', 'clipart', 'design', 'symbol', 'badge',
        'flat design', 'minimal', 'simple', 'geometric',
        // Hebrew keywords
        'וקטור', 'איור', 'לוגו', 'איקון', 'סמל', 'עיצוב'
    ];
    
    // Check keywords
    const hasVectorKeywords = vectorKeywords.some(keyword => 
        text.includes(keyword)
    );
    
    // Check file type
    const isSvg = url.toLowerCase().includes('.svg');
    const isPng = url.toLowerCase().includes('.png'); // PNGs are often used for vector-style graphics
    
    return hasVectorKeywords || isSvg || (isPng && hasVectorKeywords);
}

/**
 * Show filter notification toast
 */
function showFilterToast(filteredCount, totalCount, filterText) {
    // Create toast element if it doesn't exist
    let toastContainer = document.getElementById('filterToastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'filterToastContainer';
        toastContainer.className = 'position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast HTML
    const toastId = 'filterToast_' + Date.now();
    const toastHTML = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="fas fa-filter text-primary me-2"></i>
                <strong class="me-auto">סינון תמונות</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                <i class="fas fa-check-circle text-success me-2"></i>
                נמצאו <strong>${filteredCount}</strong> תמונות מתאימות מתוך ${totalCount}
                <br><small class="text-muted">${filterText}</small>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    // Initialize and show toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 4000
    });
    
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

/**
 * Handle Enter key press in Freepik search input
 */
function handleFreepikSearchKeypress(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        searchFreepikImages();
    }
}

/**
 * Quick search with predefined terms optimized for transparent images
 */
function quickSearch(searchTerm) {
    const searchInput = document.getElementById('freepikSearchInput');
    searchInput.value = searchTerm;
    
    // Automatically enable transparent filter for transparent-optimized searches
    const transparentFilter = document.getElementById('transparentOnlyFilter');
    if (searchTerm.includes('transparent') || searchTerm.includes('cutout') || 
        searchTerm.includes('isolated') || searchTerm.includes('logo') ||
        searchTerm.includes('icon') || searchTerm.includes('vector')) {
        transparentFilter.checked = true;
        toggleTransparentFilter();
    }
    
    // Auto-enable vector filter for vector searches
    const vectorFilterCheckbox = document.getElementById('vectorOnlyFilter');
    if (searchTerm.includes('vector') || searchTerm.includes('icon') || 
        searchTerm.includes('logo') || searchTerm.includes('symbol')) {
        vectorFilterCheckbox.checked = true;
        toggleVectorFilter();
    }
    
    // Perform the search
    searchFreepikImages();
    
    console.log('🚀 Quick search triggered:', searchTerm);
}

/**
 * Search for images in Freepik database
 */
function searchFreepikImages() {
    const searchInput = document.getElementById('freepikSearchInput');
    const searchQuery = searchInput.value.trim();
    
    if (!searchQuery) {
        alert('אנא הזן מילת חיפוש');
        return;
    }
    
    console.log('🔍 Starting Freepik search for:', searchQuery);
    
    // Show loading state
    const searchBtn = document.getElementById('freepikSearchBtn');
    const searchStatus = document.getElementById('freepikSearchStatus');
    const resultsContainer = document.getElementById('freepikResults');
    const searchResultsArea = document.getElementById('searchResultsArea');
    
    // Make sure search results area is visible
    if (searchResultsArea) {
        searchResultsArea.style.display = 'block';
        console.log('searchResultsArea made visible before search');
    } else {
        console.log('searchResultsArea not found!');
    }
    
    searchBtn.disabled = true;
    searchStatus.style.display = 'block';
    resultsContainer.style.display = 'none';
    
    // Make API request to search Freepik
    fetch('/search-freepik-images/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            query: searchQuery
        })
    })
    .then(response => response.json())
    .then(data => {
        searchBtn.disabled = false;
        searchStatus.style.display = 'none';
        
        if (data.success && data.results && data.results.length > 0) {
            // Save results for filtering
            lastSearchResults = data.results;
            
            // Apply filters if any are active
            if (transparentFilter || vectorFilter) {
                applyFiltersToResults();
            } else {
                displayFreepikResults(data.results);
            }
            
            // Show source indicator with statistics
            const sourceIndicator = document.getElementById('imageSourceIndicator');
            const sourceBadge = sourceIndicator.querySelector('.badge');
            
            // Calculate statistics
            const transparentCount = data.results.filter(img => img.is_likely_transparent).length;
            const vectorCount = data.results.filter(img => img.is_likely_vector).length;
            
            let statsText = `מקור: ${data.source || 'תמונות Stock'} (${data.results.length} תמונות`;
            if (transparentCount > 0) statsText += `, ${transparentCount} שקופות`;
            if (vectorCount > 0) statsText += `, ${vectorCount} וקטור`;
            statsText += ')';
            
            sourceBadge.textContent = statsText;
            sourceIndicator.style.display = 'block';
            
            console.log(`✅ Found ${data.results.length} images from ${data.source || 'Stock'}`);
            console.log(`📊 Stats: ${transparentCount} transparent, ${vectorCount} vector`);
        } else {
            lastSearchResults = []; // Reset results
            resultsContainer.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-info text-center">
                        <i class="fas fa-search me-2"></i>
                        לא נמצאו תוצאות עבור "${searchQuery}"<br>
                        נסה מילות חיפוש אחרות
                    </div>
                </div>
            `;
            resultsContainer.style.display = 'block';
        }
    })
    .catch(error => {
        console.error('❌ Freepik search error:', error);
        searchBtn.disabled = false;
        searchStatus.style.display = 'none';
        
        resultsContainer.innerHTML = `
            <div class="col-12">
                <div class="alert alert-danger text-center">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    שגיאה בחיפוש תמונות<br>
                    ${error.message || 'נסה שוב מאוחר יותר'}
                </div>
            </div>
        `;
        resultsContainer.style.display = 'block';
    });
}

/**
 * Display Freepik search results
 */
function displayFreepikResults(results) {
    const resultsContainer = document.getElementById('freepikResults');
    const searchResultsArea = document.getElementById('searchResultsArea');
    
    let html = '';
    results.forEach(image => {
        // Create indicator badges based on image properties
        let badges = '';
        if (image.is_likely_transparent) {
            badges += `<span class="badge bg-success position-absolute top-0 start-0 m-1" style="font-size: 0.7em;" title="רקע שקוף/קל להסרה">
                <i class="fas fa-magic"></i>
            </span>`;
        }
        if (image.is_likely_vector) {
            badges += `<span class="badge bg-primary position-absolute top-0 end-0 m-1" style="font-size: 0.7em;" title="תמונה וקטורית">
                <i class="fas fa-vector-square"></i>
            </span>`;
        }
        
        // Add transparency score as a subtle indicator
        let transparencyIndicator = '';
        if (image.transparency_score && image.transparency_score > 30) {
            const opacity = Math.min(image.transparency_score / 100, 0.8);
            transparencyIndicator = `style="border: 2px solid rgba(40, 167, 69, ${opacity});"`;
        }
        
        html += `
            <div class="col-6 col-md-4">
                <div class="freepik-result-item position-relative" onclick="selectFreepikImage('${image.id}', '${image.preview}', '${image.title}')">
                    ${badges}
                    <img src="${image.thumbnail || image.preview}" 
                         alt="${image.title}" 
                         class="img-fluid rounded"
                         ${transparencyIndicator}
                         style="width: 100%; height: 80px; object-fit: cover; cursor: pointer;">
                    <div class="text-center mt-1">
                        <small class="text-muted" title="${image.title}">${image.title.length > 30 ? image.title.substring(0, 30) + '...' : image.title}</small>
                    </div>
                </div>
            </div>
        `;
    });
    
    resultsContainer.innerHTML = html;
    resultsContainer.style.display = 'block';
    
    // Make sure the search results area is visible
    if (searchResultsArea) {
        searchResultsArea.style.display = 'block';
        console.log('searchResultsArea made visible after displaying results');
    } else {
        console.log('searchResultsArea not found in displayFreepikResults!');
    }
}

/**
 * Select and download a Freepik image
 */
function selectFreepikImage(imageId, imageUrl, imageTitle) {
    if (!selectedProduct) {
        showNoProductMessage();
        return;
    }
    
    console.log('📥 Selecting image:', imageId, imageTitle);
    
    // Show loading state
    const resultsContainer = document.getElementById('freepikResults');
    resultsContainer.style.opacity = '0.5';
    
    // Download and add image to canvas
    fetch('/download-freepik-image/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            image_id: imageId,
            image_url: imageUrl,
            image_title: imageTitle
        })
    })
    .then(response => response.json())
    .then(data => {
        resultsContainer.style.opacity = '1';
        
        if (data.success && data.image_url) {
            // Add the downloaded image to canvas
            addFreepikImageToCanvas(data.image_url, data.title || imageTitle);
            console.log('✅ Image added to canvas');
            
            // Hide results after selection
            resultsContainer.style.display = 'none';
            document.getElementById('imageSourceIndicator').style.display = 'none';
            document.getElementById('freepikSearchInput').value = '';
        } else {
            alert('שגיאה בהורדת התמונה: ' + (data.error || 'נסה שוב'));
        }
    })
    .catch(error => {
        console.error('❌ Download error:', error);
        resultsContainer.style.opacity = '1';
        alert('שגיאה בהורדת התמונה: ' + error.message);
    });
}

/**
 * Add Freepik image to canvas
 */
function addFreepikImageToCanvas(imageUrl, imageTitle) {
    try {
        const canvas = document.getElementById('designCanvas');
        
        if (!canvas) {
            console.error('Design canvas not found');
            return;
        }
        
        // Create new image element
        const imageElement = document.createElement('div');
        elementCounter++;
        imageElement.id = 'element_' + elementCounter;
        imageElement.className = 'design-element image-element';
        imageElement.setAttribute('data-element-type', 'freepik-image');
        imageElement.setAttribute('data-image-title', imageTitle || 'Stock Image');
        
        // Position the image (center of canvas)
        const canvasRect = canvas.getBoundingClientRect();
        const centerX = canvasRect.width / 2 - 50;
        const centerY = canvasRect.height / 2 - 50;
        
        imageElement.style.position = 'absolute';
        imageElement.style.left = centerX + 'px';
        imageElement.style.top = centerY + 'px';
        imageElement.style.width = '100px';
        imageElement.style.height = '100px';
        imageElement.style.cursor = 'move';
        imageElement.style.border = '2px dashed transparent';
        imageElement.style.borderRadius = '8px';
        imageElement.style.overflow = 'hidden';
        imageElement.style.zIndex = '10';
        
        // Create image tag
        const img = document.createElement('img');
        img.src = imageUrl;
        img.alt = imageTitle || 'Stock Image';
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'cover';
        img.style.borderRadius = '6px';
        
        // Handle image load errors
        img.onerror = function() {
            console.error('Failed to load image:', imageUrl);
            imageElement.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #f0f0f0; font-size: 12px; color: #666;">
                    <i class="fas fa-image"></i>
                </div>
            `;
        };
        
        imageElement.appendChild(img);
        
        // Add drag functionality
        imageElement.addEventListener('mousedown', startDrag);
        
        // Add click selection
        imageElement.addEventListener('click', function(e) {
            e.stopPropagation();
            selectElement(imageElement);
        });
        
        // Add to canvas
        canvas.appendChild(imageElement);
        
        // Select the new element
        selectElement(imageElement);
        
        console.log(`✅ Added stock image "${imageTitle}" to canvas`);
        
    } catch (error) {
        console.error('Error adding image to canvas:', error);
        alert('שגיאה בהוספת התמונה לעיצוב');
    }
}

// Tool Selection Functions for New Interface
function selectTool(button, toolType) {
    console.log('Tool selected:', toolType);
    
    // Remove active class from all tool buttons
    document.querySelectorAll('.tool-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Add active class to clicked button
    button.classList.add('active');
    
    // Hide all tool options
    document.querySelectorAll('.tool-options').forEach(option => {
        option.classList.remove('active');
    });
    
    // Show the selected tool options
    const selectedOptions = document.getElementById(toolType + '-options');
    if (selectedOptions) {
        selectedOptions.classList.add('active');
        document.getElementById('toolOptionsBar').style.display = 'block';
    } else {
        document.getElementById('toolOptionsBar').style.display = 'none';
    }
    
    // Show search results area for images tool
    const searchResultsArea = document.getElementById('searchResultsArea');
    console.log('selectTool called for:', toolType, 'searchResultsArea found:', !!searchResultsArea);
    
    if (toolType === 'images') {
        if (searchResultsArea) {
            searchResultsArea.style.display = 'block';
            console.log('searchResultsArea displayed for images tool');
        }
    } else {
        if (searchResultsArea) {
            searchResultsArea.style.display = 'none';
            console.log('searchResultsArea hidden for non-images tool');
        }
    }
}

// Zoom Functions
function zoomIn() {
    const canvas = document.getElementById('designCanvas');
    if (canvas) {
        const currentScale = parseFloat(canvas.style.transform.replace('scale(', '').replace(')', '') || '1');
        const newScale = Math.min(currentScale * 1.2, 3); // Maximum 300%
        canvas.style.transform = `scale(${newScale})`;
        canvas.style.transformOrigin = 'center center';
        
        // Update zoom level display
        const zoomLevel = document.querySelector('.zoom-level');
        if (zoomLevel) {
            zoomLevel.textContent = `${Math.round(newScale * 100)}%`;
        }
    }
}

function zoomOut() {
    const canvas = document.getElementById('designCanvas');
    if (canvas) {
        const currentScale = parseFloat(canvas.style.transform.replace('scale(', '').replace(')', '') || '1');
        const newScale = Math.max(currentScale / 1.2, 0.25); // Minimum 25%
        canvas.style.transform = `scale(${newScale})`;
        canvas.style.transformOrigin = 'center center';
        
        // Update zoom level display
        const zoomLevel = document.querySelector('.zoom-level');
        if (zoomLevel) {
            zoomLevel.textContent = `${Math.round(newScale * 100)}%`;
        }
    }
}

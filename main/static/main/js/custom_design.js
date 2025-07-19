// Custom Design Page JavaScript

// Global variables
let selectedElement = null;
let elementCounter = 0;
let isDragging = false;
let dragOffset = { x: 0, y: 0 };
let selectedProduct = null;
let currentConversationId = null; // מזהה השיחה הנוכחית

// Product Selection
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
function selectElement(e) {
    if (e.target.classList.contains('delete-btn')) return;
    if (e.target.hasAttribute('contenteditable')) return;
    
    // Remove previous selection
    document.querySelectorAll('.design-element').forEach(el => {
        el.classList.remove('selected');
    });
    
    // Add selection to current element
    const element = e.currentTarget;
    element.classList.add('selected');
    selectedElement = element;
    
    e.stopPropagation();
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
    
    // Get prompt from either textarea
    const promptFromSidebar = document.getElementById('aiDesignPrompt');
    const promptFromTop = document.getElementById('aiDesignPromptTop');
    
    let prompt = '';
    if (promptFromSidebar && promptFromSidebar.value.trim()) {
        prompt = promptFromSidebar.value.trim();
    } else if (promptFromTop && promptFromTop.value.trim()) {
        prompt = promptFromTop.value.trim();
    }
    
    const generateBtn = document.getElementById('generateBtn');
    const aiStatus = document.getElementById('aiStatus');
    
    console.log('Prompt:', prompt);
    
    if (!prompt) {
        alert('אנא הכנס תיאור עיצוב');
        return;
    }
    
    if (!selectedProduct) {
        alert('אנא בחר מוצר לעיצוב');
        return;
    }
    
    console.log('Selected product:', selectedProduct);
    
    // Show loading
    if (generateBtn) {
        generateBtn.disabled = true;
        generateBtn.classList.add('ai-loading');
    }
    if (aiStatus) aiStatus.style.display = 'block';
    
    try {
        const response = await fetch('/generate-ai-design/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                prompt: prompt,
                product_id: selectedProduct.id,
                product_name: document.querySelector('.product-option.selected .product-name').textContent,
                conversation_id: currentConversationId  // הוספת מזהה השיחה
            })
        });
        
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
            `;
            imageElement.style.left = '100px';
            imageElement.style.top = '100px';
            
            canvas.appendChild(imageElement);
            makeElementInteractive(imageElement);
            
            // Clear both prompts
            if (promptFromSidebar) promptFromSidebar.value = '';
            if (promptFromTop) promptFromTop.value = '';
            
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
        alert('שגיאה בחיבור לשרת');
    } finally {
        // Hide loading
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.classList.remove('ai-loading');
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
});

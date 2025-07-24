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
    
    // הפעלת כלי העיצוב
    enableDesignTools();
    
    // סגירת ה-dropdown
    setTimeout(closeDropdownManually, 100);
}

// Product Message Functions
function showNoProductMessage() {
    const message = document.getElementById('noProductMessage');
    if (message) {
        message.classList.remove('d-none');
        // Scroll to the message
        message.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function hideNoProductMessage() {
    const message = document.getElementById('noProductMessage');
    if (message) {
        message.classList.add('d-none');
    }
}

// הפעלת כלי העיצוב כאשר נבחר מוצר
function enableDesignTools() {
    console.log('Enabling design tools');
    
    // הסתרת הודעת הכלים המושבתים
    const disabledMessage = document.getElementById('toolsDisabledMessage');
    if (disabledMessage) {
        disabledMessage.classList.add('d-none');
    }
    
    // הפעלת כל כלי העיצוב
    const toolButtons = document.querySelectorAll('.tool-button');
    toolButtons.forEach(button => {
        button.classList.remove('disabled');
        button.removeAttribute('disabled');
    });
    
    // הפעלת כלי AI כברירת מחדל
    const aiTool = document.querySelector('[data-tool="ai"]');
    if (aiTool && !aiTool.classList.contains('active')) {
        selectTool(aiTool, 'ai');
    }
    
    // הצגת סרגל הכלים
    const toolOptionsBar = document.getElementById('toolOptionsBar');
    if (toolOptionsBar) {
        toolOptionsBar.classList.remove('hidden');
    }
}

// השבתת כלי העיצוב כאשר אין מוצר נבחר
function disableDesignTools() {
    console.log('Disabling design tools');
    
    // הצגת הודעת הכלים המושבתים
    const disabledMessage = document.getElementById('toolsDisabledMessage');
    if (disabledMessage) {
        disabledMessage.classList.remove('d-none');
    }
    
    // השבתת כל כלי העיצוב
    const toolButtons = document.querySelectorAll('.tool-button');
    toolButtons.forEach(button => {
        button.classList.add('disabled');
        button.classList.remove('active');
        button.setAttribute('disabled', 'disabled');
    });
    
    // הסתרת סרגל הכלים
    const toolOptionsBar = document.getElementById('toolOptionsBar');
    if (toolOptionsBar) {
        toolOptionsBar.classList.add('hidden');
    }
    
    // ניקוי הכלי הנוכחי
    const toolOptions = document.querySelectorAll('.tool-options');
    toolOptions.forEach(option => {
        option.classList.remove('active');
    });
}

function updateCanvasBackground(productElement) {
    const canvas = document.getElementById('designCanvas');
    const placeholderText = document.getElementById('placeholderText');
    const productImage = productElement.dataset.productImage;
    
    if (productImage && productImage.trim() !== '') {
        canvas.style.backgroundImage = `url('${productImage}')`;
        canvas.classList.add('with-product');
        placeholderText.classList.add('d-none');
    } else {
        // Show placeholder for products without image
        canvas.style.backgroundImage = 'none';
        canvas.classList.remove('with-product');
        placeholderText.classList.remove('d-none');
        placeholderText.innerHTML = `
            <i class="fas fa-tshirt js-placeholder-icon"></i>
            <p>נבחר מוצר: ${productElement.dataset.productName}</p>
            <p class="js-placeholder-text">התחל לעצב על המוצר</p>
        `;
    }
    
    // Update print dimensions display
    const printDimensionsDiv = document.getElementById('printDimensions');
    const printDimensionsText = document.getElementById('printDimensionsText');
    const printSize = productElement.dataset.productPrintSize;
    
    if (printSize) {
        printDimensionsText.textContent = printSize;
        printDimensionsDiv.classList.add('d-block');
        printDimensionsDiv.classList.remove('d-none');
    } else {
        printDimensionsDiv.classList.add('d-none');
        printDimensionsDiv.classList.remove('d-block');
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
        placeholderText.classList.add('d-none');
    } else {
        // Show placeholder for products without image
        canvas.style.backgroundImage = 'none';
        canvas.classList.remove('with-product');
        placeholderText.classList.remove('d-none');
        placeholderText.innerHTML = `
            <i class="fas fa-tshirt js-placeholder-icon"></i>
            <p>נבחר מוצר: ${productElement.querySelector('.product-name').textContent}</p>
            <p class="js-placeholder-text">התחל לעצב על המוצר</p>
        `;
    }
    
    // Update print dimensions display
    const printDimensionsDiv = document.getElementById('printDimensions');
    const printDimensionsText = document.getElementById('printDimensionsText');
    
    if (printDimensions) {
        printDimensionsText.textContent = printDimensions;
        printDimensionsDiv.classList.add('d-block');
        printDimensionsDiv.classList.remove('d-none');
    } else {
        printDimensionsDiv.classList.add('d-none');
        printDimensionsDiv.classList.remove('d-block');
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
    
    // Get text from input field
    const textInput = document.getElementById('textInput');
    let textContent = 'טקסט חדש'; // default text
    if (textInput && textInput.value.trim()) {
        textContent = textInput.value.trim();
        textInput.value = ''; // Clear input after use
    }
    
    // Get current font size from slider
    const fontSizeSlider = document.getElementById('fontSize');
    const fontSize = fontSizeSlider ? fontSizeSlider.value + 'px' : '24px';
    
    const canvas = document.getElementById('designCanvas');
    const textElement = document.createElement('div');
    textElement.className = 'design-element text-element';
    textElement.id = 'element_' + (++elementCounter);
    textElement.innerHTML = `
        <span contenteditable="true" class="js-text-editable">${textContent}</span>
        <button class="delete-btn" onclick="deleteElement('${textElement.id}')">&times;</button>
    `;
    textElement.style.left = '50px';
    textElement.style.top = '50px';
    textElement.style.fontSize = fontSize;
    
    // Get current color from color picker and apply to the span
    const colorPicker = document.getElementById('textColor');
    const currentColor = colorPicker ? colorPicker.value : '#000000';
    
    // Get current font family from selector
    const fontFamilySelector = document.getElementById('fontFamily');
    const currentFontFamily = fontFamilySelector ? fontFamilySelector.value : 'Arial';
    
    // Check if bold is active
    const boldBtn = document.getElementById('boldBtn');
    const isBold = boldBtn && boldBtn.classList.contains('active');
    const fontWeight = isBold ? '700' : '400';
    
    // Check if arch is active
    const archBtn = document.getElementById('archBtn');
    const isArched = archBtn && archBtn.classList.contains('active');
    const archValue = isArched ? document.getElementById('archCurve').value : 0;
    
    canvas.appendChild(textElement);
    
    // Apply color, font, and effects to the span element (not the container)
    const textSpan = textElement.querySelector('span[contenteditable]');
    if (textSpan) {
        textSpan.style.color = currentColor;
        textSpan.style.fontSize = fontSize;
        textSpan.style.fontFamily = currentFontFamily;
        textSpan.style.fontWeight = fontWeight;
        
        if (isArched) {
            textSpan.classList.add('text-arch');
            const curvature = parseFloat(archValue) || 0;
            createSimpleArchEffect(textSpan, curvature);
        }
    }
    
    makeElementInteractive(textElement);
    
    // Select the new element to make it active
    selectElement(textElement);
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
                <img src="${e.target.result}" class="image-element js-image-small">
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
        <span class="js-emoji-large">${emoji}</span>
        <button class="delete-btn" onclick="deleteElement('${emojiElement.id}')">&times;</button>
    `;
    emojiElement.style.left = '150px';
    emojiElement.style.top = '150px';
    
    canvas.appendChild(emojiElement);
    makeElementInteractive(emojiElement);
    
    // Hide emoji picker
    document.getElementById('emojiPicker').classList.add('hidden');
}

// Toggle emoji picker
function toggleEmojiPicker() {
    const emojiPicker = document.getElementById('emojiPicker');
    emojiPicker.classList.toggle('hidden');
}

// Element Interaction
function makeElementInteractive(element) {
    element.addEventListener('mousedown', startDrag);
    element.addEventListener('click', function(e) {
        console.log('Element clicked, calling selectElement');
        selectElement(e);
        // If it's a text element, also update UI controls
        if (element.classList.contains('text-element')) {
            updateUIControlsFromElement(element);
        }
    });
    
    // Special handling for text elements
    if (element.classList.contains('text-element')) {
        const textSpan = element.querySelector('span[contenteditable]');
        if (textSpan) {
            // Handle clicks on the text span itself
            textSpan.addEventListener('click', function(e) {
                e.stopPropagation();
                console.log('Text span clicked');
                selectElement(element); // Select parent element
                this.focus(); // Focus on text for editing
                updateUIControlsFromElement(element); // Update controls immediately
            });
            
            textSpan.addEventListener('mousedown', function(e) {
                e.stopPropagation();
            });
            
            // Handle when text gets focus (for editing)
            textSpan.addEventListener('focus', function(e) {
                console.log('Text focused for editing');
                selectElement(element); // Make sure parent is selected
                updateUIControlsFromElement(element); // Update color picker and font size
            });
            
            // Handle text selection within the span
            textSpan.addEventListener('mouseup', function(e) {
                setTimeout(() => {
                    const selection = window.getSelection();
                    if (selection.toString().length > 0) {
                        console.log('Text selected:', selection.toString());
                        selectElement(element);
                        updateUIControlsFromElement(element);
                    }
                }, 10);
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
    
    // Update UI controls if it's a text element
    updateUIControlsFromElement(element);
}

function deleteElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.remove();
        selectedElement = null;
    }
}

// UI Controls

// Function to update UI controls based on selected element
function updateUIControlsFromElement(element) {
    if (!element || !element.classList.contains('text-element')) {
        return;
    }
    
    const textSpan = element.querySelector('span[contenteditable]');
    if (!textSpan) {
        return;
    }
    
    console.log('Updating UI controls from element');
    
    // Update color picker to match selected text color
    const currentColor = window.getComputedStyle(textSpan).color;
    const colorPicker = document.getElementById('textColor');
    if (colorPicker && currentColor) {
        // Convert RGB to hex if needed
        const hexColor = rgbToHex(currentColor);
        if (hexColor) {
            console.log('Setting color picker to:', hexColor);
            colorPicker.value = hexColor;
            updateColorIndicator(hexColor);
        }
    }
    
    // Update font size slider to match selected text size
    let currentFontSize;
    
    // Check if arch is active and use original font size
    if (textSpan.classList.contains('text-arch') && textSpan.originalFontSize) {
        currentFontSize = textSpan.originalFontSize;
        console.log('Using stored original font size for arch text:', currentFontSize);
    } else {
        currentFontSize = window.getComputedStyle(textSpan).fontSize;
        console.log('Using computed font size:', currentFontSize);
    }
    
    const fontSizeSlider = document.getElementById('fontSize');
    const fontSizeValue = document.getElementById('fontSizeValue');
    if (fontSizeSlider && fontSizeValue && currentFontSize) {
        const fontSize = parseInt(currentFontSize);
        console.log('Setting font size to:', fontSize);
        fontSizeSlider.value = fontSize;
        fontSizeValue.textContent = fontSize + 'px';
    }
    
    // Update font family selector to match selected text font
    const currentFontFamily = window.getComputedStyle(textSpan).fontFamily;
    const fontFamilySelector = document.getElementById('fontFamily');
    if (fontFamilySelector && currentFontFamily) {
        console.log('Current font family:', currentFontFamily);
        // Remove quotes and normalize font family name
        const normalizedFontFamily = currentFontFamily.replace(/['"]/g, '').split(',')[0].trim();
        console.log('Normalized font family:', normalizedFontFamily);
        
        // Try to match with available options
        const options = fontFamilySelector.querySelectorAll('option');
        for (let option of options) {
            if (option.value === normalizedFontFamily || option.value.includes(normalizedFontFamily)) {
                console.log('Setting font family selector to:', option.value);
                fontFamilySelector.value = option.value;
                // Update font preview
                fontFamilySelector.setAttribute('data-current-font', option.value);
                fontFamilySelector.style.fontFamily = option.value;
                break;
            }
        }
    }
    
    // Update bold button state
    const boldBtn = document.getElementById('boldBtn');
    if (boldBtn) {
        const currentWeight = window.getComputedStyle(textSpan).fontWeight;
        const isBold = currentWeight === 'bold' || currentWeight === '700' || parseInt(currentWeight) >= 700;
        if (isBold) {
            boldBtn.classList.add('active');
        } else {
            boldBtn.classList.remove('active');
        }
    }
    
    // Update arch button and controls state
    const archBtn = document.getElementById('archBtn');
    const archSlider = document.getElementById('archCurve');
    const archControls = document.querySelector('.arch-controls');
    if (archBtn && textSpan.classList.contains('text-arch')) {
        archBtn.classList.add('active');
        archSlider.style.display = 'block';
        archControls.style.display = 'block';
        
        // Get current arch angle
        const currentTransform = textSpan.style.getPropertyValue('--arch-angle');
        if (currentTransform) {
            const angle = parseFloat(currentTransform);
            archSlider.value = angle || 0;
            document.getElementById('archCurveValue').textContent = angle || '0';
        }
    } else if (archBtn) {
        archBtn.classList.remove('active');
        archSlider.style.display = 'none';
        archControls.style.display = 'none';
    }
}

// Helper function to convert RGB to HEX
function rgbToHex(rgb) {
    if (!rgb || rgb === 'transparent') return null;
    
    // Handle hex colors that are already in hex format
    if (rgb.startsWith('#')) return rgb;
    
    // Handle rgb() format
    const match = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
    if (!match) return null;
    
    const r = parseInt(match[1]);
    const g = parseInt(match[2]);  
    const b = parseInt(match[3]);
    
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}
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
    console.log('changeColor called with:', color);
    updateColorIndicator(color);
    
    // Apply color to currently selected element if it exists
    if (selectedElement && selectedElement.classList.contains('text-element')) {
        console.log('Applying color to selected element:', selectedElement);
        const textSpan = selectedElement.querySelector('span[contenteditable]');
        if (textSpan) {
            console.log('Found text span, applying color:', color);
            textSpan.style.color = color;
        } else {
            console.log('No text span found in selected element');
        }
    } else {
        console.log('No selected text element found');
    }
    
    // Also update any focused contenteditable element (blue border state)
    const focusedElement = document.activeElement;
    if (focusedElement && focusedElement.hasAttribute('contenteditable')) {
        console.log('Applying color to focused element:', focusedElement);
        focusedElement.style.color = color;
        
        // Also select the parent element to make sure it's in the selected state
        const parentElement = focusedElement.closest('.design-element');
        if (parentElement && !parentElement.classList.contains('selected')) {
            console.log('Auto-selecting parent element');
            selectElement(parentElement);
        }
    }
}

function changeFontSize(size) {
    console.log('changeFontSize called with size:', size);
    
    const fontSizeValue = document.getElementById('fontSizeValue');
    if (fontSizeValue) {
        fontSizeValue.textContent = size + 'px';
    }
    
    // Apply to currently selected element if it exists
    if (selectedElement && selectedElement.classList.contains('text-element')) {
        const textSpan = selectedElement.querySelector('span[contenteditable]');
        if (textSpan) {
            // Apply font size directly without logging too much
            textSpan.style.fontSize = size + 'px';
            
            // Update stored original font size
            textSpan.originalFontSize = size + 'px';
            
            // If arch is active, recreate the arch with throttling
            const archBtn = document.getElementById('archBtn');
            if (archBtn && archBtn.classList.contains('active') && textSpan.classList.contains('text-arch')) {
                // Clear any existing timeout to prevent multiple recreations
                if (textSpan.fontSizeUpdateTimeout) {
                    clearTimeout(textSpan.fontSizeUpdateTimeout);
                }
                
                const archSlider = document.getElementById('archCurve');
                const curvature = archSlider ? parseFloat(archSlider.value) : 0;
                
                // Throttle arch recreation to prevent performance issues
                textSpan.fontSizeUpdateTimeout = setTimeout(() => {
                    createSimpleArchEffect(textSpan, curvature);
                }, 100); // Increased timeout for better performance
            }
        }
    }
    
    // Also update any focused contenteditable element (blue border state)
    const focusedElement = document.activeElement;
    if (focusedElement && focusedElement.hasAttribute('contenteditable')) {
        console.log('Applying font size to focused element:', size);
        focusedElement.style.fontSize = size + 'px';
        
        // Also select the parent element to make sure it's in the selected state
        const parentElement = focusedElement.closest('.design-element');
        if (parentElement && !parentElement.classList.contains('selected')) {
            selectElement(parentElement);
        }
        
        // If arch is active on focused element, recreate it
        const parentTextSpan = parentElement ? parentElement.querySelector('span[contenteditable]') : null;
        if (parentTextSpan && parentTextSpan.classList.contains('text-arch')) {
            const archBtn = document.getElementById('archBtn');
            if (archBtn && archBtn.classList.contains('active')) {
                const archSlider = document.getElementById('archCurve');
                const curvature = archSlider ? parseFloat(archSlider.value) : 0;
                console.log('Recreating arch for focused element with new font size');
                
                setTimeout(() => {
                    createSimpleArchEffect(parentTextSpan, curvature);
                }, 10);
            }
        }
    }
}

function changeFontFamily(fontFamily) {
    console.log('changeFontFamily called with font:', fontFamily);
    
    // Update the select element font preview
    const fontFamilySelector = document.getElementById('fontFamily');
    if (fontFamilySelector) {
        fontFamilySelector.setAttribute('data-current-font', fontFamily);
        fontFamilySelector.style.fontFamily = fontFamily;
    }
    
    // Apply to currently selected element if it exists
    if (selectedElement && selectedElement.classList.contains('text-element')) {
        console.log('Applying font family to selected element:', selectedElement);
        const textSpan = selectedElement.querySelector('span[contenteditable]');
        if (textSpan) {
            console.log('Found text span, applying font family:', fontFamily);
            textSpan.style.fontFamily = fontFamily;
        } else {
            console.log('No text span found in selected element');
        }
    } else {
        console.log('No selected text element found');
    }
    
    // Also update any focused contenteditable element (blue border state)
    const focusedElement = document.activeElement;
    if (focusedElement && focusedElement.hasAttribute('contenteditable')) {
        console.log('Applying font family to focused element:', focusedElement);
        focusedElement.style.fontFamily = fontFamily;
        
        // Also select the parent element to make sure it's in the selected state
        const parentElement = focusedElement.closest('.design-element');
        if (parentElement && !parentElement.classList.contains('selected')) {
            selectElement(parentElement);
        }
    }
}

function toggleBold() {
    console.log('toggleBold called');
    const boldBtn = document.getElementById('boldBtn');
    
    let isBold = false;
    
    // Apply to currently selected element if it exists
    if (selectedElement && selectedElement.classList.contains('text-element')) {
        const textSpan = selectedElement.querySelector('span[contenteditable]');
        if (textSpan) {
            const currentWeight = window.getComputedStyle(textSpan).fontWeight;
            isBold = currentWeight === 'bold' || currentWeight === '700' || parseInt(currentWeight) >= 700;
            
            if (isBold) {
                textSpan.style.fontWeight = '400';
                boldBtn.classList.remove('active');
            } else {
                textSpan.style.fontWeight = '700';
                boldBtn.classList.add('active');
            }
        }
    }
    
    // Also update any focused contenteditable element (blue border state)
    // Also update any focused contenteditable element (blue border state)
    const focusedElement = document.activeElement;
    if (focusedElement && focusedElement.hasAttribute('contenteditable')) {
        const currentWeight = window.getComputedStyle(focusedElement).fontWeight;
        isBold = currentWeight === 'bold' || currentWeight === '700' || parseInt(currentWeight) >= 700;
        
        if (isBold) {
            focusedElement.style.fontWeight = '400';
            boldBtn.classList.remove('active');
        } else {
            focusedElement.style.fontWeight = '700';
            boldBtn.classList.add('active');
        }
        
        // Also select the parent element
        const parentElement = focusedElement.closest('.design-element');
        if (parentElement && !parentElement.classList.contains('selected')) {
            selectElement(parentElement);
        }
    }
}

// Font weight function removed - using simple bold toggle only

// Helper function to create simple arch effect using custom curved text
function createSimpleArchEffect(textSpan, curvature) {
    console.log('Creating arch effect with custom curved text, curvature:', curvature);
    
    // Store original fontSize before any modifications
    if (!textSpan.originalFontSize) {
        const computedStyle = window.getComputedStyle(textSpan);
        textSpan.originalFontSize = computedStyle.fontSize;
        console.log('Stored original font size:', textSpan.originalFontSize);
    }
    
    // Remove any existing arch effect
    if (textSpan.originalText) {
        // Restore original text
        textSpan.innerHTML = textSpan.originalText;
        textSpan.style.position = '';
        textSpan.style.display = '';
        textSpan.style.height = '';
        textSpan.style.width = '';
    }
    
    if (curvature === 0) {
        // No arch effect, keep text normal
        console.log('Curvature is 0, removing arch effect');
        return;
    }
    
    try {
        // Store original text
        if (!textSpan.originalText) {
            textSpan.originalText = textSpan.textContent;
        }
        
        // Calculate radius with better progression that works from 0 to 50+
        const absCurvature = Math.abs(curvature);
        let radius;
        
        if (absCurvature === 0) {
            // Perfect 0 - no arch
            console.log('Zero curvature - no arch effect');
            return;
        } else if (absCurvature <= 1) {
            // Very sharp curve for 0.1 to 1
            radius = 20 + (absCurvature * 30); // 20 to 50
        } else if (absCurvature <= 5) {
            // Sharp for 1 to 5
            radius = 50 + ((absCurvature - 1) * 20); // 50 to 130
        } else if (absCurvature <= 15) {
            // Medium for 5 to 15  
            radius = 130 + ((absCurvature - 5) * 6); // 130 to 190
        } else if (absCurvature <= 30) {
            // Gentle curve for 15 to 30
            radius = 190 + ((absCurvature - 15) * 2); // 190 to 220
        } else if (absCurvature <= 50) {
            // Very gentle for 30 to 50
            radius = 220 + ((absCurvature - 30) * 4); // 220 to 300
        } else {
            // Maximum gentle curve for 50+
            radius = 300;
        }
        
        // Minimum radius
        radius = Math.max(radius, 15);
        
        console.log(`Custom curved text radius: ${radius} for curvature: ${curvature}`);
        
        // Direction: positive = arch up, negative = arch down
        const direction = curvature > 0 ? -1 : 1;
        
        // Create curved text - this preserves Hebrew text direction
        if (typeof createCurvedText === 'function') {
            createCurvedText(textSpan, radius, direction);
            console.log('✅ Custom curved text effect created successfully for Hebrew');
        } else {
            console.error('createCurvedText function not available');
        }
        
    } catch (error) {
        console.error('❌ Error creating curved text effect:', error);
        // Fallback to simple CSS transform
        const angle = curvature * 1.5;
        textSpan.style.transform = `rotate(${angle}deg)`;
        textSpan.style.transformOrigin = 'center center';
    }
}

// Remove arch effect with custom cleanup
function removeSimpleArchEffect(textSpan) {
    console.log('Removing arch effect with custom cleanup');
    
    // Clear any pending timeouts
    if (textSpan.fontSizeUpdateTimeout) {
        clearTimeout(textSpan.fontSizeUpdateTimeout);
        delete textSpan.fontSizeUpdateTimeout;
    }
    
    // Remove arch class
    textSpan.classList.remove('text-arch');
    
    // If there's an SVG container, try to extract text and remove it
    const svgContainer = textSpan.querySelector('.svg-arch-container, .arch-svg-container');
    if (svgContainer) {
        console.log('Found SVG container, removing...');
        // Try to get text from SVG textPath
        const textPath = svgContainer.querySelector('textPath');
        if (textPath && textPath.textContent) {
            textSpan.textContent = textPath.textContent;
        }
        svgContainer.remove();
    }
    
    // Restore original text if it exists and no SVG was found
    if (textSpan.originalText && !svgContainer) {
        try {
            textSpan.innerHTML = textSpan.originalText;
            console.log('✅ Original text restored');
        } catch (error) {
            console.error('❌ Error restoring original text:', error);
        }
    }
    
    // Reset container styles to original
    textSpan.style.position = '';
    textSpan.style.display = '';
    textSpan.style.height = '';
    textSpan.style.width = '';
    textSpan.style.verticalAlign = '';
    textSpan.style.overflow = '';
    textSpan.style.textAlign = '';
    
    // Clear CSS transforms as fallback
    textSpan.style.transform = '';
    textSpan.style.transformOrigin = '';
    
    // Restore original font size if stored
    if (textSpan.originalFontSize) {
        textSpan.style.fontSize = textSpan.originalFontSize;
    }
    
    console.log('✅ Arch effect removed completely');
}

// Replace complex SVG functions with simple ones
function createArchEffect(textSpan, curvature) {
    createSimpleArchEffect(textSpan, curvature);
}

function removeArchEffect(textSpan) {
    removeSimpleArchEffect(textSpan);
}

// Remove old functions completely
function wrapTextForArch(textSpan) {
    return;
}

function unwrapTextFromArch(textSpan) {
    return;
}

function toggleArch() {
    console.log('toggleArch called');
    const archBtn = document.getElementById('archBtn');
    const archSlider = document.getElementById('archCurve');
    const archControls = document.querySelector('.arch-controls');
    
    let isArched = archBtn.classList.contains('active');
    
    if (isArched) {
        // Turn off arch
        archBtn.classList.remove('active');
        archSlider.style.display = 'none';
        archControls.style.display = 'none';
        
        // Remove arch from selected element
        if (selectedElement && selectedElement.classList.contains('text-element')) {
            const textSpan = selectedElement.querySelector('span[contenteditable]');
            if (textSpan) {
                textSpan.classList.remove('text-arch');
                removeSimpleArchEffect(textSpan);
            }
        }
        
        // Reset slider value
        archSlider.value = 0;
        document.getElementById('archCurveValue').textContent = '0';
    } else {
        // Turn on arch
        archBtn.classList.add('active');
        archSlider.style.display = 'block';
        archControls.style.display = 'block';
        
        // Apply arch to selected element if exists
        if (selectedElement && selectedElement.classList.contains('text-element')) {
            const textSpan = selectedElement.querySelector('span[contenteditable]');
            if (textSpan) {
                textSpan.classList.add('text-arch');
                const curvature = parseFloat(archSlider.value) || 0;
                createSimpleArchEffect(textSpan, curvature);
            }
        }
    }
}

function updateArchCurve(value) {
    console.log('updateArchCurve called with value:', value);
    document.getElementById('archCurveValue').textContent = value;
    
    // Apply to currently selected element if it exists
    if (selectedElement && selectedElement.classList.contains('text-element')) {
        const textSpan = selectedElement.querySelector('span[contenteditable]');
        if (textSpan && textSpan.classList.contains('text-arch')) {
            const curvature = parseFloat(value);
            
            // Add smooth transition with throttling for better performance
            if (textSpan.archUpdateTimeout) {
                clearTimeout(textSpan.archUpdateTimeout);
            }
            
            textSpan.archUpdateTimeout = setTimeout(() => {
                createSimpleArchEffect(textSpan, curvature);
            }, 50); // Reduced timeout for smoother real-time updates
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
                <img src="${data.image_url}" class="image-element js-image-medium">
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
    
    // Check if Hebrew SVG arch text function is loaded
    if (typeof createCurvedText === 'undefined') {
        console.warn('⚠️ Hebrew SVG arch text function not loaded - arch effects may not work properly');
    } else {
        console.log('✅ Hebrew SVG arch text function loaded successfully');
    }
    
    // Initialize color indicator
    updateColorIndicator('#000000');
    
    // בדיקה האם יש מוצר נבחר מראש
    const preSelectedDropdownItem = document.querySelector('.product-dropdown-item.active');
    if (preSelectedDropdownItem) {
        console.log('Pre-selected product found, enabling tools');
        enableDesignTools();
        // Update the selected product object
        selectedProduct = { 
            id: preSelectedDropdownItem.dataset.productId, 
            image: preSelectedDropdownItem.dataset.productImage,
            name: preSelectedDropdownItem.dataset.productName,
            price: preSelectedDropdownItem.dataset.productPrice
        };
    } else {
        console.log('No product selected, disabling tools');
        disableDesignTools();
    }
    
    // Auto-select product if one is already selected (old method)
    const selectedProductOld = document.querySelector('.product-option.selected');
    if (selectedProductOld) {
        selectProduct(selectedProductOld);
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
            fontSizeValue.textContent = this.value + 'px';
            // Apply to selected text element immediately
            changeFontSize(this.value);
        });
    }
    
    // Add text input handling - Enter key to add text
    const textInput = document.getElementById('textInput');
    if (textInput) {
        textInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                addText();
            }
        });
    }
    
    // Add color picker event listener
    const textColorPicker = document.getElementById('textColor');
    if (textColorPicker) {
        // Listen to both 'change' and 'input' events for real-time updates
        textColorPicker.addEventListener('change', function() {
            changeColor(this.value);
        });
        textColorPicker.addEventListener('input', function() {
            changeColor(this.value);
        });
    }
    
    // Add font family selector event listener
    const fontFamilySelector = document.getElementById('fontFamily');
    if (fontFamilySelector) {
        fontFamilySelector.addEventListener('change', function() {
            changeFontFamily(this.value);
        });
    }
    
    // Add drag and drop functionality for Freepik images
    const designCanvas = document.getElementById('designCanvas');
    if (designCanvas) {
        // Prevent default drag behaviors
        designCanvas.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
            designCanvas.style.border = '2px dashed #007bff';
        });
        
        designCanvas.addEventListener('dragenter', function(e) {
            e.preventDefault();
            designCanvas.style.border = '2px dashed #007bff';
        });
        
        designCanvas.addEventListener('dragleave', function(e) {
            e.preventDefault();
            designCanvas.style.border = '1px solid #ddd';
        });
        
        designCanvas.addEventListener('drop', function(e) {
            e.preventDefault();
            designCanvas.style.border = '1px solid #ddd';
            
            // Get image data from the dragged element
            const imageUrl = e.dataTransfer.getData('text/plain');
            const imageAlt = e.dataTransfer.getData('text/alt');
            
            if (imageUrl) {
                // Create image element on canvas
                addImageToCanvas(imageUrl, imageAlt, e.offsetX, e.offsetY);
            }
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

// פונקציה להפיכת אלמנט לגריר
function makeDraggable(element) {
    let isDragging = false;
    let startX, startY, startLeft, startTop;
    
    element.addEventListener('mousedown', function(e) {
        if (e.target.classList.contains('resize-handle') || e.target.tagName === 'BUTTON') {
            return; // Don't drag when clicking resize handle or button
        }
        
        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;
        startLeft = parseInt(window.getComputedStyle(element).left);
        startTop = parseInt(window.getComputedStyle(element).top);
        
        element.style.zIndex = '100';
        
        e.preventDefault();
    });
    
    document.addEventListener('mousemove', function(e) {
        if (!isDragging) return;
        
        const deltaX = e.clientX - startX;
        const deltaY = e.clientY - startY;
        
        element.style.left = (startLeft + deltaX) + 'px';
        element.style.top = (startTop + deltaY) + 'px';
    });
    
    document.addEventListener('mouseup', function() {
        if (isDragging) {
            isDragging = false;
            element.style.zIndex = '10';
        }
    });
}

// פונקציה להוספת תמונה לקנבס
function addImageToCanvas(imageUrl, imageAlt, x, y) {
    const designCanvas = document.getElementById('designCanvas');
    if (!designCanvas) return;
    
    // Create image container
    const imageContainer = document.createElement('div');
    imageContainer.className = 'design-image draggable-element';
    imageContainer.style.position = 'absolute';
    imageContainer.style.left = x + 'px';
    imageContainer.style.top = y + 'px';
    imageContainer.style.cursor = 'move';
    imageContainer.style.border = '2px solid transparent';
    imageContainer.style.borderRadius = '4px';
    imageContainer.style.zIndex = '10';
    
    // Create image element
    const img = document.createElement('img');
    img.src = imageUrl;
    img.alt = imageAlt || 'Freepik Image';
    img.style.maxWidth = '200px';
    img.style.maxHeight = '200px';
    img.style.width = 'auto';
    img.style.height = 'auto';
    img.style.display = 'block';
    
    // Add resize handles
    const resizeHandle = document.createElement('div');
    resizeHandle.className = 'resize-handle';
    resizeHandle.style.position = 'absolute';
    resizeHandle.style.bottom = '0';
    resizeHandle.style.right = '0';
    resizeHandle.style.width = '10px';
    resizeHandle.style.height = '10px';
    resizeHandle.style.background = '#007bff';
    resizeHandle.style.cursor = 'se-resize';
    resizeHandle.style.display = 'none';
    
    // Delete button
    const deleteBtn = document.createElement('button');
    deleteBtn.innerHTML = '×';
    deleteBtn.style.position = 'absolute';
    deleteBtn.style.top = '-10px';
    deleteBtn.style.right = '-10px';
    deleteBtn.style.width = '20px';
    deleteBtn.style.height = '20px';
    deleteBtn.style.background = '#dc3545';
    deleteBtn.style.color = 'white';
    deleteBtn.style.border = 'none';
    deleteBtn.style.borderRadius = '50%';
    deleteBtn.style.cursor = 'pointer';
    deleteBtn.style.fontSize = '12px';
    deleteBtn.style.display = 'none';
    deleteBtn.style.zIndex = '11';
    
    // Event listeners
    imageContainer.addEventListener('click', function() {
        // Remove selection from other elements
        document.querySelectorAll('.design-image').forEach(el => {
            el.style.border = '2px solid transparent';
            el.querySelector('.resize-handle').style.display = 'none';
            el.querySelector('button').style.display = 'none';
        });
        
        // Select this element
        this.style.border = '2px solid #007bff';
        resizeHandle.style.display = 'block';
        deleteBtn.style.display = 'block';
    });
    
    deleteBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        imageContainer.remove();
    });
    
    // Make draggable
    makeDraggable(imageContainer);
    
    // Append elements
    imageContainer.appendChild(img);
    imageContainer.appendChild(resizeHandle);
    imageContainer.appendChild(deleteBtn);
    designCanvas.appendChild(imageContainer);
    
    console.log('Image added to canvas:', imageUrl);
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
                <img src="${data.image_url}" class="image-element js-image-medium">
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
            badges += `<span class="badge bg-success transparent-indicator" title="רקע שקוף/קל להסרה">
                <i class="fas fa-magic"></i>
            </span>`;
        }
        if (image.is_likely_vector) {
            badges += `<span class="badge bg-primary vector-indicator" title="תמונה וקטורית">
                <i class="fas fa-vector-square"></i>
            </span>`;
        }
        
        // Add transparency score as a CSS class
        let transparencyClass = '';
        if (image.transparency_score && image.transparency_score > 30) {
            if (image.transparency_score > 70) {
                transparencyClass = 'transparency-high';
            } else if (image.transparency_score > 50) {
                transparencyClass = 'transparency-medium';
            } else {
                transparencyClass = 'transparency-low';
            }
        }
        
        html += `
            <div class="freepik-result-item position-relative" 
                 draggable="true" 
                 data-image-id="${image.id}" 
                 data-image-url="${image.preview}" 
                 data-image-title="${image.title}"
                 onclick="selectFreepikImage('${image.id}', '${image.preview}', '${image.title}')">
                ${badges}
                <img src="${image.thumbnail || image.preview}" 
                     alt="${image.title}" 
                     class="img-fluid rounded ${transparencyClass}">
                <div class="image-title">
                    <small title="${image.title}">${image.title.length > 30 ? image.title.substring(0, 30) + '...' : image.title}</small>
                </div>
            </div>
        `;
    });
    
    resultsContainer.innerHTML = html;
    resultsContainer.style.display = 'block';
    
    // Add drag event listeners to all result items
    const resultItems = resultsContainer.querySelectorAll('.freepik-result-item');
    resultItems.forEach(item => {
        item.addEventListener('dragstart', function(e) {
            const imageUrl = this.dataset.imageUrl;
            const imageTitle = this.dataset.imageTitle;
            
            // Set the data to transfer
            e.dataTransfer.setData('text/plain', imageUrl);
            e.dataTransfer.setData('text/alt', imageTitle);
            e.dataTransfer.effectAllowed = 'copy';
            
            // Add visual feedback
            this.style.opacity = '0.5';
        });
        
        item.addEventListener('dragend', function(e) {
            // Remove visual feedback
            this.style.opacity = '1';
        });
    });
    
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
                <div class="js-error-placeholder">
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
    
    // בדיקה אם יש מוצר נבחר
    if (!selectedProduct || !selectedProduct.id) {
        console.log('No product selected - showing warning');
        showNoProductMessage();
        return false;
    }
    
    // בדיקה אם הכלי מושבת
    if (button.classList.contains('disabled') || button.hasAttribute('disabled')) {
        console.log('Tool is disabled');
        return false;
    }
    
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
        document.getElementById('toolOptionsBar').classList.remove('hidden');
    } else {
        document.getElementById('toolOptionsBar').classList.add('hidden');
    }
    
    // Show search results area for images tool
    const searchResultsArea = document.getElementById('searchResultsArea');
    console.log('selectTool called for:', toolType, 'searchResultsArea found:', !!searchResultsArea);
    
    if (toolType === 'images') {
        if (searchResultsArea) {
            searchResultsArea.classList.remove('hidden');
            console.log('searchResultsArea displayed for images tool');
        }
    } else {
        if (searchResultsArea) {
            searchResultsArea.classList.add('hidden');
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

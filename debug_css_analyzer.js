/**
 * CSS Debug Analyzer Tool
 * משמש לבדיקת כללי CSS שחלים על אלמנט מסוים
 * 
 * שימוש:
 * 1. פתח את הדפדפן ועבור ל-Developer Tools (F12)
 * 2. בחר אלמנט עם ה-Inspector או עם document.querySelector()
 * 3. הכנס את הקוד הזה לקונסול
 * 4. או טען את הקובץ ואז קרא לפונקציה analyzeCSSForElement(element)
 */

(async function () {
    const el = $0; // האלמנט המסומן ב-Inspector (או תוכל להשתמש ב-document.querySelector())
    
    if (!el) {
        console.error("אין אלמנט מסומן! בחר אלמנט ב-Inspector או השתמש ב-document.querySelector()");
        return;
    }
    
    const results = [];
    const computed = window.getComputedStyle(el);

    /**
     * מקבל מידע על מקור הכלל
     */
    function getRuleOrigin(rule, sheet) {
        if (sheet.href) {
            const fileName = sheet.href.split('/').pop() || sheet.href;
            return `קובץ: ${fileName}`;
        }
        if (sheet.ownerNode && sheet.ownerNode.tagName === "STYLE") {
            return "inline <style> בתוך HTML";
        }
        if (sheet.ownerNode && sheet.ownerNode.id) {
            return `<style> עם ID: ${sheet.ownerNode.id}`;
        }
        return "מקור לא ידוע";
    }

    console.log(`🔍 מנתח CSS עבור האלמנט:`, el);
    console.log(`📋 Tag: ${el.tagName}, Classes: ${el.className}, ID: ${el.id}`);
    
    // עובר על כל קובצי ה-CSS
    for (const sheet of document.styleSheets) {
        let rules;
        try {
            rules = sheet.cssRules;
        } catch (e) {
            console.warn("❌ לא יכול לגשת לקובץ CSS בגלל CORS:", sheet.href);
            continue;
        }

        // עובר על כל הכללים בקובץ
        for (const rule of rules) {
            if (!rule.selectorText) continue;
            
            // מפצל סלקטורים מרובים (כמו .class1, .class2)
            const selectors = rule.selectorText.split(',');
            
            for (const selector of selectors) {
                const cleanSelector = selector.trim();
                try {
                    // בודק אם הסלקטור חל על האלמנט
                    if (el.matches(cleanSelector)) {
                        const declarations = [];
                        
                        // עובר על כל התכונות בכלל
                        for (let i = 0; i < rule.style.length; i++) {
                            const prop = rule.style[i];
                            const declaredVal = rule.style.getPropertyValue(prop).trim();
                            const priority = rule.style.getPropertyPriority(prop);
                            const computedVal = computed.getPropertyValue(prop).trim();

                            // בודק אם התכונה בוטלה
                            const isOverridden = declaredVal !== computedVal && !priority;
                            const status = isOverridden ? "🚫 בוטל (Overridden)" : "✅ פעיל (Active)";
                            
                            declarations.push({
                                property: prop,
                                declared: declaredVal + (priority ? ' !important' : ''),
                                computed: computedVal,
                                status: status,
                                isImportant: !!priority
                            });
                        }

                        results.push({
                            selector: cleanSelector,
                            origin: getRuleOrigin(rule, sheet),
                            declarations,
                            specificity: getSpecificity(cleanSelector)
                        });
                    }
                } catch (e) {
                    // סלקטור לא תקין
                    console.warn("סלקטור לא תקין:", cleanSelector);
                }
            }
        }
    }

    /**
     * מחשב specificity של סלקטור
     */
    function getSpecificity(selector) {
        const ids = (selector.match(/#/g) || []).length;
        const classes = (selector.match(/\./g) || []).length;
        const attributes = (selector.match(/\[/g) || []).length;
        const pseudoClasses = (selector.match(/:/g) || []).length - (selector.match(/::/g) || []).length;
        const elements = selector.replace(/#[^\s\+\>\~\.\[:]+/g, '').replace(/\.[^\s\+\>\~\.\[:]+/g, '').replace(/\[[^\]]*\]/g, '').replace(/:[^\s\+\>\~\.\[:]+/g, '').replace(/::[^\s\+\>\~\.\[:]+/g, '').split(/[\s\+\>\~]+/).filter(s => s && s !== '*').length;
        
        return `(${ids},${classes + attributes + pseudoClasses},${elements})`;
    }

    // מיון התוצאות לפי specificity
    results.sort((a, b) => {
        const aSpec = a.specificity.match(/\((\d+),(\d+),(\d+)\)/);
        const bSpec = b.specificity.match(/\((\d+),(\d+),(\d+)\)/);
        
        for (let i = 1; i <= 3; i++) {
            const diff = parseInt(bSpec[i]) - parseInt(aSpec[i]);
            if (diff !== 0) return diff;
        }
        return 0;
    });

    // יצירת הדוח
    const timestamp = new Date().toLocaleString('he-IL');
    const elementInfo = `Tag: ${el.tagName.toLowerCase()}${el.id ? `#${el.id}` : ''}${el.className ? `.${el.className.split(' ').join('.')}` : ''}`;
    
    const output = `🔍 דוח ניתוח CSS - ${timestamp}
📋 אלמנט: ${elementInfo}
📊 נמצאו ${results.length} כללים שחלים על האלמנט

${'='.repeat(80)}

${results.map((r, i) => {
        const decText = r.declarations.map(d => {
            const importantMark = d.isImportant ? ' 🔥' : '';
            return `  ${d.property}: ${d.declared}${importantMark}
    └── ${d.status}
    └── ערך מחושב: ${d.computed}`;
        }).join('\n\n');

        return `📌 כלל #${i + 1}
🎯 סלקטור: ${r.selector}
📈 Specificity: ${r.specificity}
📂 מקור: ${r.origin}

${r.selector} {
${decText}
}`;
    }).join('\n\n' + '='.repeat(80) + '\n\n')}

💡 הסברים:
✅ פעיל = התכונה משפיעה על האלמנט
🚫 בוטל = התכונה בוטלה על ידי כלל אחר עם specificity גבוה יותר
🔥 !important = התכונה מסומנת כ-important
📈 Specificity = (IDs, Classes+Attributes+Pseudo, Elements)

🔧 כלי דיבאגינג נוסף:
לבדיקת remove-bg-btn ספציפית, הרץ:
document.querySelector('.remove-bg-btn')?.closest('.design-element, .design-image, .draggable-element')?.classList.contains('selected')
`;

    // הורדת הקובץ
    console.log("📥 יוצר קובץ להורדה...");
    const blob = new Blob([output], { type: 'text/plain; charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `css-debug-${elementInfo.replace(/[^a-zA-Z0-9]/g, '-')}-${Date.now()}.txt`;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    console.log("✅ הקובץ הועבר להורדה!");
    console.log("📋 תוצאות הניתוח:", results);
    
    return results;
})();

/**
 * פונקציה נוספת לניתוח אלמנט ספציפי
 */
window.analyzeCSSForElement = function(element) {
    if (!element) {
        console.error("אנא ספק אלמנט לניתוח");
        return;
    }
    
    // מגדיר את $0 זמנית
    window.$0 = element;
    
    // מריץ את הניתוח
    return eval(document.querySelector('script[data-css-analyzer]')?.textContent || 'console.error("CSS Analyzer לא נטען")');
};

console.log("🚀 CSS Debug Analyzer נטען בהצלחה!");
console.log("📖 לשימוש: בחר אלמנט ב-Inspector והרץ את הקוד, או קרא ל-analyzeCSSForElement(element)");

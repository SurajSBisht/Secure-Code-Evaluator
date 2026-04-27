document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyze-btn');
    const codeInput = document.getElementById('code-input');
    
    // Output containers
    const tokensOut = document.getElementById('tokens-output');
    const astOut = document.getElementById('ast-output');
    const semanticOut = document.getElementById('semantic-output');

    analyzeBtn.addEventListener('click', async () => {
        const code = codeInput.value;
        if (!code.trim()) return;

        // UI loading state
        const originalText = analyzeBtn.innerHTML;
        analyzeBtn.innerHTML = 'Analyzing...';
        analyzeBtn.disabled = true;

        try {
            const response = await fetch('http://127.0.0.1:5000/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code })
            });

            const data = await response.json();
            
            // Remove empty classes
            tokensOut.classList.remove('empty');
            astOut.classList.remove('empty');
            semanticOut.classList.remove('empty');

            // 1. Display Tokens
            if (data.tokens) {
                tokensOut.innerHTML = data.tokens.map(t => 
                    `<div class="token-item">
                        <span class="token-type">${escapeHTML(t.type)}</span>
                        <span class="token-value">${escapeHTML(t.value)}</span>
                    </div>`
                ).join('');
            } else {
                tokensOut.innerHTML = '';
            }

            // 2. Display AST or Parser Errors
            if (data.ast) {
                astOut.innerHTML = renderAST(data.ast);
            } else {
                if (data.error && data.error.includes("Parser Error")) {
                   astOut.innerHTML = `<div class="error-text">❌ ${escapeHTML(data.error)}</div>`;
                } else {
                   astOut.innerHTML = '';
                }
            }

            // 3. Display Semantic Results or General Errors
            if (data.errors !== undefined && Array.isArray(data.errors)) {
                if (data.errors.length === 0) {
                    semanticOut.innerHTML = `<div class="success-text">🎉 No semantic errors! Code is perfectly valid.</div>`;
                } else {
                    semanticOut.innerHTML = data.errors.map(err => 
                        `<div class="error-text">⚠️ ${escapeHTML(err)}</div>`
                    ).join('');
                }
            } else if (data.error && !data.error.includes("Parser Error")) {
                semanticOut.innerHTML = `<div class="error-text">❌ ${escapeHTML(data.error)}</div>`;
                if (!data.ast) {
                   semanticOut.innerHTML += `<div class="error-text">Cannot proceed (Parser Error).</div>`;
                }
            }

        } catch (error) {
            console.error('Fetch Error:', error);
            tokensOut.innerHTML = `<div class="error-text">❌ Connection failed. Ensure Flask is running.</div>`;
            astOut.innerHTML = '';
            semanticOut.innerHTML = '';
        } finally {
            analyzeBtn.innerHTML = originalText;
            analyzeBtn.disabled = false;
        }
    });

    // Helper: Escape HTML to prevent XSS
    function escapeHTML(str) {
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }

    // Helper: Recursively format the AST into HTML elements
    function renderAST(node) {
        if (!node) return '';
        let html = `<div class="ast-node">`;
        html += `<span class="ast-type">${escapeHTML(node.type)}</span>`;
        if (node.value !== null && node.value !== undefined) {
             html += ` : <span class="ast-value">${escapeHTML(String(node.value))}</span>`;
        }
        if (node.children && node.children.length > 0) {
            html += `<div>${node.children.map(renderAST).join('')}</div>`;
        }
        html += `</div>`;
        return html;
    }
});

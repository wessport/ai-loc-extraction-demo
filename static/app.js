/**
 * AI Location Extraction Demo
 * Interactive demo showing AI-powered location extraction
 */

const API_BASE = '.';

const elements = {
    countrySelect: document.getElementById('country-select'),
    jobDescription: document.getElementById('job-description'),
    charCount: document.getElementById('char-count'),
    extractBtn: document.getElementById('extract-btn'),
    
    vizInitial: document.getElementById('viz-initial'),
    vizProcessing: document.getElementById('viz-processing'),
    vizResult: document.getElementById('viz-result'),
    
    scanText: document.getElementById('scan-text'),
    scanLine: document.getElementById('scan-line'),
    thinkingContent: document.getElementById('thinking-content'),
    
    resultCard: document.getElementById('result-card'),
    resultLocation: document.getElementById('result-location'),
    resultGranularity: document.getElementById('result-granularity'),
    resultModel: document.getElementById('result-model'),
    confidenceFill: document.getElementById('confidence-fill'),
    confidenceValue: document.getElementById('confidence-value'),
    highlightedText: document.getElementById('highlighted-text'),
    explanationContent: document.getElementById('explanation-content'),
};

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initParticles();
    initCharCounter();
    initExtractButton();
});

function initTheme() {
    const toggle = document.getElementById('theme-toggle');
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    toggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
    });
}

function initParticles() {
    const container = document.getElementById('particles');
    const particleCount = 20;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.animationDelay = `${Math.random() * 20}s`;
        particle.style.animationDuration = `${15 + Math.random() * 10}s`;
        container.appendChild(particle);
    }
}

function initCharCounter() {
    elements.jobDescription.addEventListener('input', () => {
        elements.charCount.textContent = elements.jobDescription.value.length;
    });
}

function initExtractButton() {
    elements.extractBtn.addEventListener('click', handleExtract);
}

async function handleExtract() {
    const jobDescription = elements.jobDescription.value.trim();
    const country = elements.countrySelect.value;
    
    if (!jobDescription) {
        showError('Please paste a job description first');
        return;
    }
    
    await runExtraction(jobDescription, country);
}

async function runExtraction(jobDescription, country) {
    elements.extractBtn.disabled = true;
    showState('processing');
    resetProcessingUI();
    
    const truncatedText = jobDescription.length > 500 
        ? jobDescription.substring(0, 500) + '...'
        : jobDescription;
    elements.scanText.textContent = truncatedText;
    
    const thinkingPromises = startThinkingStream(country);
    
    try {
        const response = await fetch(`${API_BASE}/api/extract`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                job_description: jobDescription,
                country: country,
            }),
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Extraction failed');
        }
        
        await animateProcessingSteps(data.processing_steps);
        await thinkingPromises;
        await showResult(data, jobDescription);
        
    } catch (error) {
        console.error('Extraction error:', error);
        showError(error.message);
    }
    
    elements.extractBtn.disabled = false;
}

function resetProcessingUI() {
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active', 'complete');
    });
    elements.thinkingContent.innerHTML = '';
}

async function animateProcessingSteps(steps) {
    for (const step of steps) {
        const stepEl = document.getElementById(`step-${step.step}`);
        if (!stepEl) continue;
        
        stepEl.classList.add('active');
        
        const detailEl = document.getElementById(`step-${step.step}-detail`);
        if (detailEl) {
            detailEl.textContent = step.description;
        }
        
        const displayTime = Math.max(step.duration_ms, 300);
        await sleep(displayTime);
        
        stepEl.classList.remove('active');
        stepEl.classList.add('complete');
        
        const timeEl = document.getElementById(`step-${step.step}-time`);
        if (timeEl) {
            timeEl.textContent = `${step.duration_ms}ms`;
        }
    }
}

function startThinkingStream(country) {
    const thoughts = [
        { text: 'Scanning job description...', delay: 300 },
        { text: 'Parsing document structure...', delay: 400 },
        { text: 'Identifying potential location mentions...', delay: 350 },
        { text: `Loading ${country} extraction rules...`, delay: 250 },
        { text: 'Applying address pattern matching...', delay: 450 },
        { text: 'Filtering corporate mailing addresses...', delay: 300 },
        { text: 'Evaluating candidate locations...', delay: 400 },
        { text: 'Determining granularity level...', delay: 250 },
        { text: 'Validating extraction result...', delay: 200 },
    ];
    
    let currentThought = 0;
    elements.thinkingContent.innerHTML = '';
    
    return new Promise(resolve => {
        const typeThought = () => {
            if (currentThought >= thoughts.length) {
                resolve();
                return;
            }
            
            const { text, delay } = thoughts[currentThought];
            typeText(text).then(() => {
                currentThought++;
                setTimeout(typeThought, delay);
            });
        };
        
        typeThought();
    });
}

function typeText(text) {
    return new Promise(resolve => {
        const line = document.createElement('div');
        elements.thinkingContent.appendChild(line);
        
        let charIndex = 0;
        const cursor = document.createElement('span');
        cursor.className = 'thinking-cursor';
        line.appendChild(cursor);
        
        const typeInterval = setInterval(() => {
            if (charIndex >= text.length) {
                clearInterval(typeInterval);
                cursor.remove();
                resolve();
                return;
            }
            
            line.insertBefore(
                document.createTextNode(text[charIndex]),
                cursor
            );
            charIndex++;
        }, 22);
    });
}

async function showResult(data, originalText) {
    await sleep(500);
    showState('result');
    
    if (data.location) {
        elements.resultLocation.textContent = data.location;
        elements.resultLocation.classList.remove('no-location');
    } else {
        elements.resultLocation.textContent = 'No location found';
        elements.resultLocation.classList.add('no-location');
    }
    
    elements.resultGranularity.textContent = data.granularity || 'N/A';
    elements.resultModel.textContent = data.model || 'gpt-4o-mini';
    
    const confidence = Math.round((data.confidence || 0) * 100);
    await sleep(300);
    elements.confidenceFill.style.width = `${confidence}%`;
    elements.confidenceValue.textContent = `${confidence}%`;
    
    if (data.highlight && data.highlight.start >= 0) {
        const before = originalText.substring(0, data.highlight.start);
        const highlighted = originalText.substring(data.highlight.start, data.highlight.end);
        const after = originalText.substring(data.highlight.end);
        
        elements.highlightedText.innerHTML = 
            escapeHtml(before) +
            `<span class="location-highlight">${escapeHtml(highlighted)}</span>` +
            escapeHtml(after);
    } else {
        elements.highlightedText.textContent = originalText;
    }
    
    if (data.explanation) {
        elements.explanationContent.textContent = '';
        await typeExplanation(data.explanation);
    } else {
        elements.explanationContent.textContent = 'No explanation provided.';
    }
}

async function typeExplanation(text) {
    let charIndex = 0;
    
    return new Promise(resolve => {
        const typeInterval = setInterval(() => {
            if (charIndex >= text.length) {
                clearInterval(typeInterval);
                resolve();
                return;
            }
            
            elements.explanationContent.textContent += text[charIndex];
            charIndex++;
        }, 10);
    });
}

function showState(state) {
    elements.vizInitial.classList.toggle('hidden', state !== 'initial');
    elements.vizProcessing.classList.toggle('hidden', state !== 'processing');
    elements.vizResult.classList.toggle('hidden', state !== 'result');
}

function showError(message) {
    alert(`Error: ${message}`);
    showState('initial');
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

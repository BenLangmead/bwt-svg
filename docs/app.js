// BWT-SVG Visualizer JavaScript
let pyodide = null;

// Initialize Pyodide when the page loads
async function initPyodide() {
    console.log('Loading Pyodide...');
    pyodide = await loadPyodide();
    
    // Load the BWT web code
    console.log('Loading BWT web code...');
    
    try {
        // Fetch and load the single Python file
        const response = await fetch('./bwt_web.py');
        const pythonCode = await response.text();
        
        console.log('Python code length:', pythonCode.length);
        console.log('Python code starts with:', pythonCode.substring(0, 100));
        
        // Execute the Python code in Pyodide
        await pyodide.runPythonAsync(pythonCode);
        
        console.log('BWT web code loaded successfully');
        
        // Test if render function is now available
        const testRender = await pyodide.runPythonAsync(`
            print("Testing render function availability...")
            print("render in globals:", 'render' in globals())
            if 'render' in globals():
                print("render function found!")
                print("render type:", type(render))
            else:
                print("render function NOT found!")
            "test complete"
        `);
        console.log('Render function test:', testRender);
        
    } catch (error) {
        console.error('Error loading BWT web code:', error);
        throw error;
    }
    
    console.log('Pyodide loaded successfully!');
}

// Show loading indicator
function showLoading() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('error').style.display = 'none';
    document.getElementById('output').style.display = 'none';
}

// Hide loading indicator
function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

// Show error message
function showError(message) {
    document.getElementById('error-message').textContent = message;
    document.getElementById('error').style.display = 'block';
    document.getElementById('output').style.display = 'none';
}

// Hide error message
function hideError() {
    document.getElementById('error').style.display = 'none';
}

// Display SVG results
function displayResults(horizontalSvg, verticalSvg) {
    const horizontalContainer = document.getElementById('horizontal-svg');
    const verticalContainer = document.getElementById('vertical-svg');
    
    // Clear previous results
    horizontalContainer.innerHTML = '';
    verticalContainer.innerHTML = '';
    
    // Check if SVG content is valid
    if (horizontalSvg && typeof horizontalSvg === 'string' && horizontalSvg.includes('<svg')) {
        horizontalContainer.innerHTML = horizontalSvg;
    } else {
        horizontalContainer.innerHTML = '<p>Error: Invalid text-space SVG content</p>';
        console.error('Invalid horizontal SVG:', horizontalSvg);
    }
    
    if (verticalSvg && typeof verticalSvg === 'string' && verticalSvg.includes('<svg')) {
        verticalContainer.innerHTML = verticalSvg;
    } else {
        verticalContainer.innerHTML = '<p>Error: Invalid lex-space SVG content</p>';
        console.error('Invalid vertical SVG:', verticalSvg);
    }
    
    // Set up download buttons
    setupDownloadButtons(horizontalSvg, verticalSvg);
    
    // Show output section
    document.getElementById('output').style.display = 'block';
    document.getElementById('output').classList.add('fade-in');
}

// Set up download button functionality
function setupDownloadButtons(horizontalSvg, verticalSvg) {
    const downloadHorizontalBtn = document.getElementById('download-horizontal');
    const downloadVerticalBtn = document.getElementById('download-vertical');
    
    downloadHorizontalBtn.onclick = () => downloadSVG(horizontalSvg, 'text-space.svg');
    downloadVerticalBtn.onclick = () => downloadSVG(verticalSvg, 'lex-space.svg');
}

// Download SVG as file
function downloadSVG(svgContent, filename) {
    if (!svgContent || !svgContent.includes('<svg')) {
        alert('No valid SVG content to download');
        return;
    }
    
    // Create blob and download
    const blob = new Blob([svgContent], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Clean up
    URL.revokeObjectURL(url);
}

// Validate input text
function validateInput(text) {
    if (!text) {
        throw new Error('Please enter some text');
    }
    
    if (!text.endsWith('$') && !text.endsWith('#')) {
        throw new Error('Text must end with $ or # to indicate the end of string');
    }
    
    if (text.length < 2) {
        throw new Error('Text must be at least 2 characters long');
    }
    
    return true;
}

// Handle form submission
async function handleSubmit(event) {
    event.preventDefault();
    
    if (!pyodide) {
        showError('Pyodide is still loading. Please wait...');
        return;
    }
    
    const textInput = document.getElementById('text-input').value.trim();
    //const showMums = document.getElementById('show-mums').checked;
    const showThresholds = document.getElementById('show-thresholds').checked;
    
    try {
        // Validate input
        validateInput(textInput);
        
        // Show loading
        showLoading();
        hideError();
        
        // Simple test first
        console.log('Testing basic Python execution...');
        const basicTest = await pyodide.runPythonAsync(`
            print("Python is working")
            "Hello from Python"
        `);
        console.log('Basic test result:', basicTest);
        
        // Test if render function exists
        console.log('Checking if render function exists...');
        const functionCheck = await pyodide.runPythonAsync(`
            print("Checking globals...")
            print("Available functions:", [name for name in globals() if callable(globals()[name])])
            print("render in globals:", 'render' in globals())
            if 'render' in globals():
                print("render function found!")
                print("render type:", type(render))
            else:
                print("render function NOT found!")
            "function check complete"
        `);
        console.log('Function check result:', functionCheck);
        
        // Generate horizontal SVG
        console.log('Generating horizontal SVG for:', textInput);
        await pyodide.runPythonAsync(`
            try:
                horizontal_result = render('${textInput}', which='horizontal', 
                                         show_mums=False, show_thresholds=${showThresholds ? 'True' : 'False'})
                print("Horizontal SVG generated successfully, length:", len(horizontal_result))
                print("First 100 chars:", horizontal_result[:100])
            except Exception as e:
                print("Error generating horizontal SVG:", str(e))
                import traceback
                traceback.print_exc()
                raise e
        `);
        
        const horizontalSvg = pyodide.runPython('horizontal_result');
        console.log('Horizontal SVG result:', horizontalSvg);
        console.log('Horizontal SVG type:', typeof horizontalSvg);
        
        // Generate vertical SVG
        console.log('Generating vertical SVG for:', textInput);
        await pyodide.runPythonAsync(`
            try:
                vertical_result = render('${textInput}', which='vertical', 
                                       show_mums=False, show_thresholds=${showThresholds ? 'True' : 'False'})
                print("Vertical SVG generated successfully, length:", len(vertical_result))
                print("First 100 chars:", vertical_result[:100])
            except Exception as e:
                print("Error generating vertical SVG:", str(e))
                import traceback
                traceback.print_exc()
                raise e
        `);
        
        const verticalSvg = pyodide.runPython('vertical_result');
        console.log('Vertical SVG result:', verticalSvg);
        console.log('Vertical SVG type:', typeof verticalSvg);
        
        // Display results
        displayResults(horizontalSvg, verticalSvg);
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred while generating the visualization');
    } finally {
        hideLoading();
    }
}

// Handle example button clicks
function handleExampleClick(text) {
    document.getElementById('text-input').value = text;
}

// Initialize the application
async function init() {
    try {
        // Set up form handler
        document.getElementById('bwt-form').addEventListener('submit', handleSubmit);
        
        // Set up example button handlers
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const text = btn.getAttribute('data-text');
                handleExampleClick(text);
            });
        });
        
        // Initialize Pyodide
        await initPyodide();
        
        // Hide loading and show form
        document.getElementById('loading').style.display = 'none';
        
        console.log('Application initialized successfully!');
        
    } catch (error) {
        console.error('Failed to initialize application:', error);
        showError('Failed to load the application. Please refresh the page.');
    }
}

// Start the application when the page loads
document.addEventListener('DOMContentLoaded', init);

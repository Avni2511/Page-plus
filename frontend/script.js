document.addEventListener('DOMContentLoaded', () => {
    const auditForm = document.getElementById('audit-form');
    const urlInput = document.getElementById('url-input');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnSpinner = submitBtn.querySelector('.spinner');
    
    const clientError = document.getElementById('client-error');
    const statusPanel = document.getElementById('status-panel');
    const errorPanel = document.getElementById('error-panel');
    const errorMessage = document.getElementById('error-message');
    const resultsPanel = document.getElementById('results-panel');
    
    // Result card bindings
    const reportUrl = document.getElementById('report-url');
    const resStatus = document.getElementById('res-status');
    const resStatusLbl = document.getElementById('res-status-lbl');
    const resTime = document.getElementById('res-time');
    const resWords = document.getElementById('res-words');
    const resH1 = document.getElementById('res-h1');
    const resImages = document.getElementById('res-images');
    const resTitle = document.getElementById('res-title');
    const resDesc = document.getElementById('res-desc');
    
    // Utility to determine DRF API endpoint dynamically
    const getApiUrl = () => {
        return '/api/audit/';
    };


    // Client-side URL Validator helper
    const isValidHttpUrl = (string) => {
        let url;
        try {
            url = new URL(string);
        } catch (_) {
            return false;  
        }
        return url.protocol === "http:" || url.protocol === "https:";
    };

    auditForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const rawUrl = urlInput.value.trim();
        
        // 1. Client-side Validation
        if (!rawUrl || !isValidHttpUrl(rawUrl)) {
            clientError.classList.remove('hidden');
            urlInput.classList.add('error-state');
            return;
        }
        
        // Clear past states
        clientError.classList.add('hidden');
        urlInput.classList.remove('error-state');
        errorPanel.classList.add('hidden');
        resultsPanel.classList.add('hidden');
        
        // 2. Set Loading UI State (Disable submit button and display loaders)
        setLoadingState(true);
        
        try {
            const apiEndpoint = getApiUrl();
            const response = await fetch(apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: rawUrl }),
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // 3. Render Audit Report Successfully
                renderResults(data);
            } else {
                // 4. Handle Server-Side Validation or Scraping Failures
                showError(data.error || "An unexpected error occurred while auditing the page.");
            }
        } catch (err) {
            // 5. Handle Network/Cors Failures
            showError("Network connection failed. Make sure the backend server is running at http://127.0.0.1:8000.");
        } finally {
            // 6. Reset UI State
            setLoadingState(false);
        }
    });

    function setLoadingState(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            btnText.style.opacity = '0';
            btnSpinner.classList.remove('hidden');
            statusPanel.classList.remove('hidden');
        } else {
            submitBtn.disabled = false;
            btnText.style.opacity = '1';
            btnSpinner.classList.add('hidden');
            statusPanel.classList.add('hidden');
        }
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorPanel.classList.remove('hidden');
        resultsPanel.classList.add('hidden');
    }

    function renderResults(data) {
        // Bind parameters
        reportUrl.textContent = data.url;
        resStatus.textContent = data.status_code;
        resTime.textContent = data.response_time;
        resWords.textContent = data.word_count.toLocaleString();
        resH1.textContent = data.h1_count;
        resImages.textContent = data.images_missing_alt;
        
        // Render Title & Description
        resTitle.textContent = data.title;
        resDesc.textContent = data.meta_description;
        
        // Handle badge styling & warnings for Status Code Card
        const statusCard = resStatus.closest('.card');
        statusCard.className = 'card status-card'; // reset classes
        
        if (data.status_code >= 200 && data.status_code < 300) {
            statusCard.classList.add('status-success');
            resStatusLbl.textContent = "Success / OK";
        } else if (data.status_code >= 300 && data.status_code < 400) {
            statusCard.classList.add('status-warning');
            resStatusLbl.textContent = "Redirect State";
        } else {
            statusCard.classList.add('status-error');
            resStatusLbl.textContent = "Error State";
        }
        
        // Image warnings badge
        const imagesCard = resImages.closest('.card');
        imagesCard.className = 'card images-card';
        if (data.images_missing_alt > 0) {
            imagesCard.classList.add('status-warning');
        } else {
            imagesCard.classList.add('status-success');
        }

        // Title and description warning states
        const titleCard = resTitle.closest('.card');
        titleCard.className = 'card span-full title-card';
        if (data.title === "Not available") {
            titleCard.classList.add('status-error');
        }

        const descCard = resDesc.closest('.card');
        descCard.className = 'card span-full desc-card';
        if (data.meta_description === "Not available") {
            descCard.classList.add('status-warning');
        }
        
        // Show Results
        resultsPanel.classList.remove('hidden');
    }
});

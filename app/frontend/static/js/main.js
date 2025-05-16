document.addEventListener('DOMContentLoaded', () => {
    const uploadBtn = document.getElementById('uploadBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const documentForm = document.getElementById('documentForm');
    const fileInput = document.getElementById('fileInput');
    const documentType = document.getElementById('documentType');
    const documentsList = document.getElementById('documentsList');
    const processedCount = document.getElementById('processedCount');
    const avgTime = document.getElementById('avgTime');

    // Initialize the page
    initializePage();

    // Event Listeners
    uploadBtn.addEventListener('click', () => {
        documentForm.style.display = 'block';
    });

    logoutBtn.addEventListener('click', handleLogout);
    documentForm.addEventListener('submit', handleDocumentUpload);

    // Fetch initial document list
    fetchDocuments();

    // Fetch statistics
    fetchStatistics();

    async function initializePage() {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('Error initializing page:', error);
            window.location.href = '/login';
        }
    }

    async function handleDocumentUpload(event) {
        event.preventDefault();

        const file = fileInput.files[0];
        if (!file) {
            alert('Please select a file');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('document_type', documentType.value);

        try {
            const response = await fetch('/api/v1/documents/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                alert('Document processed successfully!');
                documentForm.reset();
                fetchDocuments();
                fetchStatistics();
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to process document');
            }
        } catch (error) {
            console.error('Error processing document:', error);
            alert(`Error: ${error.message}`);
        }
    }

    async function handleLogout() {
        try {
            const response = await fetch('/api/v1/auth/logout', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (response.ok) {
                localStorage.removeItem('token');
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('Error logging out:', error);
            alert('Failed to logout');
        }
    }

    async function fetchDocuments() {
        try {
            const response = await fetch('/api/v1/documents/list', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (response.ok) {
                const documents = await response.json();
                renderDocuments(documents);
            }
        } catch (error) {
            console.error('Error fetching documents:', error);
        }
    }

    async function fetchStatistics() {
        try {
            const response = await fetch('/api/v1/analytics/statistics', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (response.ok) {
                const stats = await response.json();
                processedCount.textContent = stats.total_documents;
                avgTime.textContent = `${stats.average_processing_time.toFixed(2)}s`;
            }
        } catch (error) {
            console.error('Error fetching statistics:', error);
        }
    }

    function renderDocuments(documents) {
        documentsList.innerHTML = documents.map(doc => `
            <div class="bg-gray-50 p-4 rounded-lg">
                <div class="flex justify-between items-center">
                    <h3 class="font-semibold">${doc.filename}</h3>
                    <span class="text-sm text-gray-600">${new Date(doc.created_at).toLocaleString()}</span>
                </div>
                <div class="mt-2">
                    <p class="text-sm text-gray-600">Type: ${doc.document_type}</p>
                    <p class="text-sm text-gray-600">Status: ${doc.status}</p>
                </div>
                <div class="mt-4 flex justify-end">
                    <button onclick="viewDocument('${doc.id}')" class="text-blue-600 hover:text-blue-800">
                        View Details
                    </button>
                </div>
            </div>
        `).join('');
    }
});

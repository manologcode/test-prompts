document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const promptSelect = document.getElementById('promptSelect');
    const modelSelect = document.getElementById('modelSelect');
    const urlTextArea = document.getElementById('urlText');
    const getUrlBtn = document.getElementById('getUrlBtn');
    const clearUrlBtn = document.getElementById('clearUrlBtn');
    const promptText = document.getElementById('promptText');
    const newPromptBtn = document.getElementById('newPromptBtn');
    const newPromptModal = document.getElementById('newPromptModal');
    const savePromptBtn = document.getElementById('savePromptBtn');
    const cancelPromptBtn = document.getElementById('cancelPromptBtn');
    const promptTitle = document.getElementById('promptTitle');
    const updatePromptsBtn = document.getElementById('updatePromptsBtn');
    const generateBtn = document.getElementById('generateBtn');
    const resultContent = document.getElementById('resultContent');
    const editPromptBtn = document.getElementById('editPromptBtn');
    const modalTitle = document.getElementById('modalTitle');

    // Variable to track if we're editing or creating
    let isEditing = false;
    let currentEditingId = null;

    // Load prompts and models on page load
    loadPrompts();
    loadModels();

    // Event listeners
    getUrlBtn.addEventListener('click', handleUrlText);
    clearUrlBtn.addEventListener('click', () => {
        urlTextArea.value = '';
    });
    newPromptBtn.addEventListener('click', () => {
        isEditing = false;
        currentEditingId = null;
        modalTitle.textContent = 'Nuevo Prompt';
        promptTitle.value = '';
        newPromptModal.classList.remove('hidden');
    });

    editPromptBtn.addEventListener('click', async () => {
        const selectedPromptId = promptSelect.value;
        if (!selectedPromptId) {
            alert('Por favor, seleccione un prompt para editar');
            return;
        }
        
        try {
            const response = await fetch(`/prompts/${selectedPromptId}`);
            const data = await response.json();
            
            if (response.ok) {
                isEditing = true;
                currentEditingId = selectedPromptId;
                modalTitle.textContent = 'Editar Prompt';
                promptTitle.value = data.title;
                newPromptModal.classList.remove('hidden');
            } else {
                throw new Error('Error al cargar el prompt');
            }
        } catch (error) {
            console.error('Error loading prompt for edit:', error);
            alert('Error al cargar el prompt para editar');
        }
    });
    
    // Close modal function
    const closeModal = () => {
        newPromptModal.classList.add('hidden');
        // Clear modal inputs and reset state
        promptTitle.value = '';
        isEditing = false;
        currentEditingId = null;
    };

    // Close modal when clicking outside
    newPromptModal.addEventListener('click', (e) => {
        if (e.target === newPromptModal) {
            closeModal();
        }
    });

    // Close modal when clicking cancel button
    cancelPromptBtn.addEventListener('click', closeModal);

    // Handle save prompt
    savePromptBtn.addEventListener('click', handleSavePrompt);

    // Handle update prompt
    updatePromptsBtn.addEventListener('click', handleUpdatePrompt);

    // Handle generate
    generateBtn.addEventListener('click', handleGenerate);

    // Load prompts from API
    async function loadPrompts() {
        try {
            const response = await fetch('/list_prompts');
            const prompts = await response.json();
            
            // Clear existing options except the default one
            promptSelect.innerHTML = '<option value="">Seleccione un prompt...</option>';
            
            // Add new options
            prompts.forEach(prompt => {
                const option = document.createElement('option');
                option.value = prompt.id;
                option.textContent = prompt.name;
                promptSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading prompts:', error);
        }
    }

    // Load models from API
    async function loadModels() {
        try {
            const response = await fetch('/list_models');
            const models = await response.json();
            
            // Clear existing options except the default one
            modelSelect.innerHTML = '<option value="">Seleccione un modelo...</option>';
            
            // Add new options
            models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.id;
                option.textContent = model.name;
                modelSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading models:', error);
        }
    }

    // Handle URL text button click
    async function handleUrlText() {
        console.log('handleUrlText called');
        const text = urlTextArea.value.trim();
        if (!text) return;

        try {
            const response = await fetch('/text_to_url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            });

            const data = await response.json();
            if (data.text) {
                urlTextArea.value = data.text;
            }
        } catch (error) {
            console.error('Error processing URL:', error);
        }
    }

    // Update prompt text when a prompt is selected
    promptSelect.addEventListener('change', async function() {
        const promptId = this.value;
        if (!promptId) {
            promptText.value = '';
            return;
        }

        try {
            const response = await fetch(`/prompts/${promptId}`);
            const data = await response.json();
            if (data.prompt) {
                promptText.value = data.prompt;
            }
        } catch (error) {
            console.error('Error loading prompt content:', error);
            alert('Error al cargar el contenido del prompt');
        }
    });

    // Handle save prompt
    async function handleGenerate() {
        const selectedModel = modelSelect.value;
        const selectedPrompt = promptText.value.trim();
        const inputText = urlTextArea.value.trim();

        if (!selectedModel || !selectedPrompt || !inputText) {
            alert('Por favor, complete todos los campos (modelo, prompt y texto)');
            return;
        }

        // Get references to result elements
        const loadingAnimation = document.getElementById('loadingAnimation');
        const resultTitle = resultContent.querySelector('h3');
        const resultDiv = resultContent.querySelector('div:last-child');

        try {
            // Show result section and loading animation, hide previous result
            resultContent.classList.remove('hidden');
            loadingAnimation.classList.remove('hidden');
            resultTitle.classList.add('hidden');
            resultDiv.classList.add('hidden');
            resultDiv.textContent = '';

            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: selectedModel,
                    prompt: selectedPrompt,
                    text: inputText
                })
            });

            const data = await response.json();
            
            if (response.ok && data.generated_text) {
                // Hide loading animation and show result
                loadingAnimation.classList.add('hidden');
                resultTitle.classList.remove('hidden');
                resultDiv.classList.remove('hidden');
                resultDiv.textContent = data.generated_text;
                
                // Show response time
                const responseTimeElement = document.getElementById('responseTime');
                responseTimeElement.textContent = `Tiempo de respuesta: ${data.elapsed_time}s`;
            } else {
                throw new Error(data.detail || 'Error al generar el texto');
            }
        } catch (error) {
            console.error('Error generating text:', error);
            alert('Error al generar el texto: ' + error.message);
            // Hide loading and result section on error
            loadingAnimation.classList.add('hidden');
            resultContent.classList.add('hidden');
        }
    }

    async function handleUpdatePrompt() {
        const selectedPromptId = promptSelect.value;
        const newPromptContent = promptText.value.trim();

        if (!selectedPromptId) {
            alert('Por favor, seleccione un prompt para actualizar');
            return;
        }

        if (!newPromptContent) {
            alert('El contenido del prompt no puede estar vacío');
            return;
        }

        // Confirmar la actualización
        if (!confirm('¿Está seguro de que desea actualizar este prompt?')) {
            return;
        }

        try {
            const response = await fetch(`/prompts/${selectedPromptId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: promptSelect.options[promptSelect.selectedIndex].text,
                    prompt: newPromptContent
                })
            });

            if (response.ok) {
                alert('Prompt actualizado correctamente');
                // Recargar la lista de prompts para reflejar los cambios
                await loadPrompts();
            } else {
                alert('Error al actualizar el prompt');
            }
        } catch (error) {
            console.error('Error updating prompt:', error);
            alert('Error al actualizar el prompt');
        }
    }

    async function handleSavePrompt() {
        const title = promptTitle.value.trim();
        const prompt = promptText.value.trim();

        if (!title || !prompt) {
            alert('Por favor, complete todos los campos');
            return;
        }

        try {
            const url = isEditing ? `/prompts/${currentEditingId}` : '/prompts/';
            const method = isEditing ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: title,
                    prompt: prompt
                })
            });

            if (response.ok) {
                // Close modal
                closeModal();
                
                // Reload prompts list
                await loadPrompts();
                
                // Show success message
                alert(isEditing ? 'Prompt actualizado correctamente' : 'Prompt guardado correctamente');
            } else {
                alert(isEditing ? 'Error al actualizar el prompt' : 'Error al guardar el prompt');
            }
        } catch (error) {
            console.error('Error saving/updating prompt:', error);
            alert(isEditing ? 'Error al actualizar el prompt' : 'Error al guardar el prompt');
        }
    }
});
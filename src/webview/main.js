(function() {
    'use strict';

    const vscode = acquireVsCodeApi();

    // DOM elements
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const calculateBtn = document.getElementById('calculate-btn');
    const refreshBtn = document.getElementById('refresh-btn');
    const suggestionsBtn = document.getElementById('suggestions-btn');
    const timeframeSelect = document.getElementById('timeframe');
    const resourcesContent = document.getElementById('resources-content');
    const suggestionsContent = document.getElementById('suggestions-content');

    // Tab switching
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            
            // Update active tab button
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Update active tab pane
            tabPanes.forEach(pane => pane.classList.remove('active'));
            document.getElementById(`${targetTab}-tab`).classList.add('active');
        });
    });

    // Calculate costs button
    calculateBtn.addEventListener('click', () => {
        const timeframe = timeframeSelect.value;
        vscode.postMessage({
            command: 'calculateCosts',
            timeframe: timeframe
        });
        
        // Show loading state
        resourcesContent.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>Calculating infrastructure costs...</p>
                <p>Check the terminal for detailed output</p>
            </div>
        `;
    });

    // Refresh costs button
    refreshBtn.addEventListener('click', () => {
        vscode.postMessage({
            command: 'refreshCosts'
        });
        
        resourcesContent.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>Refreshing cost estimates...</p>
            </div>
        `;
    });

    // Get suggestions button
    suggestionsBtn.addEventListener('click', () => {
        vscode.postMessage({
            command: 'getSuggestions'
        });
        
        suggestionsContent.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>Generating AI-powered suggestions...</p>
                <p>Check the terminal for detailed output</p>
            </div>
        `;
    });

    // Listen for messages from the extension
    window.addEventListener('message', event => {
        const message = event.data;
        
        switch (message.command) {
            case 'costsCalculating':
                resourcesContent.innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Calculating costs for ${message.timeframe}...</p>
                        <p>Check the terminal for results</p>
                    </div>
                `;
                break;
                
            case 'suggestionsGenerating':
                suggestionsContent.innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Generating AI suggestions...</p>
                        <p>Check the terminal for results</p>
                    </div>
                `;
                break;
                
            case 'costsRefreshing':
                resourcesContent.innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Refreshing cost estimates...</p>
                    </div>
                `;
                break;
                
            case 'costsCalculated':
                displayCosts(message.costs, message.timeframe);
                break;
                
            case 'suggestionsGenerated':
                displaySuggestions(message.suggestions);
                break;
        }
    });

    function displayCosts(costs, timeframe) {
        if (!costs || costs.length === 0) {
            resourcesContent.innerHTML = `
                <div class="no-results">
                    <p>No resources found or costs calculated.</p>
                    <p>Make sure you have .tf files in your workspace.</p>
                </div>
            `;
            return;
        }

        let html = `
            <div class="costs-summary">
                <h3>Cost Summary for ${timeframe}</h3>
                <div class="total-cost">
                    <span class="label">Total Estimated Cost:</span>
                    <span class="amount">$${costs.totalCost.toFixed(2)}</span>
                </div>
            </div>
            <div class="resources-list">
                <h4>Resources Breakdown</h4>
        `;

        costs.resources.forEach(resource => {
            html += `
                <div class="resource-item">
                    <div class="resource-name">${resource.name}</div>
                    <div class="resource-cost">$${resource.monthlyCost.toFixed(2)}/month</div>
                </div>
            `;
        });

        html += '</div>';
        resourcesContent.innerHTML = html;
    }

    function displaySuggestions(suggestions) {
        if (!suggestions || suggestions.length === 0) {
            suggestionsContent.innerHTML = `
                <div class="no-results">
                    <p>No suggestions generated.</p>
                    <p>Make sure you have .tf files and OpenAI API key configured.</p>
                </div>
            `;
            return;
        }

        let html = `
            <div class="suggestions-list">
                <h3>AI Cost Optimization Suggestions</h3>
        `;

        suggestions.forEach((suggestion, index) => {
            html += `
                <div class="suggestion-item">
                    <h4>Option ${index + 1}: ${suggestion.type}</h4>
                    <div class="suggestion-details">
                        <p><strong>Estimated Savings:</strong> ${suggestion.savingsPercent}%</p>
                        <p><strong>New Monthly Cost:</strong> $${suggestion.newCost.toFixed(2)}</p>
                        <p><strong>Explanation:</strong> ${suggestion.explanation}</p>
                    </div>
                </div>
            `;
        });

        html += '</div>';
        suggestionsContent.innerHTML = html;
    }

    // Initialize with default timeframe
    timeframeSelect.value = '1m';
})();

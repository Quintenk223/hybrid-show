document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analysisForm');
    const resultsSection = document.getElementById('resultsSection');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = {
            sku: document.getElementById('sku').value,
            quantity: parseFloat(document.getElementById('quantity').value),
            price_current: parseFloat(document.getElementById('price_current').value),
            price_proposed: parseFloat(document.getElementById('price_proposed').value),
            moq_current: parseInt(document.getElementById('moq_current').value),
            moq_proposed: parseInt(document.getElementById('moq_proposed').value),
            lead_time_current: parseInt(document.getElementById('lead_time_current').value),
            lead_time_proposed: parseInt(document.getElementById('lead_time_proposed').value),
            reorder_quantity: parseFloat(document.getElementById('reorder_quantity').value),
            sis: parseInt(document.getElementById('sis').value)
        };

        try {
            // Show loading state
            resultsSection.style.display = 'block';
            resultsSection.innerHTML = '<div class="result-card"><h3>Analyzing...</h3><p>Please wait while we calculate your decision recommendation.</p></div>';

            // Make API call
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error('Analysis failed');
            }

            const data = await response.json();
            displayResults(data);
        } catch (error) {
            resultsSection.innerHTML = `<div class="result-card"><h3>Error</h3><p>${error.message}</p></div>`;
        }
    });
});

function displayResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    
    // Recommendation
    const recommendationBox = document.querySelector('.recommendation-box');
    const recommendationTitle = document.getElementById('recommendationTitle');
    const savingsDisplay = document.getElementById('savingsDisplay');
    
    const isSwitch = data.recommendation === 'SWITCH TO VIETNAM';
    recommendationBox.className = `recommendation-box ${isSwitch ? 'switch' : 'stay'}`;
    recommendationTitle.textContent = `Recommended: ${data.recommendation}`;
    
    if (data.cost_savings > 0) {
        savingsDisplay.textContent = `$${formatCurrency(data.cost_savings)} Saved per Cycle`;
        savingsDisplay.className = 'savings-display positive';
    } else {
        savingsDisplay.textContent = `Additional Cost: $${formatCurrency(Math.abs(data.npv_delta))}`;
        savingsDisplay.className = 'savings-display negative';
    }

    // Financial Analysis
    document.getElementById('npvDelta').textContent = formatCurrency(data.npv_delta);
    document.getElementById('npvDelta').className = `metric-value ${data.npv_delta > 0 ? 'positive' : 'negative'}`;
    document.getElementById('currentCost').textContent = formatCurrency(data.current_cost);
    document.getElementById('proposedCost').textContent = formatCurrency(data.proposed_cost);
    
    // Cost Breakdown
    const costBreakdown = document.getElementById('costBreakdown');
    const breakdown = data.cost_breakdown;
    costBreakdown.innerHTML = `
        <h4>Current Supplier (China) Breakdown:</h4>
        <div class="cost-item"><span>Product Cost:</span> <span>${formatCurrency(breakdown.price_cost_current)}</span></div>
        <div class="cost-item"><span>Freight (× FVM ${data.supplier_metrics.current.fvm}):</span> <span>${formatCurrency(breakdown.freight_cost_current)}</span></div>
        <div class="cost-item"><span>Duties (${data.supplier_metrics.current.tariffs_percent}%):</span> <span>${formatCurrency(breakdown.duties_current)}</span></div>
        <h4 style="margin-top: 15px;">Proposed Supplier (Vietnam) Breakdown:</h4>
        <div class="cost-item"><span>Product Cost:</span> <span>${formatCurrency(breakdown.price_cost_proposed)}</span></div>
        <div class="cost-item"><span>Freight (× FVM ${data.supplier_metrics.proposed.fvm}):</span> <span>${formatCurrency(breakdown.freight_cost_proposed)}</span></div>
        <div class="cost-item"><span>Duties (${data.supplier_metrics.proposed.tariffs_percent}%):</span> <span>${formatCurrency(breakdown.duties_proposed)}</span></div>
    `;

    // Risk Analysis
    const currentRisk = data.risk_analysis.current_risk;
    const proposedRisk = data.risk_analysis.proposed_risk;
    
    const currentRiskScore = document.getElementById('currentRiskScore');
    currentRiskScore.textContent = (currentRisk.total_risk_score * 100).toFixed(1) + '%';
    currentRiskScore.className = `risk-score ${getRiskClass(currentRisk.total_risk_score)}`;
    
    document.getElementById('currentRiskBreakdown').innerHTML = `
        <div class="risk-component"><span>GTS Penalty:</span> <span>${(currentRisk.gts_penalty * 100).toFixed(1)}%</span></div>
        <div class="risk-component"><span>GSV:</span> <span>${(currentRisk.gsv * 100).toFixed(1)}%</span></div>
        <div class="risk-component"><span>GLV Score:</span> <span>${(currentRisk.glv_score * 100).toFixed(1)}%</span></div>
    `;
    
    const proposedRiskScore = document.getElementById('proposedRiskScore');
    proposedRiskScore.textContent = (proposedRisk.total_risk_score * 100).toFixed(1) + '%';
    proposedRiskScore.className = `risk-score ${getRiskClass(proposedRisk.total_risk_score)}`;
    
    document.getElementById('proposedRiskBreakdown').innerHTML = `
        <div class="risk-component"><span>GTS Penalty:</span> <span>${(proposedRisk.gts_penalty * 100).toFixed(1)}%</span></div>
        <div class="risk-component"><span>GSV:</span> <span>${(proposedRisk.gsv * 100).toFixed(1)}%</span></div>
        <div class="risk-component"><span>GLV Score:</span> <span>${(proposedRisk.glv_score * 100).toFixed(1)}%</span></div>
    `;

    // Supplier Metrics
    const supplierMetrics = document.getElementById('supplierMetrics');
    supplierMetrics.innerHTML = `
        <div class="supplier-metrics-grid">
            <div class="supplier-metric-group">
                <h4>China (Current)</h4>
                <div class="supplier-metric"><span>GAS:</span> <span>${(data.supplier_metrics.current.gas * 100).toFixed(0)}%</span></div>
                <div class="supplier-metric"><span>FVM:</span> <span>×${data.supplier_metrics.current.fvm.toFixed(2)}</span></div>
                <div class="supplier-metric"><span>TFRF:</span> <span>${(data.supplier_metrics.current.tfrf * 100).toFixed(0)}%</span></div>
                <div class="supplier-metric"><span>Tariffs:</span> <span>${data.supplier_metrics.current.tariffs_percent}%</span></div>
            </div>
            <div class="supplier-metric-group">
                <h4>Vietnam (Proposed)</h4>
                <div class="supplier-metric"><span>GAS:</span> <span>${(data.supplier_metrics.proposed.gas * 100).toFixed(0)}%</span></div>
                <div class="supplier-metric"><span>FVM:</span> <span>×${data.supplier_metrics.proposed.fvm.toFixed(2)}</span></div>
                <div class="supplier-metric"><span>TFRF:</span> <span>${(data.supplier_metrics.proposed.tfrf * 100).toFixed(0)}%</span></div>
                <div class="supplier-metric"><span>Tariffs:</span> <span>${data.supplier_metrics.proposed.tariffs_percent}%</span></div>
            </div>
        </div>
        <div style="margin-top: 20px; padding: 15px; background: #f0f9ff; border-radius: 5px; font-size: 0.9em;">
            <strong>Trade Fragmentation Risk:</strong> Expected cost increase of ${(data.supplier_metrics.current.tfrf * 100).toFixed(0)}% (China) vs ${(data.supplier_metrics.proposed.tfrf * 100).toFixed(0)}% (Vietnam) due to trade bloc restrictions.<br>
            <strong>Maritime Risk Adjustment:</strong> Freight multiplier of ×${data.supplier_metrics.current.fvm.toFixed(2)} (China) vs ×${data.supplier_metrics.proposed.fvm.toFixed(2)} (Vietnam) for route volatility.
        </div>
    `;

    // Contingency Recommendations
    const contingencyRecs = document.getElementById('contingencyRecommendations');
    if (data.contingency_recommendations && data.contingency_recommendations.length > 0) {
        contingencyRecs.innerHTML = data.contingency_recommendations.map(rec => `
            <div class="contingency-item">
                <h4><span class="priority ${rec.priority.toLowerCase()}">${rec.priority}</span>${rec.category}</h4>
                <p>${rec.recommendation}</p>
            </div>
        `).join('');
    }

    // Legal Questions
    const legalQuestions = document.getElementById('legalQuestions');
    if (data.legal_questions && data.legal_questions.length > 0) {
        legalQuestions.innerHTML = data.legal_questions.map(q => `
            <div class="question-item">
                <h4><span class="category">${q.category}</span></h4>
                <p>${q.question}</p>
            </div>
        `).join('');
    }

    // Email Generator
    const emailGenerator = document.getElementById('emailGenerator');
    if (data.email_generator_prompt) {
        emailGenerator.innerHTML = `
            <div class="contingency-item">
                <p><strong>Monthly Update Prompt:</strong></p>
                <p style="margin-top: 10px; font-style: italic; color: #666;">${data.email_generator_prompt}</p>
            </div>
        `;
    }

    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

function getRiskClass(score) {
    if (score < 0.33) return 'low';
    if (score < 0.66) return 'medium';
    return 'high';
}


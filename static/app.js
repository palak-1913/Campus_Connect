document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('recommendForm');
    const resultsContainer = document.getElementById('resultsContainer');
    const targetContainer = document.getElementById('targetContainer');
    const loader = document.getElementById('loader');
    const errorMsg = document.getElementById('errorMsg');
    const resultsHeader = document.getElementById('resultsHeader');
    const cardViewBtn = document.getElementById('cardViewBtn');
    const listViewBtn = document.getElementById('listViewBtn');
    
    let currentResults = [];
    let currentTarget = null;

    // View toggles
    cardViewBtn.addEventListener('click', () => {
        cardViewBtn.classList.add('active');
        listViewBtn.classList.remove('active');
        resultsContainer.className = 'results-grid';
    });

    listViewBtn.addEventListener('click', () => {
        listViewBtn.classList.add('active');
        cardViewBtn.classList.remove('active');
        resultsContainer.className = 'results-list';
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const studentId = document.getElementById('studentId').value;
        const topN = document.getElementById('topN').value;
        
        // Reset state
        resultsContainer.innerHTML = '';
        if (targetContainer) targetContainer.innerHTML = '';
        resultsHeader.classList.add('hidden');
        errorMsg.classList.add('hidden');
        loader.classList.remove('hidden');
        
        try {
            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    student_id: parseInt(studentId),
                    top_n: parseInt(topN)
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Failed to fetch recommendations');
            }
            
            
            currentTarget = data.target;
            currentResults = data.recommendations;
            renderResults();
            
        } catch (error) {
            errorMsg.textContent = `Error: ${error.message}`;
            errorMsg.classList.remove('hidden');
        } finally {
            loader.classList.add('hidden');
        }
    });
    
    function renderResults() {
        if (currentTarget && targetContainer) {
            const targetSkillsTags = currentTarget.Skills ? currentTarget.Skills.split('|').map(s => `<span class="tag">${s.trim()}</span>`).join('') : '<span class="tag">None</span>';
            const targetProjectTags = currentTarget.Projects && currentTarget.Projects.toLowerCase() !== 'no projects' ? currentTarget.Projects.split('|').map(p => `<span class="tag">${p.trim()}</span>`).join('') : '<span class="tag">None</span>';
            
            targetContainer.innerHTML = `
                <div class="target-card fade-in">
                    <div class="target-badge"><i class="fa-solid fa-user"></i> Your Profile</div>
                    <div class="card-top">
                        <div>
                            <div class="name">${currentTarget.Name}</div>
                            <div class="domain">${currentTarget.Interested_domain}</div>
                        </div>
                    </div>
                    
                    <div class="info-row">
                        <span class="info-label">Academic Profile</span>
                        <div class="cgpa-pill"><i class="fa-solid fa-star"></i> CGPA: ${currentTarget.CGPA}</div>
                        <div style="margin-top: 0.3rem; color: #94a3b8; font-size: 0.85rem">${currentTarget.Course}</div>
                    </div>
                    
                    <div class="info-row">
                        <span class="info-label">Skills</span>
                        <div class="tags-container">
                            ${targetSkillsTags}
                        </div>
                    </div>
                    
                    <div class="info-row">
                        <span class="info-label">Projects</span>
                        <div class="tags-container">
                            ${targetProjectTags}
                        </div>
                    </div>
                </div>
            `;
        }

        if (currentResults.length === 0) {
            errorMsg.textContent = 'No recommendations found.';
            errorMsg.classList.remove('hidden');
            return;
        }
        
        resultsHeader.classList.remove('hidden');
        
        currentResults.forEach((profile, index) => {
            const delay = index * 0.1; // Staggered animation
            
            const skillsTags = profile.Skills ? profile.Skills.split('|').map(s => `<span class="tag">${s.trim()}</span>`).join('') : '<span class="tag">None</span>';
            const projectTags = profile.Projects && profile.Projects.toLowerCase() !== 'no projects' ? profile.Projects.split('|').map(p => `<span class="tag">${p.trim()}</span>`).join('') : '<span class="tag">None</span>';
            
            // Format score to percentage
            const matchScore = Math.round(profile.score * 100);
            
            const card = document.createElement('div');
            card.className = 'profile-card fade-in';
            card.style.animationDelay = `${delay}s`;
            card.innerHTML = `
                <div class="card-top">
                    <div>
                        <div class="name">${profile.Name}</div>
                        <div class="domain">${profile.Interested_domain}</div>
                    </div>
                    <div class="score-badge" title="Match Score">
                        <i class="fa-solid fa-chart-pie"></i> ${matchScore}%
                    </div>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Academic Profile</span>
                    <div class="cgpa-pill"><i class="fa-solid fa-star"></i> CGPA: ${profile.CGPA}</div>
                    <div style="margin-top: 0.3rem; color: #94a3b8; font-size: 0.85rem">${profile.Course}</div>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Skills</span>
                    <div class="tags-container">
                        ${skillsTags}
                    </div>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Projects</span>
                    <div class="tags-container">
                        ${projectTags}
                    </div>
                </div>
            `;
            
            resultsContainer.appendChild(card);
        });
    }
});

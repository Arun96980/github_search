document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const tabs = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const searchBtn = document.getElementById('search-btn');
    const resultsArea = document.getElementById('results-area');
    const resultsHeader = document.getElementById('results-header');
    const resultCount = document.getElementById('result-count');
    const emptyState = document.getElementById('empty-state');
    const loader = document.querySelector('.loader');
    const btnText = document.querySelector('.btn-text');
    const btnIcon = document.querySelector('.fa-arrow-right');
    const pagination = document.getElementById('pagination');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const pageInfo = document.getElementById('page-info');

    // State
    let currentMode = 'nlp';
    let currentPage = 1;

    // Tab Switching
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Add active class to current
            tab.classList.add('active');
            const targetId = `${tab.dataset.tab}-content`;
            document.getElementById(targetId).classList.add('active');

            currentMode = tab.dataset.tab;
        });
    });

    // Search Function
    searchBtn.addEventListener('click', () => {
        currentPage = 1; // Reset to first page on new search
        performSearch();
    });

    // Pagination
    prevBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            performSearch();
        }
    });

    nextBtn.addEventListener('click', () => {
        currentPage++;
        performSearch();
    });

    async function performSearch() {
        console.log('Starting search...');
        setLoading(true);
        resultsArea.innerHTML = '';
        resultsHeader.classList.add('hidden');
        emptyState.classList.add('hidden');
        resultsArea.classList.add('hidden');
        pagination.classList.add('hidden');

        try {
            let data;
            console.log('Mode:', currentMode, 'Page:', currentPage);
            if (currentMode === 'nlp') {
                const query = document.getElementById('nlp-input').value.trim();
                if (!query) {
                    console.log('Empty query');
                    setLoading(false);
                    return;
                }
                console.log('Calling NLP API...');
                data = await searchNLP(query, currentPage);
            } else {
                console.log('Calling Manual API...');
                data = await searchManual(currentPage);
            }

            console.log('Data received:', data);
            renderResults(data);
            updatePagination(data);
        } catch (error) {
            console.error('Search failed:', error);
            alert('Search failed. Please try again.');
        } finally {
            console.log('Search complete');
            setLoading(false);
        }
    }

    async function searchNLP(query, page) {
        const response = await fetch('/api/search/nlp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, page })
        });
        return await response.json();
    }

    async function searchManual(page) {
        const filters = {
            language: document.getElementById('lang-input').value.trim() || null,
            topics: document.getElementById('topic-input').value.split(',').map(t => t.trim()).filter(t => t) || null,
            stars_min: parseInt(document.getElementById('min-stars').value) || null,
            license: document.getElementById('license-select').value || null,
            updated_after: document.getElementById('updated-after').value || null,
            good_first_issue: document.getElementById('good-first-issue').checked,
            help_wanted: document.getElementById('help-wanted').checked,
            sort: document.getElementById('sort-select').value,
            order: 'desc',
            limit: 15,
            page: page
        };

        const response = await fetch('/api/search/manual', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(filters)
        });
        return await response.json();
    }

    function renderResults(data) {
        const items = data.results.items;
        const total = data.results.total_count;

        if (!items || items.length === 0) {
            emptyState.classList.remove('hidden');
            return;
        }

        resultsHeader.classList.remove('hidden');
        resultCount.textContent = `${formatNumber(total)} found`;
        resultsArea.classList.remove('hidden');

        items.forEach(repo => {
            const card = document.createElement('a');
            card.href = repo.html_url;
            card.target = '_blank';
            card.className = 'repo-item';

            // Use owner avatar
            const avatarUrl = repo.owner ? repo.owner.avatar_url : 'https://github.com/github.png';

            // Format date
            const updatedDate = new Date(repo.pushed_at).toLocaleDateString(undefined, {
                year: 'numeric', month: 'short', day: 'numeric'
            });

            // Topics
            const topicsHtml = (repo.topics || []).slice(0, 3)
                .map(t => `<span class="topic-tag">${t}</span>`).join(' ');

            card.innerHTML = `
                <img src="${avatarUrl}" alt="${repo.owner.login}" class="repo-avatar">
                <div class="repo-content">
                    <div class="repo-title-row">
                        <div class="repo-name">${repo.full_name}</div>
                        <div class="repo-meta-inline">
                            <span>${repo.language || ''}</span>
                        </div>
                    </div>
                    <div class="repo-desc">${repo.description || 'No description available.'}</div>
                    <div class="repo-stats">
                        <div class="stat-item stars">
                            <i class="fa-regular fa-star"></i>
                            <span>${formatNumber(repo.stargazers_count)}</span>
                        </div>
                        <div class="stat-item">
                            <i class="fa-regular fa-circle-dot"></i>
                            <span>${repo.open_issues_count} issues</span>
                        </div>
                        <div class="stat-item">
                            <span>Updated ${updatedDate}</span>
                        </div>
                        <div class="stat-item">
                            ${topicsHtml}
                        </div>
                    </div>
                </div>
            `;

            resultsArea.appendChild(card);
        });
    }

    function updatePagination(data) {
        const total = data.results.total_count;
        const limit = 15;
        const totalPages = Math.ceil(total / limit);

        if (totalPages > 1) {
            pagination.classList.remove('hidden');
            pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
            prevBtn.disabled = currentPage === 1;
            nextBtn.disabled = currentPage >= totalPages;
        } else {
            pagination.classList.add('hidden');
        }
    }

    function setLoading(isLoading) {
        if (isLoading) {
            loader.classList.remove('hidden');
            btnText.textContent = 'Searching...';
            btnIcon.classList.add('hidden');
            searchBtn.disabled = true;
        } else {
            loader.classList.add('hidden');
            btnText.textContent = 'Find Repositories';
            btnIcon.classList.remove('hidden');
            searchBtn.disabled = false;
        }
    }

    function formatNumber(num) {
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'k';
        }
        return num;
    }
});

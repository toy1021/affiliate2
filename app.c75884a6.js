class NewsApp {
constructor() {
this.data = null;
this.filteredArticles = [];
this.currentPage = 1;
this.articlesPerPage = 10;
this.currentCategory = '';
this.currentSource = '';
this.currentSearch = '';
this.init();
}
async init() {
try {
await this.loadData();
this.setupEventListeners();
this.render();
} catch (error) {
console.error('Failed to initialize app:', error);
document.getElementById('articles-container').innerHTML = '<p>記事の読み込みに失敗しました。</p>';
}
}
async loadData() {
const response = await fetch('articles.json');
this.data = await response.json();
this.filteredArticles = this.data.articles;
}
setupEventListeners() {
const searchInput = document.getElementById('search-input');
searchInput.addEventListener('input', (e) => {
this.currentSearch = e.target.value;
this.currentPage = 1;
this.filterArticles();
});
document.getElementById('category-filter').addEventListener('change', (e) => {
this.currentCategory = e.target.value;
this.currentPage = 1;
this.filterArticles();
});
document.getElementById('source-filter').addEventListener('change', (e) => {
this.currentSource = e.target.value;
this.currentPage = 1;
this.filterArticles();
});
document.getElementById('category-menu').addEventListener('click', (e) => {
if (e.target.tagName === 'A') {
e.preventDefault();
const category = e.target.dataset.category || '';
this.currentCategory = category;
document.getElementById('category-filter').value = category;
this.currentPage = 1;
this.filterArticles();
}
});
}
filterArticles() {
this.filteredArticles = this.data.articles.filter(article => {
const categoryMatch = !this.currentCategory || article.category === this.currentCategory;
const sourceMatch = !this.currentSource || article.source_name === this.currentSource;
let searchMatch = true;
if (this.currentSearch) {
const searchLower = this.currentSearch.toLowerCase();
const titleMatch = article.title.toLowerCase().includes(searchLower);
const summaryMatch = article.summary && article.summary.toLowerCase().includes(searchLower);
searchMatch = titleMatch || summaryMatch;
}
return categoryMatch && sourceMatch && searchMatch;
});
this.renderArticles();
this.renderPagination();
}
render() {
document.getElementById('update-time').textContent = this.data.metadata.last_updated;
document.getElementById('article-count').textContent = this.data.articles.length;
this.renderFilters();
this.renderSidebar();
this.renderArticles();
this.renderPagination();
document.getElementById('filters').style.display = 'flex';
document.getElementById('sidebar').style.display = 'block';
}
renderFilters() {
const categoryFilter = document.getElementById('category-filter');
categoryFilter.innerHTML = '<option value="">全カテゴリ</option>';
this.data.categories.forEach(cat => {
const option = document.createElement('option');
option.value = cat.name;
option.textContent = `${cat.name} (${cat.count})`;
categoryFilter.appendChild(option);
});
const sourceFilter = document.getElementById('source-filter');
sourceFilter.innerHTML = '<option value="">全ソース</option>';
this.data.sources.forEach(source => {
const option = document.createElement('option');
option.value = source.name;
option.textContent = `${source.name} (${source.count})`;
sourceFilter.appendChild(option);
});
}
renderSidebar() {
const categoryMenu = document.getElementById('category-menu');
categoryMenu.innerHTML = `
<li><a href="#" data-category="">全カテゴリ (${this.data.articles.length})</a></li>
${this.data.categories.map(cat => 
`<li><a href="#" data-category="${cat.name}">${cat.name} (${cat.count})</a></li>`
).join('')}
`;
}
renderArticles() {
const container = document.getElementById('articles-container');
const startIndex = (this.currentPage - 1) * this.articlesPerPage;
const endIndex = startIndex + this.articlesPerPage;
const pageArticles = this.filteredArticles.slice(startIndex, endIndex);
if (pageArticles.length === 0) {
container.innerHTML = '<p>該当する記事が見つかりません。</p>';
return;
}
container.innerHTML = pageArticles.map(article => `
<article class="article-card">
<div class="article-meta">
<span>${article.published_relative}</span>
<span>${article.category} | ${article.source_name}</span>
</div>
<h2 class="article-title">
<a href="articles/${this.createSlug(article.id)}.html">${article.title}</a>
</h2>
<p class="article-summary">${article.summary}</p>
${article.affiliate_links && article.affiliate_links.length > 0 ? `
<div class="affiliate-links">
${article.affiliate_links.map(link => 
`<a href="${link.url}" target="_blank" rel="noopener" class="affiliate-link">${link.text}</a>`
).join('')}
</div>
` : ''}
</article>
`).join('');
}
renderPagination() {
const pagination = document.getElementById('pagination');
const totalPages = Math.ceil(this.filteredArticles.length / this.articlesPerPage);
if (totalPages <= 1) {
pagination.style.display = 'none';
return;
}
pagination.style.display = 'flex';
let html = '';
if (this.currentPage > 1) {
html += `<button onclick="app.goToPage(${this.currentPage - 1})">前へ</button>`;
}
for (let i = Math.max(1, this.currentPage - 2); i <= Math.min(totalPages, this.currentPage + 2); i++) {
html += `<button onclick="app.goToPage(${i})" class="${i === this.currentPage ? 'active' : ''}">${i}</button>`;
}
if (this.currentPage < totalPages) {
html += `<button onclick="app.goToPage(${this.currentPage + 1})">次へ</button>`;
}
pagination.innerHTML = html;
}
goToPage(page) {
this.currentPage = page;
this.renderArticles();
this.renderPagination();
window.scrollTo(0, 0);
}
createSlug(articleId) {
let slug = articleId.replace(/ /g, '_').replace(/\
slug = slug.replace(/[<>:"|?*]/g, '');
return slug;
}
}
const app = new NewsApp();
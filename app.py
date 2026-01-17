import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
import os

st.set_page_config(
    page_title='NeuroDrive - Semantic File Search',
    page_icon='🔍',
    layout='wide',
    initial_sidebar_state='collapsed'
)

# Professional Enterprise CSS
st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    .block-container {
        padding: 1.5rem 3rem !important;
        max-width: 1600px !important;
    }
    
    /* Header */
    .app-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem 3rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .app-title {
        font-size: 2rem;
        font-weight: 700;
        color: white;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .app-subtitle {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.85);
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Cards */
    .card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        transition: all 0.2s;
    }
    
    .card:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Stats Card */
    .stat-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.25rem;
        text-align: center;
        transition: all 0.2s;
    }
    
    .stat-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    .stat-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.75rem;
        color: white;
        font-size: 1.5rem;
    }
    
    .stat-number {
        font-size: 1.875rem;
        font-weight: 700;
        color: #111827;
        margin: 0.5rem 0 0.25rem;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: #6b7280;
        font-weight: 500;
    }
    
    /* Search Container */
    .search-box {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        transition: border-color 0.2s;
    }
    
    .search-box:focus-within {
        border-color: #3b82f6;
    }
    
    /* Result Card */
    .result-item {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border-left: 4px solid #3b82f6;
        transition: all 0.2s;
    }
    
    .result-item:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transform: translateX(4px);
    }
    
    .result-header {
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .result-rank {
        background: #1e3a8a;
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.875rem;
        margin-right: 0.75rem;
    }
    
    .result-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: #111827;
        flex: 1;
    }
    
    .result-path {
        font-size: 0.875rem;
        color: #6b7280;
        margin-top: 0.25rem;
        font-family: 'SF Mono', Monaco, monospace;
    }
    
    .score-badge {
        display: inline-block;
        padding: 0.375rem 0.75rem;
        border-radius: 6px;
        font-size: 0.875rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-top: 0.75rem;
    }
    
    .badge-primary {
        background: #dbeafe;
        color: #1e3a8a;
    }
    
    .badge-secondary {
        background: #f3e8ff;
        color: #6b21a8;
    }
    
    /* Drag & Drop Zone */
    .upload-zone {
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 3rem 2rem;
        text-align: center;
        background: #f8fafc;
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .upload-zone:hover {
        border-color: #3b82f6;
        background: #eff6ff;
    }
    
    .upload-icon {
        font-size: 3rem;
        color: #3b82f6;
        margin-bottom: 1rem;
    }
    
    .upload-text {
        font-size: 1.125rem;
        color: #111827;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .upload-subtext {
        font-size: 0.875rem;
        color: #6b7280;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
        color: white;
        border: none;
        padding: 0.625rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9375rem;
        transition: all 0.2s;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    .stButton>button:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #d1d5db;
        padding: 0.625rem 1rem;
        font-size: 0.9375rem;
        transition: all 0.2s;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: white;
        padding: 0.5rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 0.9375rem;
        font-weight: 600;
        color: #6b7280;
        padding: 0.625rem 1.25rem;
        border-radius: 6px;
        transition: all 0.2s;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
        color: white;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #1e3a8a 100%);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #374151;
    }
    
    /* Icons */
    .icon {
        margin-right: 0.5rem;
    }
    
    /* Example Query Buttons */
    .example-btn {
        background: white;
        border: 1px solid #e5e7eb;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
        font-weight: 500;
        color: #374151;
    }
    
    .example-btn:hover {
        border-color: #3b82f6;
        background: #eff6ff;
        color: #1e3a8a;
    }
    
    /* Info Boxes */
    .info-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 1rem;
        color: #1e3a8a;
        font-size: 0.9375rem;
    }
    
    /* File Type Tags */
    .file-type {
        display: inline-block;
        background: white;
        border: 1px solid #e5e7eb;
        padding: 0.75rem 1.25rem;
        border-radius: 8px;
        font-weight: 500;
        color: #374151;
        transition: all 0.2s;
    }
    
    .file-type:hover {
        border-color: #3b82f6;
        background: #eff6ff;
    }
</style>
''', unsafe_allow_html=True)

# Session state
if 'api_url' not in st.session_state:
    st.session_state.api_url = 'http://127.0.0.1:8000'
if 'indexed_files' not in st.session_state:
    st.session_state.indexed_files = 0
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

# Header
st.markdown('''
<div class="app-header">
    <div class="app-title">NeuroDrive</div>
    <div class="app-subtitle">Enterprise Semantic Search Platform</div>
</div>
''', unsafe_allow_html=True)

# Settings
with st.expander('Settings & Configuration', expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        api_url = st.text_input('API Endpoint', value=st.session_state.api_url)
        st.session_state.api_url = api_url
    with col2:
        use_context = st.toggle('Enable Context Ranking', value=True)
    with col3:
        num_results = st.slider('Maximum Results', 1, 10, 5)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(['Search', 'Index Files', 'Analytics', 'History'])

# TAB 1: SEARCH
with tab1:
    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1])
    with col1:
        query = st.text_input(
            'Search Query',
            placeholder='Enter your search query (e.g., "machine learning research papers")',
            label_visibility='collapsed',
            key='search_query'
        )
    with col2:
        search_btn = st.button('Search', use_container_width=True, type='primary')
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Example Queries
    st.markdown('<p style="font-weight: 600; color: #374151; margin-bottom: 0.75rem;">Quick Search Examples</p>', unsafe_allow_html=True)
    cols = st.columns(4)
    examples = [
        'Machine Learning Research',
        'Financial Reports Q3',
        'Meeting Minutes 2024',
        'Technical Documentation'
    ]
    for col, ex in zip(cols, examples):
        if col.button(ex, use_container_width=True):
            st.session_state.search_query = ex
            st.rerun()
    
    if search_btn and query:
        with st.spinner('Processing search request...'):
            try:
                response = requests.post(
                    f'{api_url}/search/',
                    json={'query': query, 'k': num_results, 'use_context': use_context},
                    timeout=30
                )
                
                if response.status_code == 200:
                    results = response.json()
                    st.session_state.search_history.append({
                        'query': query,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'results': results['count']
                    })
                    
                    st.success(f'Found {results["count"]} matching documents')
                    
                    if results['count'] > 0:
                        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
                        for i, result in enumerate(results['results'], 1):
                            similarity = result.get('similarity_score', 0)
                            context = result.get('context_score', similarity)
                            
                            st.markdown(f'''
                            <div class="result-item">
                                <div class="result-header">
                                    <div class="result-rank">{i}</div>
                                    <div class="result-title">{result["name"]}</div>
                                </div>
                                <div class="result-path">{result["path"]}</div>
                                <span class="score-badge badge-primary">Similarity: {similarity:.1%}</span>
                                <span class="score-badge badge-secondary">Context Score: {context:.1%}</span>
                            </div>
                            ''', unsafe_allow_html=True)
                            
                            with st.expander('View Content Preview'):
                                st.text_area('', result.get('preview', 'No preview available'), height=120, label_visibility='collapsed')
                    else:
                        st.info('No documents match your query. Try different keywords or index more files.')
                else:
                    st.error(f'Search failed with status code {response.status_code}')
            except requests.exceptions.ConnectionError:
                st.error('Cannot connect to backend API. Please ensure the server is running.')
                st.code('cd backend/app && python -m uvicorn main:app --reload')
            except Exception as e:
                st.error(f'An error occurred: {str(e)}')

# TAB 2: INDEX FILES
with tab2:
    st.markdown('### Add Documents to Knowledge Base')
    
    # Traditional folder indexing
    st.markdown('#### Method 1: Index Folder')
    col1, col2 = st.columns([4, 1])
    with col1:
        folder_path = st.text_input(
            'Folder Path',
            placeholder='C:/Users/Username/Documents/MyFiles',
            help='Enter the complete path to the folder you want to index'
        )
    with col2:
        st.write('')
        index_btn = st.button('Start Indexing', use_container_width=True, type='primary')
    
    if index_btn and folder_path:
        progress = st.progress(0)
        status = st.empty()
        
        try:
            status.info('Step 1 of 3: Scanning directory...')
            progress.progress(33)
            time.sleep(0.3)
            
            response = requests.post(
                f'{api_url}/scan/',
                json={'folder_path': folder_path},
                timeout=120
            )
            
            status.info('Step 2 of 3: Extracting text content...')
            progress.progress(66)
            time.sleep(0.3)
            
            status.info('Step 3 of 3: Generating embeddings...')
            progress.progress(100)
            
            if response.status_code == 200:
                result = response.json()
                status.empty()
                progress.empty()
                
                st.success('Indexing completed successfully')
                
                col1, col2, col3 = st.columns(3)
                
                col1.markdown(f'''
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-file-alt"></i></div>
                    <div class="stat-number">{result.get('files_scanned', 0)}</div>
                    <div class="stat-label">Files Scanned</div>
                </div>
                ''', unsafe_allow_html=True)
                
                col2.markdown(f'''
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-check-circle"></i></div>
                    <div class="stat-number">{result.get('files_indexed', 0)}</div>
                    <div class="stat-label">Files Indexed</div>
                </div>
                ''', unsafe_allow_html=True)
                
                success_rate = (result.get('files_indexed', 0) / max(result.get('files_scanned', 1), 1)) * 100
                col3.markdown(f'''
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-percentage"></i></div>
                    <div class="stat-number">{success_rate:.0f}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                ''', unsafe_allow_html=True)
                
                st.session_state.indexed_files += result.get('files_indexed', 0)
            else:
                status.error('Indexing operation failed')
        except Exception as e:
            st.error(f'Error: {str(e)}')
        finally:
            progress.empty()
            status.empty()
    
    st.markdown('---')
    
    # File upload (drag & drop)
    st.markdown('#### Method 2: Upload Files')
    uploaded_files = st.file_uploader(
        'Drag and drop files here',
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help='Supported formats: PDF, DOCX, TXT'
    )
    
    if uploaded_files:
        st.markdown(f'<div class="info-box">Selected {len(uploaded_files)} file(s) for upload</div>', unsafe_allow_html=True)
        
        if st.button('Upload & Index Files', type='primary'):
            # Save files temporarily and index them
            temp_dir = 'temp_uploads'
            os.makedirs(temp_dir, exist_ok=True)
            
            for file in uploaded_files:
                file_path = os.path.join(temp_dir, file.name)
                with open(file_path, 'wb') as f:
                    f.write(file.getbuffer())
            
            # Index the temp directory
            try:
                response = requests.post(
                    f'{api_url}/scan/',
                    json={'folder_path': temp_dir},
                    timeout=120
                )
                if response.status_code == 200:
                    result = response.json()
                    st.success(f'Successfully indexed {result.get("files_indexed", 0)} files')
                else:
                    st.error('Upload failed')
            except Exception as e:
                st.error(f'Error: {str(e)}')
    
    st.markdown('---')
    st.markdown('### Supported Document Types')
    col1, col2, col3 = st.columns(3)
    col1.markdown('<div class="file-type">PDF Documents</div>', unsafe_allow_html=True)
    col2.markdown('<div class="file-type">Word Documents (DOCX)</div>', unsafe_allow_html=True)
    col3.markdown('<div class="file-type">Text Files (TXT)</div>', unsafe_allow_html=True)

# TAB 3: ANALYTICS
with tab3:
    st.markdown('### Knowledge Base Overview')
    
    if st.button('Refresh Analytics', use_container_width=True, type='primary'):
        try:
            response = requests.get(f'{api_url}/get_file/')
            if response.status_code == 200:
                data = response.json()
                files = data.get('files', [])
                total = data.get('total', 0)
                
                col1, col2, col3, col4 = st.columns(4)
                
                col1.markdown(f'''
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-database"></i></div>
                    <div class="stat-number">{total}</div>
                    <div class="stat-label">Total Documents</div>
                </div>
                ''', unsafe_allow_html=True)
                
                types = len(set(f.get('ext', '') for f in files))
                col2.markdown(f'''
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-file-alt"></i></div>
                    <div class="stat-number">{types}</div>
                    <div class="stat-label">File Types</div>
                </div>
                ''', unsafe_allow_html=True)
                
                total_size = sum(f.get('size', 0) for f in files)
                size_mb = total_size / (1024 * 1024)
                col3.markdown(f'''
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-hdd"></i></div>
                    <div class="stat-number">{size_mb:.1f}</div>
                    <div class="stat-label">Total Size (MB)</div>
                </div>
                ''', unsafe_allow_html=True)
                
                searches = len(st.session_state.search_history)
                col4.markdown(f'''
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-search"></i></div>
                    <div class="stat-number">{searches}</div>
                    <div class="stat-label">Total Searches</div>
                </div>
                ''', unsafe_allow_html=True)
                
                st.markdown('---')
                
                if files:
                    st.markdown('### Document Distribution by Type')
                    ext_counts = {}
                    for f in files:
                        ext = f.get('ext', 'unknown')
                        ext_counts[ext] = ext_counts.get(ext, 0) + 1
                    df = pd.DataFrame(list(ext_counts.items()), columns=['Type', 'Count'])
                    st.bar_chart(df.set_index('Type'))
                    
                    st.markdown('---')
                    st.markdown('### Indexed Documents')
                    df = pd.DataFrame(files)
                    df['Size (MB)'] = (df['size'] / (1024 * 1024)).round(2)
                    df = df[['name', 'ext', 'Size (MB)']]
                    df.columns = ['Document Name', 'Type', 'Size (MB)']
                    st.dataframe(df, use_container_width=True, height=400)
                else:
                    st.markdown('<div class="info-box">No documents indexed. Navigate to Index Files tab to begin.</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f'Error: {str(e)}')

# TAB 4: HISTORY
with tab4:
    st.markdown('### Search History')
    
    if st.session_state.search_history:
        for search in reversed(st.session_state.search_history[-15:]):
            st.markdown(f'''
            <div class="result-item">
                <div class="result-title">{search["query"]}</div>
                <div class="result-path">{search["timestamp"]} • {search["results"]} results found</div>
            </div>
            ''', unsafe_allow_html=True)
        
        if st.button('Clear History', type='secondary'):
            st.session_state.search_history = []
            st.rerun()
    else:
        st.markdown('<div class="info-box">No search history available. Execute searches to populate history.</div>', unsafe_allow_html=True)

# Footer
st.markdown('---')
st.markdown('''
<div style="text-align: center; color: #9ca3af; padding: 1.5rem 0;">
    <p style="font-size: 0.9375rem; font-weight: 600; color: #6b7280;">NeuroDrive - Enterprise Semantic Search</p>
    <p style="font-size: 0.8125rem;">Powered by FastAPI, Sentence Transformers, FAISS & Streamlit</p>
    <p style="font-size: 0.75rem; color: #9ca3af; margin-top: 0.5rem;">Development Team: Shashwat, Pavan, Shaunak, Manvi, Tanmay</p>
</div>
''', unsafe_allow_html=True)

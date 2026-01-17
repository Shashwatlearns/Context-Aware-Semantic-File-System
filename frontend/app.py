import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
import os
import tempfile
from pathlib import Path

st.set_page_config(
    page_title='NeuroDrive - Semantic File Search',
    page_icon='🧠',
    layout='wide',
    initial_sidebar_state='expanded'
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stButton>button {
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

if 'api_url' not in st.session_state:
    st.session_state.api_url = 'http://127.0.0.1:8000'
if 'indexed_files' not in st.session_state:
    st.session_state.indexed_files = 0
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'last_search_results' not in st.session_state:
    st.session_state.last_search_results = None
if 'indexing_job_id' not in st.session_state:
    st.session_state.indexing_job_id = None

def export_results_to_csv(results):
    if not results:
        return None
    data = []
    for r in results:
        data.append({
            'Rank': r['rank'],
            'File Name': r['name'],
            'Path': r['path'],
            'Score': r.get('hybrid_score') or r.get('similarity_score', 0),
            'Type': r['file_type'],
            'Method': r['search_method']
        })
    df = pd.DataFrame(data)
    return df.to_csv(index=False)

def check_indexing_progress(api_url, job_id):
    try:
        response = requests.get(f'{api_url}/scan/progress/{job_id}', timeout=3)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

with st.sidebar:
    st.title('Settings')
    
    api_url = st.text_input('API URL', value=st.session_state.api_url)
    st.session_state.api_url = api_url
    
    st.divider()
    
    st.subheader('Search Options')
    use_context = st.toggle('Context Ranking', value=True)
    use_hybrid = st.toggle('Hybrid Search', value=True)
    num_results = st.slider('Results', 1, 20, 5)
    min_score = st.slider('Min Score', 0.0, 1.0, 0.0, 0.05)
    
    st.divider()
    
    st.subheader('Quick Stats')
    if st.button('Refresh Stats'):
        try:
            response = requests.get(f'{api_url}/search/health')
            if response.status_code == 200:
                health = response.json()
                st.session_state.indexed_files = health.get('documents_indexed', 0)
        except:
            pass
    
    st.metric('Indexed Files', st.session_state.indexed_files)
    st.metric('Searches', len(st.session_state.search_history))
    
    if st.session_state.indexing_job_id:
        st.divider()
        st.subheader('Indexing Progress')
        progress_data = check_indexing_progress(api_url, st.session_state.indexing_job_id)
        
        if progress_data and progress_data.get('status') != 'not_found':
            status = progress_data.get('status', 'unknown')
            processed = progress_data.get('processed', 0)
            total = progress_data.get('total', 1)
            indexed = progress_data.get('indexed', 0)
            
            progress_pct = (processed / total) * 100 if total > 0 else 0
            
            st.progress(progress_pct / 100)
            st.write(f'**Status:** {status}')
            st.write(f'**Processed:** {processed}/{total}')
            st.write(f'**Indexed:** {indexed}')
            
            if status == 'completed':
                st.success('Indexing complete!')
                if st.button('Clear Progress'):
                    st.session_state.indexing_job_id = None
                    st.rerun()
            else:
                if st.button('Refresh Progress'):
                    st.rerun()

st.title('NeuroDrive v2.0')
st.caption('AI-Powered Semantic File Search System')

tab1, tab2, tab3, tab4 = st.tabs(['Search', 'Index Files', 'Analytics', 'System'])

with tab1:
    st.header('Search Your Files')
    
    query = st.text_input(
        'Search query',
        placeholder='e.g., machine learning, budget report',
    )
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_button = st.button('Search', type='primary', use_container_width=True)
    
    with col2:
        if st.session_state.last_search_results:
            if st.button('Export CSV', use_container_width=True):
                csv = export_results_to_csv(st.session_state.last_search_results.get('results', []))
                if csv:
                    st.download_button(
                        'Download',
                        csv,
                        file_name=f'search_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                        mime='text/csv'
                    )
    
    with col3:
        if st.button('Clear', use_container_width=True):
            st.session_state.last_search_results = None
            st.rerun()
    
    if search_button and query:
        with st.spinner('Searching...'):
            try:
                response = requests.post(
                    f'{api_url}/search/',
                    json={
                        'query': query,
                        'k': num_results,
                        'use_context': use_context,
                        'use_hybrid': use_hybrid,
                        'min_score': min_score
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    results = response.json()
                    st.session_state.last_search_results = results
                    
                    st.session_state.search_history.append({
                        'query': query,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'results': results['count'],
                        'method': results['search_method'],
                        'time_ms': results['processing_time_ms']
                    })
                    
                    method = results['search_method']
                    cache = 'CACHED' if results.get('cache_hit') else 'NEW'
                    time_ms = results['processing_time_ms']
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric('Results', results['count'])
                    with col2:
                        st.metric('Method', method.title())
                    with col3:
                        st.metric('Cache', cache)
                    with col4:
                        st.metric('Time', f'{time_ms:.0f}ms')
                    
                    st.divider()
                    
                    if results['count'] > 0:
                        for i, result in enumerate(results['results'], 1):
                            with st.expander(f"#{i} - {result['name']}", expanded=(i==1)):
                                st.write(f"**Path:** `{result['path']}`")
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    score = result.get('hybrid_score') or result.get('similarity_score', 0)
                                    st.metric('Score', f'{score:.1%}')
                                with col2:
                                    st.metric('Type', result['file_type'])
                                with col3:
                                    st.metric('Method', result.get('search_method', 'N/A'))
                                
                                if result.get('semantic_score') and result.get('bm25_score'):
                                    st.write('**Score Breakdown:**')
                                    st.write(f"- Semantic: {result['semantic_score']:.3f}")
                                    st.write(f"- Keyword (BM25): {result['bm25_score']:.3f}")
                                
                                st.write('**Preview:**')
                                preview = result.get('preview', 'No preview available')
                                
                                if result['file_type'] in ['.py', '.js', '.java', '.cpp']:
                                    st.code(preview, language='python')
                                else:
                                    st.text_area('', preview, height=150, key=f'preview_{i}', label_visibility='collapsed')
                    else:
                        st.warning('No results found.')
                else:
                    st.error(f'Error: {response.status_code}')
                    
            except Exception as e:
                st.error(f'Error: {str(e)}')
    
    elif st.session_state.last_search_results:
        results = st.session_state.last_search_results
        st.info(f'Showing {results["count"]} results from last search: "{results["query"]}"')

with tab2:
    st.header('Index New Files')
    
    index_tab1, index_tab2 = st.tabs(['Folder Path', 'Upload Files'])
    
    with index_tab1:
        st.info('Enter the full path to a folder on your computer')
        
        folder_path = st.text_input(
            'Folder Path',
            placeholder='C:/Users/YourName/Documents',
            key='folder_input'
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button('Documents', use_container_width=True):
                folder_path = str(os.path.expanduser('~/Documents'))
                st.rerun()
        with col2:
            if st.button('Desktop', use_container_width=True):
                folder_path = str(os.path.expanduser('~/Desktop'))
                st.rerun()
        with col3:
            if st.button('Downloads', use_container_width=True):
                folder_path = str(os.path.expanduser('~/Downloads'))
                st.rerun()
        
        if folder_path:
            st.code(folder_path, language=None)
        
        col1, col2 = st.columns(2)
        with col1:
            max_files = st.number_input('Max files to index', min_value=1, max_value=10000, value=1000)
        with col2:
            file_types = st.multiselect('File types', ['.pdf', '.docx', '.txt'], default=['.pdf', '.docx', '.txt'])
        
        if st.button('Start Indexing', type='primary', use_container_width=True):
            if folder_path:
                with st.spinner('Starting indexing...'):
                    try:
                        response = requests.post(
                            f'{api_url}/scan/',
                            json={
                                'folder_path': folder_path,
                                'max_files': max_files,
                                'file_types': file_types
                            },
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.indexing_job_id = result['job_id']
                            st.success('Indexing started!')
                            st.info(f'Job ID: {result["job_id"]}')
                            st.info(f'Files to process: {result["files_to_process"]}')
                            st.info(f'Estimated time: ~{result["estimated_time_seconds"]:.0f}s')
                            st.info('Check progress in the sidebar!')
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f'Error: {response.status_code}')
                    except Exception as e:
                        st.error(f'Error: {str(e)}')
            else:
                st.warning('Please enter a folder path')
    
    with index_tab2:
        st.info('Drag and drop files here to index them instantly')
        
        uploaded_files = st.file_uploader(
            'Choose files',
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True,
        )
        
        if uploaded_files:
            st.success(f'{len(uploaded_files)} file(s) ready to index')
            
            for i, file in enumerate(uploaded_files, 1):
                st.write(f'{i}. {file.name} ({file.size / 1024:.1f} KB)')
            
            if st.button('Index These Files', type='primary', use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        status_text.text('Saving files...')
                        for i, uploaded_file in enumerate(uploaded_files):
                            file_path = Path(temp_dir) / uploaded_file.name
                            with open(file_path, 'wb') as f:
                                f.write(uploaded_file.getbuffer())
                            progress_bar.progress((i + 1) / (len(uploaded_files) * 2))
                        
                        status_text.text('Creating embeddings...')
                        response = requests.post(
                            f'{api_url}/scan/sync',
                            json={'folder_path': temp_dir},
                            timeout=300
                        )
                        
                        progress_bar.progress(1.0)
                        
                        if response.status_code == 200:
                            result = response.json()
                            status_text.empty()
                            progress_bar.empty()
                            
                            st.success(f'Successfully indexed {result["files_indexed"]} files!')
                            st.balloons()
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric('Scanned', result['files_scanned'])
                            with col2:
                                st.metric('Indexed', result['files_indexed'])
                        else:
                            st.error(f'Error: {response.status_code}')
                
                except Exception as e:
                    st.error(f'Error: {str(e)}')
                finally:
                    progress_bar.empty()
                    status_text.empty()

with tab3:
    st.header('Search Analytics')
    
    if st.session_state.search_history:
        df = pd.DataFrame(st.session_state.search_history)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric('Total Searches', len(df))
        with col2:
            avg_results = df['results'].mean()
            st.metric('Avg Results', f'{avg_results:.1f}')
        with col3:
            avg_time = df['time_ms'].mean()
            st.metric('Avg Time', f'{avg_time:.0f}ms')
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader('Search Results Distribution')
            st.bar_chart(df['results'].value_counts().sort_index())
        
        with col2:
            st.subheader('Response Time Trend')
            st.line_chart(df['time_ms'])
        
        st.divider()
        
        st.subheader('Recent Searches')
        display_df = df[['timestamp', 'query', 'results', 'method', 'time_ms']].tail(10)
        st.dataframe(display_df, use_container_width=True)
        
        if st.button('Download Search History'):
            csv = df.to_csv(index=False)
            st.download_button(
                'Download CSV',
                csv,
                file_name=f'search_history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv'
            )
        
        if st.button('Clear History'):
            st.session_state.search_history = []
            st.rerun()
    else:
        st.info('No search history yet. Perform some searches to see analytics!')

with tab4:
    st.header('System Status')
    
    if st.button('Refresh All', use_container_width=True):
        st.rerun()
    
    try:
        health = requests.get(f'{api_url}/search/health', timeout=5).json()
        cache_stats = requests.get(f'{api_url}/search/cache/stats', timeout=5).json()
        
        st.subheader('Health Status')
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            docs = health.get('documents_indexed', 0)
            st.metric('Documents', docs)
        
        with col2:
            hybrid = 'Active' if health.get('hybrid_search_available') else 'Off'
            st.metric('Hybrid', hybrid)
        
        with col3:
            cache_enabled = 'Active' if health.get('caching_available') else 'Off'
            st.metric('Cache', cache_enabled)
        
        with col4:
            status = 'Healthy' if health.get('status') == 'healthy' else 'Error'
            st.metric('Status', status)
        
        st.divider()
        
        st.subheader('Cache Performance')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write('**Result Cache:**')
            rc = cache_stats.get('result_cache', {})
            st.metric('Hit Rate', rc.get('hit_rate', '0%'))
            st.write(f"- Hits: {rc.get('hits', 0)}")
            st.write(f"- Misses: {rc.get('misses', 0)}")
            st.write(f"- Evictions: {rc.get('evictions', 0)}")
            st.write(f"- Size: {rc.get('size', 0)}/{rc.get('max_size', 0)}")
        
        with col2:
            st.write('**Embedding Cache:**')
            ec = cache_stats.get('embedding_cache', {})
            st.metric('Hit Rate', ec.get('hit_rate', '0%'))
            st.write(f"- Hits: {ec.get('hits', 0)}")
            st.write(f"- Misses: {ec.get('misses', 0)}")
            st.write(f"- Evictions: {ec.get('evictions', 0)}")
            st.write(f"- Size: {ec.get('size', 0)}/{ec.get('max_size', 0)}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button('Clear Cache', use_container_width=True):
                try:
                    requests.post(f'{api_url}/search/cache/clear')
                    st.success('Cache cleared!')
                    time.sleep(0.5)
                    st.rerun()
                except:
                    st.error('Failed to clear cache')
        
        
        
        st.divider()
        st.subheader('Database Management')
        
        if st.button('Clear All Indexed Files', type='secondary', use_container_width=True):
            st.warning('WARNING: This will permanently delete ALL indexed files from the database!')
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button('Cancel Operation'):
                    st.rerun()
            with col_b:
                if st.button('YES - DELETE ALL', type='primary'):
                    try:
                        response = requests.delete(f'{api_url}/search/database/clear', timeout=10)
                        if response.status_code == 200:
                            st.success('Database cleared successfully!')
                            st.session_state.indexed_files = 0
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f'Failed: {response.status_code}')
                    except Exception as e:
                        st.error(f'Error: {str(e)}')

        st.divider()
        
        with st.expander('Raw Health Data'):
            st.json(health)
        
        with st.expander('Raw Cache Data'):
            st.json(cache_stats)
    
    except Exception as e:
        st.error('Cannot connect to backend')
        st.code(str(e))

st.divider()
st.caption('NeuroDrive v2.0 - AI-Powered Semantic File Search | Hybrid Search | Caching | Analytics')





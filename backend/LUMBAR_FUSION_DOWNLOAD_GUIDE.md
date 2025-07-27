# Lumbar Fusion Paper Download Guide

## Overview
This guide explains how to use the PubMed lumbar fusion paper download system that has been implemented for the SpinalSurgery Research Platform.

## Features Implemented

1. **Automated PubMed Search & Download**
   - Search for posterolateral lumbar fusion papers
   - Sort by date (most recent first)
   - Download metadata and PDFs (when available)
   - Automatic Korean translation

2. **Database Integration**
   - Papers are saved to the ResearchPaper model
   - Prevents duplicate downloads
   - Tracks fusion type and study type

3. **File Organization**
   - Papers stored in: `/home/drjang00/DevEnvironments/spinalsurgery-research/research_papers/lumbar_fusion_2025/`
   - Each paper gets its own folder with:
     - `metadata.json` - Complete paper information
     - `summary.txt` - English summary with Korean translation
     - `korean_summary.txt` - Korean-only summary
     - `{PMID}.pdf` - PDF file (if available)

4. **API Endpoints**
   - `GET /api/v1/lumbar-fusion/lumbar-fusion-papers` - List papers with filtering
   - `GET /api/v1/lumbar-fusion/lumbar-fusion-papers/{paper_id}` - Get paper details
   - `GET /api/v1/lumbar-fusion/lumbar-fusion-papers/{paper_id}/korean-summary` - Get Korean summary
   - `GET /api/v1/lumbar-fusion/lumbar-fusion-papers/stats/overview` - Get statistics

## Usage Instructions

### 1. Download Papers from PubMed

Run the main download script:

```bash
cd /home/drjang00/DevEnvironments/spinalsurgery-research/backend
python scripts/download_lumbar_fusion_papers.py
```

This will:
- Search PubMed for the latest 10 posterolateral lumbar fusion papers
- Download metadata and PDFs
- Translate to Korean
- Save to database

### 2. Test the System

Run the test script:

```bash
cd /home/drjang00/DevEnvironments/spinalsurgery-research/backend
python test_lumbar_fusion_download.py
```

This will download 2 papers as a test.

### 3. Access Papers via API

With the backend running, you can access papers through the API:

```bash
# Get all papers
curl -X GET "http://localhost:8000/api/v1/lumbar-fusion/lumbar-fusion-papers" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get specific paper
curl -X GET "http://localhost:8000/api/v1/lumbar-fusion/lumbar-fusion-papers/PMID_HERE" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get statistics
curl -X GET "http://localhost:8000/api/v1/lumbar-fusion/lumbar-fusion-papers/stats/overview" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Filter Papers

The API supports filtering:

```bash
# Filter by fusion type
curl -X GET "http://localhost:8000/api/v1/lumbar-fusion/lumbar-fusion-papers?fusion_type=PLF" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by year
curl -X GET "http://localhost:8000/api/v1/lumbar-fusion/lumbar-fusion-papers?year=2024" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Search in title/abstract
curl -X GET "http://localhost:8000/api/v1/lumbar-fusion/lumbar-fusion-papers?search=minimally%20invasive" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Customization

### Modify Search Query

Edit the search query in `scripts/download_lumbar_fusion_papers.py`:

```python
search_query = '("posterolateral lumbar fusion"[Title/Abstract] OR "lumbar posterolateral fusion"[Title/Abstract] OR "PLF"[Title/Abstract] AND "lumbar"[Title/Abstract]) AND ("2020"[PDAT] : "2025"[PDAT])'
```

### Change Number of Papers

Modify the `max_results` parameter:

```python
results = await downloader.search_and_download_papers(
    query=search_query,
    max_results=10,  # Change this number
    translate_to_korean=True,
    save_to_database=True
)
```

### Add PubMed API Key

For better performance, add your PubMed API key:

```bash
export PUBMED_API_KEY="your_api_key_here"
```

## Troubleshooting

1. **No papers found**: Check your internet connection and PubMed availability
2. **Translation errors**: The Google Translate API may have rate limits
3. **PDF download failures**: Many papers don't have free PDFs available
4. **Database errors**: Ensure the database is running and migrations are applied

## Future Enhancements

1. Add more paper sources (Sci-Hub, institutional access)
2. Implement batch download scheduling
3. Add AI-powered paper summarization
4. Create frontend interface for paper management
5. Add citation tracking and analysis
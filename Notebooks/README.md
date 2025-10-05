# LegalAI Data Processing Notebooks

This directory contains Jupyter notebooks and scripts used for data processing, document analysis, and AI model development for the LegalAI system. These notebooks handle the extraction, preprocessing, and indexing of legal documents from Sri Lankan legal sources.

## Contents

### Data Acquisition and Preprocessing

#### Acts and Bills Processing

- **[dp-1-download-pdf-acts-bills.ipynb](dp-1-download-pdf-acts-bills.ipynb)**: Downloads PDF documents for acts and bills from legal sources
- **[dp-1-preprocess bills.ipynb](dp-1-preprocess%20bills.ipynb)**: Preprocesses bill documents for text extraction and analysis
- **[acts-batch-ocr.ipynb](acts-batch-ocr.ipynb)**: Batch OCR processing for scanned act documents
- **[dsep-acts-sinhala-extraction.ipynb](dsep-acts-sinhala-extraction.ipynb)**: Extracts and processes Sinhala language legal acts for the system

#### Gazette Processing

- **[dp-1-preprocess gazettes.ipynb](dp-1-preprocess%20gazettes.ipynb)**: Preprocesses gazette documents and extracts relevant legal information

#### Constitution Processing

- **[constitution_preprocessing_for_RAG.ipynb](constitution_preprocessing_for_RAG.ipynb)**: Preprocesses Sri Lankan constitution text for RAG (Retrieval-Augmented Generation) systems

### Data Validation and Analysis

- **[dp-1-check-data.ipynb](dp-1-check-data.ipynb)**: Validates and analyzes processed data quality
- **[dp-1-check-files.ipynb](dp-1-check-files.ipynb)**: File system checks and data integrity validation

### Vector Search and Indexing

- **[dp-2-faiss.ipynb](dp-2-faiss.ipynb)**: FAISS vector database implementation for document similarity search

### Metadata Processing

- **[dp-3-metadata-1.ipynb](dp-3-metadata-1.ipynb)**: Initial metadata extraction and processing
- **[dp-3-metadata-2.ipynb](dp-3-metadata-2.ipynb)**: Advanced metadata analysis and enrichment
- **[dp-3-metadata-3.ipynb](dp-3-metadata-3.ipynb)**: Metadata validation and final processing

### AI and RAG Development

- **[dsep-rag-comparison.ipynb](dsep-rag-comparison.ipynb)**: Comparative analysis of different RAG (Retrieval-Augmented Generation) approaches
- **[langChain_approach.ipynb](langChain_approach.ipynb)**: Implementation using LangChain framework for document processing

### Utility Scripts

- **[extractor6.py](extractor6.py)**: Python script for document extraction and processing utilities

## Prerequisites

To run these notebooks, you need:

- **Python 3.8+**
- **Jupyter Notebook** or **JupyterLab**
- **Required packages**: pandas, numpy, faiss-cpu, transformers, beautifulsoup4, requests, etc.

Install dependencies:

```bash
pip install jupyter pandas numpy faiss-cpu transformers beautifulsoup4 requests
```

## Usage

1. **Start Jupyter**:

   ```bash
   jupyter notebook
   # or
   jupyter lab
   ```

2. **Navigate to Notebooks directory** and open desired notebook

3. **Run cells sequentially** - most notebooks have dependencies on previous processing steps

## Data Flow

The notebooks follow a sequential data processing pipeline:

1. **Data Acquisition** → Download and collect legal documents
2. **Preprocessing** → OCR, text extraction, and cleaning
3. **Validation** → Data quality checks and integrity validation
4. **Indexing** → FAISS vector database creation
5. **Metadata** → Enhanced metadata extraction and processing
6. **AI Integration** → RAG system development and testing

## Output Data

Processed data is typically stored in:

- `../Backend/database/` - Database files and schemas
- `../docs/` - Fine-tuning datasets
- Vector indices and processed documents

## Contributing

When adding new notebooks:

1. Follow naming convention: `dp-<phase>-<description>.ipynb`
2. Include comprehensive documentation in notebook markdown cells
3. Add dependencies and setup instructions
4. Update this README with new entries
5. Ensure notebooks can run independently (or document dependencies)

## Related Documentation

- [Main Project README](../README.md): Project overview
- [Backend README](../Backend/README.md): How processed data is used in the API
- [Software Architecture Document](../docs/Software%20Architecture%20Document.pdf): Technical implementation details

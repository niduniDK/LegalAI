from .query_processor import retrieve_doc

def get_pdfs(query: str, top_k: int = 10):
    content, filenames = retrieve_doc(query, top_k)
    pdf_urls = []

    for filename in filenames:
        name_split = filename.split('.')[0]
        name = name_split[:-7].replace("-", "/")
        year = name_split[-7:]
        url = f"https://documents.gov.lk/view/bills/{name}{year}.pdf"
        pdf_urls.append(url)

    return pdf_urls
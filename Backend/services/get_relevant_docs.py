from .query_processor import retrieve_doc

def get_pdfs(query: str, top_k: int = 10):
    print(f"\n> GET_PDFS: Processing query: '{query}' with top_k={top_k}")
    content, filenames = retrieve_doc(query, top_k)
    pdf_urls = []

    print(f"\n> Retrieved {len(filenames)} document filenames")
    print(f"Filenames: {filenames}")

    for filename in filenames:
        name_split = filename.split('.')[0]
        name = name_split[:-7].replace("-", "/")
        year = name_split[-7:]
        url = f"https://documents.gov.lk/view/bills/{name}{year}.pdf"
        pdf_urls.append(url)
        print(f"Generated URL for {filename}: {url}")

    # print(f"Generated {len(pdf_urls)} PDF URLs")
    return pdf_urls
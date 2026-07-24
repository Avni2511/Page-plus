import re
from bs4 import BeautifulSoup

def parse_html_report(html_content):
    """
    Parses HTML content and extracts required webpage metrics:
    - title
    - meta_description
    - h1_count
    - images_missing_alt
    - word_count
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. Extract Title
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else "Not available"
    if not title:
        title = "Not available"

    # 2. Extract Meta Description
    # Handle name="description" and name="Description" case-insensitively
    meta_desc_tag = soup.find('meta', attrs={'name': re.compile(r'^description$', re.IGNORECASE)})
    meta_description = "Not available"
    if meta_desc_tag:
        meta_description = meta_desc_tag.get('content', '').strip()
        if not meta_description:
            meta_description = "Not available"
            
    # 3. Count H1 tags
    h1_count = len(soup.find_all('h1'))
    
    # 4. Count Images Missing Alt attribute or containing empty/whitespace alt attribute
    images = soup.find_all('img')
    images_missing_alt = 0
    for img in images:
        alt = img.get('alt')
        if alt is None or alt.strip() == '':
            images_missing_alt += 1
            
    # 5. Approximate visible word count
    # Clone the soup to avoid modifying the original when removing script/style tags
    clean_soup = BeautifulSoup(html_content, 'html.parser')
    for tag in clean_soup(['script', 'style', 'noscript', 'header', 'footer', 'nav']):
        tag.decompose()
        
    # Get all text
    visible_text = clean_soup.get_text(separator=' ')
    # Clean up whitespace and split into words
    words = re.findall(r'\b\w+\b', visible_text)
    word_count = len(words)
    
    return {
        "title": title,
        "meta_description": meta_description,
        "h1_count": h1_count,
        "images_missing_alt": images_missing_alt,
        "word_count": word_count
    }

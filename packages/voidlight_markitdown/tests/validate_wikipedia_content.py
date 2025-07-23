"""
Wikipedia Content Validation

Validates the quality and accuracy of Wikipedia content extraction.
"""

import difflib
import json
import re
from typing import Dict, List, Optional, Tuple
from urllib.request import urlopen, Request
from urllib.parse import quote, unquote

from bs4 import BeautifulSoup
from voidlight_markitdown import VoidLightMarkItDown


class WikipediaContentValidator:
    """Validate Wikipedia content extraction quality"""
    
    def __init__(self):
        self.md = VoidLightMarkItDown()
        self.validation_results = []
    
    def fetch_wikipedia_api_content(self, article_title: str, lang: str = 'en') -> Dict:
        """Fetch article content using Wikipedia API for comparison"""
        
        # Use Wikipedia API to get clean text
        api_url = f"https://{lang}.wikipedia.org/w/api.php"
        params = {
            'action': 'query',
            'format': 'json',
            'titles': article_title,
            'prop': 'extracts|info|categories',
            'exintro': 0,
            'explaintext': 1,
            'inprop': 'url'
        }
        
        query_string = '&'.join([f"{k}={quote(str(v))}" for k, v in params.items()])
        url = f"{api_url}?{query_string}"
        
        req = Request(url, headers={'User-Agent': 'VoidlightMarkitdown/1.0'})
        
        try:
            with urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                pages = data['query']['pages']
                page_id = list(pages.keys())[0]
                
                if page_id == '-1':
                    return {'error': 'Page not found'}
                
                page_data = pages[page_id]
                return {
                    'title': page_data.get('title', ''),
                    'extract': page_data.get('extract', ''),
                    'url': page_data.get('fullurl', ''),
                    'categories': [cat['title'] for cat in page_data.get('categories', [])]
                }
        except Exception as e:
            return {'error': str(e)}
    
    def extract_infobox_data(self, html_content: str) -> Dict:
        """Extract infobox data from Wikipedia HTML"""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        infobox = soup.find('table', {'class': 'infobox'})
        
        if not infobox:
            return {}
        
        data = {}
        for row in infobox.find_all('tr'):
            header = row.find('th')
            value = row.find('td')
            
            if header and value:
                key = header.get_text(strip=True)
                val = value.get_text(strip=True)
                data[key] = val
        
        return data
    
    def validate_content_structure(self, markdown: str, url: str) -> Dict:
        """Validate the structure of extracted content"""
        
        lines = markdown.split('\n')
        
        # Structure validation
        validation = {
            'has_title': False,
            'has_sections': False,
            'section_hierarchy_valid': True,
            'has_content': len(markdown.strip()) > 0,
            'line_count': len(lines),
            'char_count': len(markdown),
            'issues': []
        }
        
        # Check title
        if lines and lines[0].startswith('# '):
            validation['has_title'] = True
        else:
            validation['issues'].append('Missing main title')
        
        # Check sections
        headers = [line for line in lines if line.strip().startswith('#')]
        validation['has_sections'] = len(headers) > 1
        validation['section_count'] = len(headers)
        
        # Validate header hierarchy
        prev_level = 0
        for header in headers:
            level = len(header.split()[0])
            if level > prev_level + 1:
                validation['section_hierarchy_valid'] = False
                validation['issues'].append(f'Invalid header hierarchy jump: {header}')
            prev_level = level
        
        # Check for common Wikipedia elements
        validation['has_links'] = '](http' in markdown or '](/' in markdown
        validation['has_references'] = '[^' in markdown or '[[' in markdown
        validation['has_lists'] = any(line.strip().startswith(('- ', '* ', '1.')) for line in lines)
        
        # Tables
        validation['has_tables'] = '|' in markdown and '---' in markdown
        
        return validation
    
    def validate_unicode_preservation(self, markdown: str, language: str) -> Dict:
        """Validate Unicode character preservation for different languages"""
        
        validations = {
            'korean': {
                'has_hangul': bool(re.search(r'[\uac00-\ud7af]', markdown)),
                'has_hanja': bool(re.search(r'[\u4e00-\u9fff]', markdown)),
                'pattern': r'[\uac00-\ud7af\u4e00-\u9fff]'
            },
            'japanese': {
                'has_hiragana': bool(re.search(r'[\u3040-\u309f]', markdown)),
                'has_katakana': bool(re.search(r'[\u30a0-\u30ff]', markdown)),
                'has_kanji': bool(re.search(r'[\u4e00-\u9fff]', markdown)),
                'pattern': r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]'
            },
            'chinese': {
                'has_chinese': bool(re.search(r'[\u4e00-\u9fff]', markdown)),
                'pattern': r'[\u4e00-\u9fff]'
            },
            'arabic': {
                'has_arabic': bool(re.search(r'[\u0600-\u06ff]', markdown)),
                'pattern': r'[\u0600-\u06ff]'
            },
            'hebrew': {
                'has_hebrew': bool(re.search(r'[\u0590-\u05ff]', markdown)),
                'pattern': r'[\u0590-\u05ff]'
            },
            'russian': {
                'has_cyrillic': bool(re.search(r'[\u0400-\u04ff]', markdown)),
                'pattern': r'[\u0400-\u04ff]'
            }
        }
        
        if language in validations:
            result = validations[language].copy()
            pattern = result.pop('pattern')
            
            # Count occurrences
            matches = re.findall(pattern, markdown)
            result['character_count'] = len(matches)
            result['unique_characters'] = len(set(matches))
            
            return result
        
        return {'language_not_configured': language}
    
    def validate_table_extraction(self, original_html: str, markdown: str) -> Dict:
        """Validate table extraction accuracy"""
        
        soup = BeautifulSoup(original_html, 'html.parser')
        html_tables = soup.find_all('table', {'class': 'wikitable'})
        
        # Count markdown tables (simple detection)
        markdown_tables = re.findall(r'\|.*\|.*\n\|[-:\s|]+\|', markdown)
        
        validation = {
            'html_table_count': len(html_tables),
            'markdown_table_count': len(markdown_tables),
            'extraction_rate': len(markdown_tables) / len(html_tables) if html_tables else 0,
            'tables_found': []
        }
        
        # Check each HTML table
        for i, table in enumerate(html_tables):
            # Get table headers
            headers = []
            header_row = table.find('tr')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            
            # Check if headers appear in markdown
            headers_found = sum(1 for h in headers if h in markdown)
            
            validation['tables_found'].append({
                'table_index': i,
                'headers': headers,
                'headers_found_in_markdown': headers_found,
                'header_coverage': headers_found / len(headers) if headers else 0
            })
        
        return validation
    
    def validate_reference_preservation(self, original_html: str, markdown: str) -> Dict:
        """Validate reference and citation preservation"""
        
        soup = BeautifulSoup(original_html, 'html.parser')
        
        # Count references in HTML
        html_refs = soup.find_all('sup', {'class': 'reference'})
        html_ref_count = len(html_refs)
        
        # Count references in markdown (various formats)
        md_ref_patterns = [
            r'\[\^\d+\]',  # Footnote style
            r'\[\d+\]',    # Numbered reference
            r'\[.*?\]\(#cite.*?\)',  # Link to citation
        ]
        
        md_ref_count = 0
        for pattern in md_ref_patterns:
            md_ref_count += len(re.findall(pattern, markdown))
        
        return {
            'html_reference_count': html_ref_count,
            'markdown_reference_count': md_ref_count,
            'preservation_rate': md_ref_count / html_ref_count if html_ref_count > 0 else 0,
            'reference_styles_found': {
                'footnote': bool(re.search(r'\[\^\d+\]', markdown)),
                'numbered': bool(re.search(r'\[\d+\]', markdown)),
                'linked': bool(re.search(r'\[.*?\]\(#cite.*?\)', markdown))
            }
        }
    
    def compare_with_api(self, url: str, markdown: str) -> Dict:
        """Compare extracted content with Wikipedia API"""
        
        # Extract article title from URL
        match = re.search(r'wikipedia\.org/wiki/(.+?)(?:\?|#|$)', url)
        if not match:
            return {'error': 'Could not extract article title from URL'}
        
        article_title = unquote(match.group(1).replace('_', ' '))
        
        # Detect language
        lang_match = re.search(r'https?://([a-z]{2,3})\.wikipedia\.org', url)
        lang = lang_match.group(1) if lang_match else 'en'
        
        # Get API content
        api_data = self.fetch_wikipedia_api_content(article_title, lang)
        
        if 'error' in api_data:
            return api_data
        
        # Compare content
        api_text = api_data.get('extract', '')
        
        # Simple similarity check (first 1000 chars)
        api_preview = api_text[:1000].lower()
        md_preview = re.sub(r'[#\*\-\[\]()]', '', markdown[:1000]).lower()
        
        similarity = difflib.SequenceMatcher(None, api_preview, md_preview).ratio()
        
        return {
            'title_match': api_data['title'].lower() in markdown.lower(),
            'content_similarity': similarity,
            'api_length': len(api_text),
            'markdown_length': len(markdown),
            'length_ratio': len(markdown) / len(api_text) if api_text else 0,
            'categories_found': sum(1 for cat in api_data.get('categories', []) if cat in markdown)
        }
    
    def validate_url(self, url: str) -> Dict:
        """Comprehensive validation of a Wikipedia URL"""
        
        print(f"Validating: {url}")
        
        try:
            # Fetch original HTML
            headers = {'User-Agent': 'VoidlightMarkitdown/1.0'}
            req = Request(url, headers=headers)
            
            with urlopen(req) as response:
                html_content = response.read()
            
            # Convert using markitdown
            import io
            content_stream = io.BytesIO(html_content)
            stream_info = StreamInfo(url=url)
            result = self.md.convert_stream(content_stream, stream_info=stream_info)
            markdown = result.markdown
            
            # Detect language from URL
            lang_match = re.search(r'https?://([a-z]{2,3})\.wikipedia\.org', url)
            language = lang_match.group(1) if lang_match else 'en'
            
            # Run all validations
            validation_result = {
                'url': url,
                'language': language,
                'conversion_success': bool(markdown),
                'title': result.title,
                'validations': {
                    'structure': self.validate_content_structure(markdown, url),
                    'unicode': self.validate_unicode_preservation(markdown, 
                                                                language if language in ['korean', 'japanese', 'chinese', 'arabic', 'hebrew', 'russian'] 
                                                                else 'english'),
                    'tables': self.validate_table_extraction(html_content.decode('utf-8'), markdown),
                    'references': self.validate_reference_preservation(html_content.decode('utf-8'), markdown),
                    'api_comparison': self.compare_with_api(url, markdown)
                }
            }
            
            # Calculate overall score
            scores = []
            
            # Structure score
            struct = validation_result['validations']['structure']
            struct_score = sum([
                struct['has_title'] * 20,
                struct['has_sections'] * 20,
                struct['section_hierarchy_valid'] * 20,
                struct['has_links'] * 10,
                struct['has_lists'] * 10,
                min(struct['section_count'] / 5, 1) * 20
            ])
            scores.append(struct_score)
            
            # Table score
            table_val = validation_result['validations']['tables']
            table_score = table_val['extraction_rate'] * 100 if table_val['html_table_count'] > 0 else 100
            scores.append(table_score)
            
            # Reference score
            ref_val = validation_result['validations']['references']
            ref_score = ref_val['preservation_rate'] * 100 if ref_val['html_reference_count'] > 0 else 100
            scores.append(ref_score)
            
            # API comparison score
            api_val = validation_result['validations']['api_comparison']
            if 'content_similarity' in api_val:
                api_score = api_val['content_similarity'] * 100
                scores.append(api_score)
            
            validation_result['overall_score'] = sum(scores) / len(scores)
            
            return validation_result
            
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'conversion_success': False
            }
    
    def generate_validation_report(self, results: List[Dict]) -> str:
        """Generate a comprehensive validation report"""
        
        report = """# Wikipedia Content Validation Report

## Summary

"""
        
        successful = [r for r in results if r.get('conversion_success', False)]
        failed = [r for r in results if not r.get('conversion_success', False)]
        
        report += f"- Total URLs tested: {len(results)}\n"
        report += f"- Successful conversions: {len(successful)}\n"
        report += f"- Failed conversions: {len(failed)}\n"
        
        if successful:
            avg_score = sum(r.get('overall_score', 0) for r in successful) / len(successful)
            report += f"- Average quality score: {avg_score:.1f}%\n"
        
        # Language breakdown
        report += "\n## By Language\n\n"
        
        languages = {}
        for result in successful:
            lang = result.get('language', 'unknown')
            if lang not in languages:
                languages[lang] = []
            languages[lang].append(result)
        
        for lang, lang_results in languages.items():
            avg_score = sum(r.get('overall_score', 0) for r in lang_results) / len(lang_results)
            report += f"### {lang.upper()}\n"
            report += f"- Articles tested: {len(lang_results)}\n"
            report += f"- Average score: {avg_score:.1f}%\n\n"
        
        # Detailed results
        report += "## Detailed Results\n\n"
        
        for result in results:
            report += f"### {result['url']}\n\n"
            
            if result.get('conversion_success'):
                report += f"- **Title**: {result.get('title', 'N/A')}\n"
                report += f"- **Overall Score**: {result.get('overall_score', 0):.1f}%\n"
                report += f"- **Language**: {result.get('language', 'unknown')}\n\n"
                
                if 'validations' in result:
                    # Structure validation
                    struct = result['validations']['structure']
                    report += "**Structure Validation:**\n"
                    report += f"- Has title: {'✅' if struct['has_title'] else '❌'}\n"
                    report += f"- Has sections: {'✅' if struct['has_sections'] else '❌'}\n"
                    report += f"- Section count: {struct.get('section_count', 0)}\n"
                    report += f"- Character count: {struct.get('char_count', 0):,}\n"
                    
                    if struct.get('issues'):
                        report += f"- Issues: {', '.join(struct['issues'])}\n"
                    
                    report += "\n"
                    
                    # Table validation
                    table_val = result['validations']['tables']
                    if table_val['html_table_count'] > 0:
                        report += "**Table Extraction:**\n"
                        report += f"- HTML tables: {table_val['html_table_count']}\n"
                        report += f"- Markdown tables: {table_val['markdown_table_count']}\n"
                        report += f"- Extraction rate: {table_val['extraction_rate']:.1%}\n\n"
                    
                    # Unicode validation
                    unicode_val = result['validations']['unicode']
                    if not unicode_val.get('language_not_configured'):
                        report += "**Unicode Preservation:**\n"
                        for key, value in unicode_val.items():
                            if key.startswith('has_'):
                                report += f"- {key}: {'✅' if value else '❌'}\n"
                        if 'character_count' in unicode_val:
                            report += f"- Character count: {unicode_val['character_count']:,}\n"
                        report += "\n"
            else:
                report += f"- **Error**: {result.get('error', 'Unknown error')}\n\n"
        
        return report


def main():
    """Run content validation tests"""
    
    validator = WikipediaContentValidator()
    
    # Test URLs covering different scenarios
    test_urls = [
        # English
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)",
        
        # Korean
        "https://ko.wikipedia.org/wiki/인공지능",
        "https://ko.wikipedia.org/wiki/한글",
        
        # Other languages
        "https://ja.wikipedia.org/wiki/人工知能",
        "https://ar.wikipedia.org/wiki/الذكاء_الاصطناعي",
        "https://he.wikipedia.org/wiki/בינה_מלאכותית",
        
        # Special cases
        "https://en.wikipedia.org/wiki/Mathematics",  # Math formulas
        "https://en.wikipedia.org/wiki/Python_(programming_language)",  # Code examples
    ]
    
    results = []
    
    for url in test_urls:
        result = validator.validate_url(url)
        results.append(result)
        
        # Save individual result
        print(f"Completed: {url} - Score: {result.get('overall_score', 0):.1f}%")
    
    # Generate report
    report = validator.generate_validation_report(results)
    
    # Save results
    json_path = "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/tests/wikipedia_validation_results.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    report_path = "/Users/voidlight/voidlight_markitdown/packages/voidlight_markitdown/tests/wikipedia_validation_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nValidation complete!")
    print(f"Results: {json_path}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
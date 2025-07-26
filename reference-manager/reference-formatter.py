#!/usr/bin/env python3
"""
참고문헌 포맷터 - Vancouver, APA, AMA 스타일 지원
"""

import re
from typing import Dict, List

class ReferenceFormatter:
    def __init__(self):
        self.styles = {
            'vancouver': self.format_vancouver,
            'apa': self.format_apa,
            'ama': self.format_ama
        }
    
    def format_reference(self, ref_data: Dict, style: str = 'vancouver') -> str:
        """참고문헌을 지정된 스타일로 포맷"""
        formatter = self.styles.get(style.lower(), self.format_vancouver)
        return formatter(ref_data)
    
    def format_vancouver(self, ref: Dict) -> str:
        """Vancouver 스타일 포맷"""
        authors = self._format_authors_vancouver(ref.get('authors', []))
        title = ref.get('title', '')
        journal = ref.get('journal', '')
        year = ref.get('year', '')
        volume = ref.get('volume', '')
        issue = ref.get('issue', '')
        pages = ref.get('pages', '')
        
        # 기본 포맷: Authors. Title. Journal. Year;Volume(Issue):Pages.
        formatted = f"{authors} {title}"
        if journal:
            formatted += f" {journal}."
        if year:
            formatted += f" {year}"
        if volume:
            formatted += f";{volume}"
        if issue:
            formatted += f"({issue})"
        if pages:
            formatted += f":{pages}"
        formatted += "."
        
        return formatted
    
    def format_apa(self, ref: Dict) -> str:
        """APA 스타일 포맷"""
        authors = self._format_authors_apa(ref.get('authors', []))
        year = ref.get('year', '')
        title = ref.get('title', '')
        journal = ref.get('journal', '')
        volume = ref.get('volume', '')
        issue = ref.get('issue', '')
        pages = ref.get('pages', '')
        
        # 기본 포맷: Authors (Year). Title. Journal, Volume(Issue), Pages.
        formatted = f"{authors}"
        if year:
            formatted += f" ({year})."
        formatted += f" {title}"
        if journal:
            formatted += f" {journal},"
        if volume:
            formatted += f" {volume}"
        if issue:
            formatted += f"({issue}),"
        if pages:
            formatted += f" {pages}"
        formatted += "."
        
        return formatted
    
    def format_ama(self, ref: Dict) -> str:
        """AMA 스타일 포맷"""
        authors = self._format_authors_ama(ref.get('authors', []))
        title = ref.get('title', '')
        journal = ref.get('journal', '')
        year = ref.get('year', '')
        volume = ref.get('volume', '')
        issue = ref.get('issue', '')
        pages = ref.get('pages', '')
        
        # 기본 포맷: Authors. Title. Journal. Year;Volume(Issue):Pages.
        formatted = f"{authors} {title}"
        if journal:
            formatted += f" {journal}."
        if year:
            formatted += f" {year}"
        if volume:
            formatted += f";{volume}"
        if issue:
            formatted += f"({issue})"
        if pages:
            formatted += f":{pages}"
        formatted += "."
        
        return formatted
    
    def _format_authors_vancouver(self, authors: List[str]) -> str:
        """Vancouver 스타일 저자 포맷"""
        if not authors:
            return ""
        
        formatted_authors = []
        for author in authors[:6]:  # 처음 6명까지
            parts = author.split()
            if len(parts) >= 2:
                # Last name + Initials
                last_name = parts[-1]
                initials = ''.join([p[0] for p in parts[:-1]])
                formatted_authors.append(f"{last_name} {initials}")
            else:
                formatted_authors.append(author)
        
        if len(authors) > 6:
            formatted_authors.append("et al")
        
        return ', '.join(formatted_authors) + '.'
    
    def _format_authors_apa(self, authors: List[str]) -> str:
        """APA 스타일 저자 포맷"""
        if not authors:
            return ""
        
        formatted_authors = []
        for i, author in enumerate(authors):
            parts = author.split()
            if len(parts) >= 2:
                # Last name, F. I.
                last_name = parts[-1]
                initials = '. '.join([p[0] for p in parts[:-1]]) + '.'
                formatted_authors.append(f"{last_name}, {initials}")
            else:
                formatted_authors.append(author)
        
        if len(formatted_authors) == 1:
            return formatted_authors[0]
        elif len(formatted_authors) == 2:
            return ' & '.join(formatted_authors)
        else:
            return ', '.join(formatted_authors[:-1]) + ', & ' + formatted_authors[-1]
    
    def _format_authors_ama(self, authors: List[str]) -> str:
        """AMA 스타일 저자 포맷"""
        return self._format_authors_vancouver(authors)  # AMA는 Vancouver와 유사
    
    def parse_pubmed_citation(self, citation: str) -> Dict:
        """PubMed 형식 인용 파싱"""
        ref_data = {}
        
        # 저자 추출
        author_match = re.search(r'^([^.]+?)\.', citation)
        if author_match:
            authors_str = author_match.group(1)
            ref_data['authors'] = [a.strip() for a in authors_str.split(',')]
        
        # 제목 추출
        title_match = re.search(r'\.\s*([^.]+?)\.\s*([A-Z][^.]*?)\.', citation)
        if title_match:
            ref_data['title'] = title_match.group(1).strip()
            ref_data['journal'] = title_match.group(2).strip()
        
        # 년도, 볼륨, 이슈, 페이지 추출
        pub_match = re.search(r'(\d{4});?(\d+)?(?:\((\d+)\))?:?(\d+-?\d+)?', citation)
        if pub_match:
            ref_data['year'] = pub_match.group(1)
            if pub_match.group(2):
                ref_data['volume'] = pub_match.group(2)
            if pub_match.group(3):
                ref_data['issue'] = pub_match.group(3)
            if pub_match.group(4):
                ref_data['pages'] = pub_match.group(4)
        
        return ref_data


# CLI 인터페이스
if __name__ == "__main__":
    import json
    import sys
    
    formatter = ReferenceFormatter()
    
    if len(sys.argv) > 1:
        # 파일에서 읽기
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            references = json.load(f)
        
        style = sys.argv[2] if len(sys.argv) > 2 else 'vancouver'
        
        for i, ref in enumerate(references, 1):
            formatted = formatter.format_reference(ref, style)
            print(f"{i}. {formatted}")
    else:
        # 예시
        example_ref = {
            'authors': ['Kim JH', 'Lee SH', 'Park CK'],
            'title': 'Minimally invasive spine surgery: techniques and outcomes',
            'journal': 'Spine J',
            'year': '2023',
            'volume': '23',
            'issue': '5',
            'pages': '678-689'
        }
        
        print("Example Reference Formatting:")
        print("-" * 50)
        for style in ['vancouver', 'apa', 'ama']:
            print(f"\n{style.upper()} Style:")
            print(formatter.format_reference(example_ref, style))
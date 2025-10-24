import re
from typing import List, Dict, Any, Set, Tuple
from datetime import datetime
import logging

try:
    from langchain_core.documents import Document

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Code fully AI generated to improve the articles production
class ArticleProcessor:
    """Advanced article content extraction, cleaning, and document preparation"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Compile regex patterns once for better performance
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for better performance"""
        # Comprehensive lists of noise patterns and indicators
        self.boilerplate_patterns = [
            # News agency credits
            r'\(ANSA\)', r'\(Reuters\)', r'\(AFP\)', r'\(AP\)', r'\(Bloomberg\)', r'\(CNN\)',
            r'\(BBC\)', r'\(DW\)', r'\(Le Monde\)', r'\(El País\)',

            # Read more prompts
            r'Continua a leggere', r'Leggi tutto', r'Read more', r'Weiterlesen', r'Lire la suite',
            r'Leer más', r'Read the full story', r'Full story',

            # Source attributions
            r'Fonte:', r'Source:', r'Quelle:', r'Fuente:', r'FOTO:', r'PHOTO:', r'VIDEO:',
            r'Image:', r'Bild:', r'Imagen:',

            # Copyright and legal
            r'©.*', r'Copyright.*', r'RIPRODUZIONE RISERVATA', r'TUTTI I DIRITTI RISERVATI',
            r'All rights reserved', r'Alle Rechte vorbehalten', r'Tous droits réservés',

            # Promotional content
            r'Per saperne di più', r'Scopri di più', r'Pubblicità', r'Sponsorizzato',
            r'Advertisement', r'Advert', r'Werbung', r'Publicidad', r'Annonce',

            # Social media prompts
            r'Follow us', r'Follow .* on', r'Subscribe', r'Newsletter', r'Sign up',
            r'Condividi', r'Share', r'Teilen', r'Partager', r'Compartir',

            # Navigation and UI elements
            r'Home', r'Back to top', r'Menu', r'Navigation', r'Search', r'Login',

            # Ellipsis and truncation
            r'\.{3,}', r'…+'
        ]

        # Compile all boilerplate patterns into one regex
        self.boilerplate_regex = re.compile(
            '|'.join(f'({pattern})' for pattern in self.boilerplate_patterns),
            flags=re.IGNORECASE
        )

        self.filler_words = {
            'click', 'read', 'discover', 'learn', 'subscribe', 'follow', 'share', 'like',
            'comment', 'download', 'install', 'buy', 'purchase', 'shop', 'order', 'get',
            'find', 'watch', 'listen', 'play', 'join', 'register', 'signup', 'try', 'visit'
        }

        self.promotional_indicators = {
            'offerta', 'sconto', 'promozione', 'acquista', 'compra', 'vendita', 'prezzo',
            'offer', 'discount', 'promotion', 'buy', 'purchase', 'sale', 'price', 'deal',
            'angebot', 'rabatt', 'aktion', 'kaufen', 'verkauf', 'preis',
            'offre', 'réduction', 'promotion', 'acheter', 'vente', 'prix',
            'oferta', 'descuento', 'promoción', 'comprar', 'venta', 'precio'
        }

        self.informative_verbs = {
            # Announcements and reports
            'announced', 'confirmed', 'reported', 'stated', 'declared', 'revealed',
            'disclosed', 'unveiled', 'presented',

            # Actions and events
            'died', 'elected', 'approved', 'rejected', 'signed', 'launched', 'started',
            'completed', 'found', 'discovered', 'increased', 'decreased', 'won', 'lost',
            'agreed', 'decided', 'voted', 'passed', 'failed', 'reached',

            # Changes and developments
            'grew', 'fell', 'rose', 'dropped', 'expanded', 'contracted', 'improved',
            'worsened', 'strengthened', 'weakened', 'changed', 'modified',

            # International variants
            'annunciato', 'confermato', 'riferito', 'dichiarato', 'rivelato',
            'morto', 'eletto', 'approvato', 'respinto', 'firmato', 'lanciato',
            'annoncé', 'confirmé', 'rapporté', 'déclaré', 'révélé',
            'angekündigt', 'bestätigt', 'gemeldet', 'erklärt', 'enthüllt',
            'anunciado', 'confirmado', 'informado', 'declarado', 'revelado'
        }

        # Compile factual patterns
        self.number_patterns = [
            r'\$\d+[\d,]*\.?\d*\s*(?:million|billion|trillion)?',
            r'\d+[\d,]*\.?\d*\s*(?:percent|%)',
            r'\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)',
            r'\d{4}'
        ]

        self.quote_patterns = [
            r'"[^"]{10,}"',  # Minimum 10 characters inside quotes
            r"'[^']{10,}'",
            r"«[^»]{10,}»",
            r"„[^“]{10,}“"
        ]

    def extract_article_cores_advanced(self, articles: List[Dict[str, Any]]) -> List[str]:
        """Advanced core extraction with multi-language support and noise filtering"""
        cores = []
        processed_count = 0
        skipped_count = 0

        for article in articles:
            if not self._is_valid_article(article):
                skipped_count += 1
                continue

            title = article.get('title', '').strip()
            content = article.get('content', '').strip()
            source = article.get('source', '').lower()

            # Clean content aggressively
            clean_content = self.clean_content_advanced(content, source)

            # Extract core information
            core = self._extract_core_structured(title, clean_content, source)
            cores.append(core)
            processed_count += 1

        self.logger.info(f"Processed {processed_count} articles, skipped {skipped_count}")
        return cores

    def _is_valid_article(self, article: Dict[str, Any]) -> bool:
        """Validate article has sufficient content with detailed checks"""
        title = article.get('title', '').strip()
        content = article.get('content', '').strip()

        # Skip articles with no title or very short/invalid content
        if (not title or
                title == '[Removed]' or
                len(title) < 15 or  # Increased minimum title length
                title.upper() == title):  # Skip ALL CAPS titles (often spam)
            return False

        # Skip if content is missing or too similar to title
        if (not content or
                content == 'No content' or
                len(content) < 50 or  # Minimum content length
                self._content_is_redundant(title, content)):
            return False

        # Additional quality checks
        if self._is_low_quality_content(content):
            return False

        return True

    def _is_low_quality_content(self, content: str) -> bool:
        """Check for low-quality content indicators"""
        content_lower = content.lower()

        # Check for excessive promotional content
        promotional_words = sum(1 for word in self.promotional_indicators if word in content_lower)
        if promotional_words > 3:
            return True

        # Check for too many filler words
        filler_count = sum(1 for word in self.filler_words if word in content_lower)
        if filler_count > 5:
            return True

        # Check for very short sentences (likely fragmented content)
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        short_sentences = sum(1 for s in sentences if len(s.split()) < 4)
        if short_sentences > len(sentences) * 0.5:  # More than 50% short sentences
            return True

        return False

    def _content_is_redundant(self, title: str, content: str) -> bool:
        """Check if content is just a repetition of the title with improved logic"""
        title_words = set(re.findall(r'\b\w+\b', title.lower()))
        content_words = set(re.findall(r'\b\w+\b', content.lower()))

        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        title_words -= common_words
        content_words -= common_words

        if not title_words:  # If title has only common words
            return False

        overlap = len(title_words & content_words)
        similarity_ratio = overlap / len(title_words)

        return similarity_ratio > 0.6  # Reduced threshold

    def clean_content_advanced(self, content: str, source: str = "") -> str:
        """Advanced content cleaning with source-specific rules"""
        if not content:
            return ""

        # Remove boilerplate patterns (single operation for better performance)
        content = self.boilerplate_regex.sub('', content)

        # Source-specific cleaning
        content = self._apply_source_specific_cleaning(content, source)

        # Remove extra whitespace and normalize
        content = re.sub(r'\s+', ' ', content).strip()

        # Remove very short paragraphs/sentences (likely noise)
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if len(s.strip()) > 25]  # Increased minimum
        content = '. '.join(sentences)

        return content

    def _apply_source_specific_cleaning(self, content: str, source: str) -> str:
        """Apply cleaning rules specific to known news sources"""
        source_cleaning_rules = {
            'ansa': [
                (r'\(ANSA\)', ''),
                (r'\bANSA\b', ''),
            ],
            'reuters': [
                (r'\(Reuters\)', ''),
                (r'\bReuters\b', ''),
            ],
            'bbc': [
                (r'Image source,.*?\.', ''),
                (r'Media caption,.*?\.', ''),
            ],
            'cnn': [
                (r'CNN.*?—', ''),
                (r'Updated:.*?(?=\w)', ''),
            ],
            'fox news': [
                (r'Fox News.*?—', ''),
            ],
            'the guardian': [
                (r'Photograph:.*?\.', ''),
            ],
        }

        for source_key, patterns in source_cleaning_rules.items():
            if source_key in source.lower():
                for pattern, replacement in patterns:
                    content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

        return content

    def _extract_core_structured(self, title: str, content: str, source: str) -> str:
        """Extract structured core information using multiple strategies"""
        if not content:
            return title

        # Strategy 1: Extract key sentences
        key_sentences = self._extract_key_sentences(content)

        # Strategy 2: Look for factual information
        factual_info = self._extract_factual_information(content)

        # Strategy 3: Extract quotes and statements
        quotes = self._extract_quotes(content)

        # Combine strategies based on availability and quality
        core_parts = []

        if key_sentences:
            core_parts.append(". ".join(key_sentences[:2]))  # Reduced from 3 to 2

        if factual_info and len(factual_info) > 0:
            core_parts.append(" | ".join(factual_info[:2]))

        if quotes:
            core_parts.append("Quotes: " + "; ".join(quotes[:1]))  # Reduced from 2 to 1

        # Fallback: use beginning of content if no good extraction
        if not core_parts and len(content) > 50:
            # Take first meaningful segment (avoid very beginning which might have noise)
            sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 30]
            if sentences:
                core_parts.append(sentences[0] + "...")

        # Combine with title (limit total length)
        max_core_length = 500  # Prevent overly long cores
        if core_parts:
            core_text = ' '.join(core_parts)
            if len(core_text) > max_core_length:
                core_text = core_text[:max_core_length] + "..."
            return f"{title} | {core_text}"
        else:
            return title

    def _extract_key_sentences(self, content: str) -> List[str]:
        """Extract the most informative sentences from content using scoring"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        scored_sentences = []

        for sentence in sentences:
            score = self._score_sentence_quality(sentence)
            if score > 0.3:  # Quality threshold
                scored_sentences.append((score, sentence))

        # Sort by score and return top sentences
        scored_sentences.sort(reverse=True)
        return [sentence for score, sentence in scored_sentences[:4]]  # Increased from 3 to 4

    def _score_sentence_quality(self, sentence: str) -> float:
        """Score sentence based on multiple quality factors"""
        score = 0.0
        sentence_lower = sentence.lower()
        words = sentence_lower.split()

        if len(words) < 6:  # Too short
            return 0.0

        # Points for informative verbs
        if any(verb in sentence_lower for verb in self.informative_verbs):
            score += 0.4

        # Points for numbers (concrete information)
        if any(char.isdigit() for char in sentence):
            score += 0.3

        # Points for proper nouns
        proper_nouns = [word for word in sentence.split() if word.istitle() and len(word) > 2]
        score += min(0.2, len(proper_nouns) * 0.05)

        # Penalty for promotional content
        if self._is_promotional(sentence):
            score -= 0.5

        # Penalty for filler words
        filler_count = len(set(words) & self.filler_words)
        score -= filler_count * 0.1

        return max(0.0, score)

    def _extract_factual_information(self, content: str) -> List[str]:
        """Extract factual information like numbers, names, locations"""
        facts = []

        # Extract numbers with context
        for pattern in self.number_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            # Add context for numbers
            for match in matches[:2]:
                # Find the sentence containing this fact
                context = self._get_fact_context(content, match)
                if context:
                    facts.append(f"{match} ({context})")
                else:
                    facts.append(match)

        # Extract names (more sophisticated pattern)
        name_matches = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', content)
        facts.extend(name_matches[:2])

        return facts[:3]  # Limit total facts

    def _get_fact_context(self, content: str, fact: str) -> str:
        """Get context around a factual element"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        for sentence in sentences:
            if fact in sentence:
                # Return first 5 words of the sentence for context
                words = sentence.split()[:7]
                return ' '.join(words) + '...'
        return ""

    def _extract_quotes(self, content: str) -> List[str]:
        """Extract substantial quoted statements"""
        quotes = []

        for pattern in self.quote_patterns:
            matches = re.findall(pattern, content)
            # Filter and clean quotes
            for quote in matches:
                # Remove quote marks and clean
                clean_quote = re.sub(r'^["«„]|["»“]$', '', quote).strip()
                if len(clean_quote.split()) >= 4:  # Minimum 4 words
                    quotes.append(clean_quote)
            if len(quotes) >= 2:  # Limit early
                break

        return quotes[:2]

    def _is_promotional(self, sentence: str) -> bool:
        """Check if sentence is promotional or filler content"""
        sentence_lower = sentence.lower()
        words = set(sentence_lower.split())

        # Check for promotional keywords
        if words & self.promotional_indicators:
            return True

        # Check for filler words density
        filler_count = len(words & self.filler_words)
        if filler_count >= 2:
            return True

        return False

    def prepare_documents_from_cores(self, articles: List[Dict[str, Any]], cores: List[str]) -> List[Document]:
        """Convert article cores to structured LangChain Documents"""
        if not LANGCHAIN_AVAILABLE:
            self.logger.warning("LangChain not available - cannot create Document objects")
            return []

        documents = []

        for i, (article, core) in enumerate(zip(articles, cores), 1):
            # Create metadata-rich document
            metadata = {
                'source': article.get('source', 'Unknown'),
                'category': article.get('category', 'General'),
                'date': self._format_date(article.get('date')),
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'article_id': i,
                'word_count': len(core.split()),
                'language': self._detect_language(core)
            }

            doc_content = f"""ARTICLE {i}: {article.get('title', '')}
SOURCE: {metadata['source']}
CATEGORY: {metadata['category']}
DATE: {metadata['date']}
CONTENT EXTRACT: {core}
"""
            documents.append(Document(page_content=doc_content.strip(), metadata=metadata))

        self.logger.info(f"Created {len(documents)} LangChain documents")
        return documents

    def _detect_language(self, text: str) -> str:
        """Simple language detection based on common words"""
        text_lower = text.lower()

        language_indicators = {
            'it': ['il', 'la', 'che', 'non', 'è', 'con'],
            'fr': ['le', 'la', 'que', 'ne', 'est', 'avec'],
            'de': ['der', 'die', 'das', 'und', 'ist', 'mit'],
            'es': ['el', 'la', 'que', 'no', 'es', 'con'],
            'en': ['the', 'and', 'that', 'not', 'is', 'with']
        }

        scores = {}
        for lang, words in language_indicators.items():
            scores[lang] = sum(1 for word in words if word in text_lower)

        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        return 'unknown'

    def _format_date(self, date_value: Any) -> str:
        """Format date consistently"""
        if isinstance(date_value, datetime):
            return date_value.strftime('%Y-%m-%d %H:%M')
        elif isinstance(date_value, str):
            return date_value
        else:
            return 'Unknown date'

    def prepare_documents(self, articles: List[Dict[str, Any]]) -> List[Document]:
        """Backward compatibility method - uses advanced processing"""
        cores = self.extract_article_cores_advanced(articles)
        return self.prepare_documents_from_cores(articles, cores)

    def clean_content(self, content: str) -> str:
        """Original clean_content method for backward compatibility"""
        return self.clean_content_advanced(content)

    def get_processing_stats(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about article processing"""
        cores = self.extract_article_cores_advanced(articles)
        avg_core_length = sum(len(core.split()) for core in cores) / max(len(cores), 1)

        return {
            "total_articles": len(articles),
            "processed_articles": len(cores),
            "skipped_articles": len(articles) - len(cores),
            "average_core_length": round(avg_core_length, 1),
            "total_words": sum(len(core.split()) for core in cores)
        }
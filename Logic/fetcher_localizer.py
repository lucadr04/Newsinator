# Logic/news_strategies.py
from typing import List, Dict, Any
from datetime import datetime, timedelta


class NewsStrategies:
    def __init__(self, newsapi):
        self.newsapi = newsapi

        # Configuration for different news sources
        # TODO: capire perchè alcuni domini funzionano ed alcuni no
        #  per ora i domini sono disattivati (vedi sotto)
        self.source_configs = {
            "italian": {
                "domains": "ansa.it,repubblica.it,ilsole24ore.com,rainews.it",
                "language": "it"
            },
            "french": {
                "domains": "lemonde.fr,lefigaro.fr,liberation.fr,20minutes.fr",
                "language": "fr"
            },
            "german": {
                "domains": "spiegel.de,zeit.de,faz.net,sueddeutsche.de",
                "language": "de"
            },
            "english": {
                "domains": "bbc.co.uk,theguardian.com,telegraph.co.uk,dailymail.co.uk",
                "language": "en"
            },
            "spanish": {
                "domains": "elpais.com,elmundo.es,abc.es,larazon.es",
                "language": "es"
            },
            "usa": {
                "domains": "cnn.com,nytimes.com,wsj.com,washingtonpost.com",
                "language": "en"
            },
            "world": {
                "domains": None,  # No domain restriction for world news
                "language": "en"
            }
        }

    def _build_query(self, categories: List[str], language: str) -> str:
        """Build search query with distinctive keywords to avoid category overlap"""
        category_queries = {
            "it": {
                "Politics": "governo OR parlamento OR senato OR ministro OR elezioni OR partito OR coalizione OR maggioranza OR opposizione OR legge OR decreto",
                "Economy": "pil OR inflazione OR borsa OR finanza OR mercato OR azionario OR banca OR investimenti OR recessione OR crescita OR deficit OR debito",
                "Technology": "intelligenza artificiale OR IA OR algoritmo OR software OR hardware OR digitale OR startup OR innovazione OR tech OR cybersecurity OR blockchain",
                "Science": "ricerca OR scoperta OR studio OR esperimento OR laboratorio OR scientifico OR pubblicazione OR accademia OR ricerca OR fisica OR chimica OR biologia",
                "Health": "medicina OR ospedale OR paziente OR malattia OR cura OR terapia OR vaccino OR farmaco OR chirurgia OR diagnosi OR prevenzione OR sanitario",
                "Sports": "calcio OR serieA OR partita OR gol OR squadra OR atleta OR campionato OR gara OR competizione OR olimpiadi OR allenamento OR risultato"
            },
            "fr": {
                "Politics": "gouvernement OR parlement OR sénat OR ministre OR élections OR parti OR coalition OR majorité OR opposition OR loi OR décret",
                "Economy": "pib OR inflation OR bourse OR finance OR marché OR actions OR banque OR investissements OR récession OR croissance OR déficit OR dette",
                "Technology": "intelligence artificielle OR IA OR algorithme OR logiciel OR matériel OR numérique OR startup OR innovation OR tech OR cybersécurité",
                "Science": "recherche OR découverte OR étude OR expérience OR laboratoire OR scientifique OR publication OR académie OR physique OR chimie OR biologie",
                "Health": "médecine OR hôpital OR patient OR maladie OR traitement OR thérapie OR vaccin OR médicament OR chirurgie OR diagnostic OR prévention",
                "Sports": "football OR ligue1 OR match OR but OR équipe OR athlète OR championnat OR compétition OR olympiques OR entraînement OR résultat"
            },
            "de": {
                "Politics": "Regierung OR Parlament OR Bundestag OR Minister OR Wahlen OR Partei OR Koalition OR Mehrheit OR Opposition OR Gesetz OR Verordnung",
                "Economy": "BIP OR Inflation OR Börse OR Finanzen OR Markt OR Aktien OR Bank OR Investitionen OR Rezession OR Wachstum OR Defizit OR Schulden",
                "Technology": "künstliche Intelligenz OR KI OR Algorithmus OR Software OR Hardware OR digital OR Startup OR Innovation OR Tech OR Cybersicherheit",
                "Science": "Forschung OR Entdeckung OR Studie OR Experiment OR Labor OR wissenschaftlich OR Veröffentlichung OR Akademie OR Physik OR Chemie OR Biologie",
                "Health": "Medizin OR Krankenhaus OR Patient OR Krankheit OR Behandlung OR Therapie OR Impfstoff OR Medikament OR Chirurgie OR Diagnose OR Prävention",
                "Sports": "Fußball OR Bundesliga OR Spiel OR Tor OR Mannschaft OR Athlet OR Meisterschaft OR Wettbewerb OR Olympia OR Training OR Ergebnis"
            },
            "es": {
                "Politics": "gobierno OR parlamento OR senado OR ministro OR elecciones OR partido OR coalición OR mayoría OR oposición OR ley OR decreto",
                "Economy": "pib OR inflación OR bolsa OR finanzas OR mercado OR acciones OR banco OR inversiones OR recesión OR crecimiento OR déficit OR deuda",
                "Technology": "inteligencia artificial OR IA OR algoritmo OR software OR hardware OR digital OR startup OR innovación OR tecnología OR ciberseguridad",
                "Science": "investigación OR descubrimiento OR estudio OR experimento OR laboratorio OR científico OR publicación OR academia OR física OR química OR biología",
                "Health": "medicina OR hospital OR paciente OR enfermedad OR tratamiento OR terapia OR vacuna OR medicamento OR cirugía OR diagnóstico OR prevención",
                "Sports": "fútbol OR liga OR partido OR gol OR equipo OR atleta OR campeonato OR competición OR olímpicos OR entrenamiento OR resultado"
            },
            "en": {
                "Politics": "government OR parliament OR senate OR minister OR elections OR party OR coalition OR majority OR opposition OR bill OR legislation OR policy",
                "Economy": "gdp OR inflation OR stockmarket OR finance OR market OR stocks OR bank OR investments OR recession OR growth OR deficit OR debt",
                "Technology": "artificial intelligence OR AI OR algorithm OR software OR hardware OR digital OR startup OR innovation OR tech OR cybersecurity OR blockchain",
                "Science": "research OR discovery OR study OR experiment OR laboratory OR scientific OR publication OR academia OR physics OR chemistry OR biology",
                "Health": "medicine OR hospital OR patient OR disease OR treatment OR therapy OR vaccine OR drug OR surgery OR diagnosis OR prevention",
                "Sports": "football OR soccer OR match OR goal OR team OR athlete OR championship OR competition OR olympics OR training OR result"
            }
        }

        query_parts = []
        lang_queries = category_queries.get(language, category_queries["en"])

        for category in categories:
            if category in lang_queries:
                query_parts.append(f"({lang_queries[category]})")

        return " OR ".join(query_parts) if query_parts else "news"

    def _resolve_date_range(self, date_range: str) -> tuple[str, str]:
        """Return the search data range selected."""
        today = datetime.utcnow().date()

        if date_range == "today":
            start = today
            end = today
        elif date_range == "yesterday":
            start = today - timedelta(days=1)
            end = today - timedelta(days=1)
        elif date_range == "this week":
            monday = today - timedelta(days=(today.isoweekday() - 1))
            start = monday
            end = today
        elif date_range == "last week":
            monday_last_week = today - timedelta(days=(today.isoweekday() - 1 + 7))
            sunday_last_week = monday_last_week + timedelta(days=6)
            start = monday_last_week
            end = sunday_last_week
        elif date_range == "this month":
            start = today.replace(day=1)
            end = today
        elif date_range == "last month":
            first_day_this_month = today.replace(day=1)
            last_day_last_month = first_day_this_month - timedelta(days=1)
            start = last_day_last_month.replace(day=1)
            end = last_day_last_month
        else:
            # Default to last 7 days
            start = today - timedelta(days=7)
            end = today

        return start.isoformat(), end.isoformat()

    def _process_articles(self, response: Any, categories: List[str]) -> List[Dict[str, Any]]:
        """Process API response into article format"""
        articles = []
        for article in response.get('articles', []):
            if article.get('title') and article.get('title') != '[Removed]':
                # Try to auto-detect category from content
                detected_category = self._detect_category_from_content(
                    article.get('title', '') + ' ' + article.get('description', ''),
                    categories
                )

                articles.append({
                    'id': f"news_{len(articles)}_{hash(article['url']) % 10000}",
                    'title': article['title'],
                    'content': article.get('description', 'No content'),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'date': datetime.now() - timedelta(hours=len(articles)),
                    'category': detected_category,
                    'url': article['url'],
                    'selected': True
                })
        return articles

    def _detect_category_from_content(self, content: str, available_categories: List[str]) -> str:
        """Try to detect the most relevant category from article content"""
        content_lower = content.lower()
        category_keywords = {
            "Politics": ["government", "parliament", "election", "minister", "policy", "law", "senate"],
            "Economy": ["economy", "market", "stock", "finance", "investment", "gdp", "inflation", "bank"],
            "Technology": ["technology", "software", "digital", "ai", "algorithm", "tech", "computer", "cyber"],
            "Science": ["science", "research", "study", "experiment", "discovery", "scientific", "laboratory"],
            "Health": ["health", "medical", "hospital", "patient", "disease", "treatment", "medicine", "vaccine"],
            "Sports": ["sports", "game", "match", "team", "player", "championship", "olympic", "goal"]
        }

        scores = {}
        for category in available_categories:
            keywords = category_keywords.get(category, [])
            score = sum(1 for keyword in keywords if keyword in content_lower)
            scores[category] = score

        # Return category with highest score, or first available category if no matches
        if scores and max(scores.values()) > 0:
            return max(scores.items(), key=lambda x: x[1])[0]
        else:
            return available_categories[0] if available_categories else "General"

    def _fetch_news(self, source_type: str, date_range: str, categories: List[str]) -> List[Dict[str, Any]]:
        """Generic method to fetch news for any source type"""
        config = self.source_configs.get(source_type, {})
        if not config:
            return []

        query = self._build_query(categories, config["language"])
        from_date, to_date = self._resolve_date_range(date_range)

        # Prepare API parameters
        params = {
            'q': query,
            'language': config["language"],
            'from_param': from_date,
            'to': to_date,
            'sort_by': 'relevancy',
            'page_size': 20
        }

        # Add domains
        #    if config["domains"]:
        #        params['domains'] = config["domains"]

        try:
            response = self.newsapi.get_everything(**params)
            return self._process_articles(response, categories)
        except Exception as e:
            print(f"Error fetching news for {source_type}: {e}")
            return []

    def fetch_italian(self, date_range: str, categories: List[str]) -> List[Dict[str, Any]]:
        """Fetch articles from Italian sources"""
        return self._fetch_news("italian", date_range, categories)

    def fetch_french(self, date_range: str, categories: List[str]) -> List[Dict[str, Any]]:
        """Fetch articles from French sources"""
        return self._fetch_news("french", date_range, categories)

    def fetch_german(self, date_range: str, categories: List[str]) -> List[Dict[str, Any]]:
        """Fetch articles from German sources"""
        return self._fetch_news("german", date_range, categories)

    def fetch_english(self, date_range: str, categories: List[str]) -> List[Dict[str, Any]]:
        """Fetch articles from UK sources"""
        return self._fetch_news("english", date_range, categories)

    def fetch_spanish(self, date_range: str, categories: List[str]) -> List[Dict[str, Any]]:
        """Fetch articles from Spanish sources"""
        return self._fetch_news("spanish", date_range, categories)

    def fetch_usa(self, date_range: str, categories: List[str]) -> List[Dict[str, Any]]:
        """Fetch articles from US sources"""
        return self._fetch_news("usa", date_range, categories)

    def fetch_world(self, date_range: str, categories: List[str]) -> List[Dict[str, Any]]:
        """Fetch international articles"""
        return self._fetch_news("world", date_range, categories)
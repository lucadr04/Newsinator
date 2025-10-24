import logging
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate


class ChainManager:
    """Manages LangChain prompt templates and chains"""

    def __init__(self, llm):
        self.llm = llm
        self.standard_chain = None
        self.focused_chain = None
        self._initialize_chains()

    def _initialize_chains(self):
        """Initialize both standard and focused summarization chains"""
        try:
            # Create the standard summarization prompt
            standard_prompt = ChatPromptTemplate.from_template("""
                You are an expert news analyst. Create a comprehensive summary of the following news articles.
                
                Please provide a detailed analysis that:
                
                1. Identifies the main themes and common topics across all articles
                2. Highlights the most significant events, developments, or trends
                3. Notes any contrasting or complementary viewpoints between sources
                4. Provides context about the importance of these developments
                5. Identifies potential implications or future trends
                
                Structure your response with clear sections and bullet points where appropriate.
                
                ARTICLES TO ANALYZE:
                {context}
                
                Please provide a comprehensive summary:
                """)

            # Create the focused journalist-style prompt
            focused_prompt = ChatPromptTemplate.from_template("""
                You are a seasoned journalist writing a detailed but concise news brief.
                
                **GOAL:** Produce a clear, factual summary that captures all major developments and provides essential context.  
                Be direct and professional — think Reuters or Associated Press feature style.
                
                **INSTRUCTIONS:**
                - IGNORE all ads, filler, and commentary in the source.
                - Focus ONLY on concrete facts, events, and official statements.
                - Include relevant context or background to clarify significance.
                - Expand on each topic: explain who, what, when, where, why, and how.
                - Use strong verbs, active voice, and journalistic clarity.
                - Do NOT include personal opinions, speculation, or rhetorical filler.
                - For each topic try to be talkative, over 8 sentences minimum.
                
                **STYLE:**
                - Write like a professional journalist.
                - Include specific names, locations, dates, and figures.
                - Maintain factual tone; provide context where needed.
                - Keep it informative, engaging, and tight.
                - Do not say things like "here is your summary"
                
                **OUTPUT FORMAT:**
                *COMPELLING HEADLINE ALL IN CAPS*
                *Strong lead paragraph*
                
                *TOPIC NAME*: *Subheading*
                *8-10 sentences with facts + context*
                
                *TOPIC NAME*: *Subheading*  
                *8-10 sentences with facts + context*
                
                ...
                
                ARTICLES:
                {context}
                """)

            # Create both chains
            self.standard_chain = create_stuff_documents_chain(self.llm, standard_prompt)
            self.focused_chain = create_stuff_documents_chain(self.llm, focused_prompt)
            logging.info("✅ LangChain summarization chains initialized successfully")

        except Exception as e:
            logging.error(f"❌ Failed to initialize LangChain chains: {e}")
            self.standard_chain = None
            self.focused_chain = None
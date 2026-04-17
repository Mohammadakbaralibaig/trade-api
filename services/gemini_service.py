from groq import Groq
import os
import logging

logger = logging.getLogger(__name__)


def analyze_with_gemini(sector: str, market_data: str) -> str:
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        prompt = (
            f"You are a senior trade analyst at an Indian economic research firm.\n\n"
            f"Using the market data below, write a detailed and professional trade opportunities report "
            f"for the {sector} sector in India.\n\n"
            f"Market Data:\n{market_data}\n\n"
            f"Structure your report with these sections:\n"
            f"# Trade Opportunities Report: {sector.title()} Sector - India\n"
            f"## 1. Executive Summary\n"
            f"## 2. Current Market Overview\n"
            f"## 3. Key Trade Opportunities\n"
            f"## 4. Export Potential\n"
            f"## 5. Import Trends\n"
            f"## 6. Major Players & Stakeholders\n"
            f"## 7. Challenges & Risks\n"
            f"## 8. Strategic Recommendations\n"
            f"## 9. Conclusion\n\n"
            f"Write at least 3-4 paragraphs per section. Be detailed and professional."
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096
        )

        logger.info(f"Analysis successful for sector: {sector}")
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return f"Analysis error: {str(e)}"
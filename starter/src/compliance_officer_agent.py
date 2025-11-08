# Compliance Officer Agent - ReACT Implementation  
# TODO: Implement Compliance Officer Agent using ReACT prompting

"""
Compliance Officer Agent Module

This agent generates regulatory-compliant SAR narratives using ReACT prompting.
It takes risk analysis results and creates structured documentation for 
FinCEN submission.

YOUR TASKS:
- Study ReACT (Reasoning + Action) prompting methodology
- Design system prompt with Reasoning/Action framework
- Implement narrative generation with word limits
- Validate regulatory compliance requirements
- Create proper audit logging and error handling
"""

import json
import openai
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# TODO: Import your foundation components
from foundation_sar import (
    ComplianceOfficerOutput,
    ExplainabilityLogger, 
    CaseData,
    RiskAnalystOutput
)
from risk_analyst_agent import RiskAnalystAgent 
# Load environment variables
load_dotenv()

class ComplianceOfficerAgent:
    """
    Compliance Officer agent using ReACT prompting framework.
    
    TODO: Implement agent that:
    - Uses Reasoning + Action structured prompting
    - Generates regulatory-compliant SAR narratives
    - Enforces word limits and terminology
    - Includes regulatory citations
    - Validates narrative completeness
    """
    
    def __init__(self, openai_client, explainability_logger, model="gpt-4"):
        """Initialize the Compliance Officer Agent
        
        Args:
            openai_client: OpenAI client instance
            explainability_logger: Logger for audit trails
            model: OpenAI model to use
        """
        self.client = openai_client
        self.logger = explainability_logger
        self.model = model
        self.system_prompt = """You are a Senior Compliance Officer specializing in Anti-Money Laundering (AML) and suspicious activity reporting. Your task is to generate a concise, regulatory-compliant SAR narrative using the ReACT (Reasoning + Action) framework.

            Follow this structured approach:

            REASONING Phase:
            1. Review the risk analyst's findings
            2. Assess regulatory narrative requirements
            3. Identify key compliance elements
            4. Plan narrative structure

            ACTION Phase:
            1. Draft a concise SAR narrative (≤120 words)
            2. Include specific customer details, transaction amounts, and dates
            3. Reference the suspicious activity pattern
            4. Use appropriate regulatory language and cite relevant rules

            Your output must follow this JSON format:
            {
            "case_id": "<string>",
            "narrative": "<SAR narrative text, ≤120 words>",
            "word_count": <integer>,
            "regulatory_citations": ["<citation_1>", "<citation_2>", "..."]
            }

            Ensure the narrative includes:
            - Customer identification
            - Description of suspicious activity
            - Transaction details
            - Justification for suspicion
            - Regulatory terminology and citations (e.g., 31 CFR 1020.320, FinCEN SAR Instructions)

            Be precise, compliant, and audit-ready.
            """


    def generate_compliance_narrative(self, case_data, risk_analysis) -> 'ComplianceOfficerOutput':
        """
        Generate regulatory-compliant SAR narrative using ReACT framework.
        
        TODO: Implement narrative generation that:
        - Creates ReACT-structured user prompt
        - Includes risk analysis findings
        - Makes OpenAI API call with constraints
        - Validates narrative word count
        - Parses and validates JSON response
        - Logs operations for audit
        """
        start_time = datetime.now()
        try:
            prompt = f"""Case ID: {case_data.case_id}
            Customer: {case_data.customer.name} ({case_data.customer.customer_id})
            Accounts: {RiskAnalystAgent._format_accounts(case_data.accounts)}
            Transactions: {RiskAnalystAgent._format_transactions(case_data.transactions)}
            Risk Findings:
            {self._format_risk_analysis_for_prompt(risk_analysis)}"""

            response = self.client.chat_completion(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800,
                model=self.model
            )

            parsed = self._extract_json_from_response(response.choices[0].message.content)
            output = ComplianceOfficerOutput(**parsed)

            validation = self._validate_narrative_compliance(output.narrative)
            if not validation["compliant"]:
                raise ValueError(f"Narrative compliance failed: {validation['reason']}")

            self.logger.log_agent_action(
                agent_type="ComplianceOfficerAgent",
                action="generate_compliance_narrative",
                case_id=case_data.case_id,
                input_data={"case": case_data.model_dump(), "risk_analysis": risk_analysis.model_dump()},
                output_data=output.model_dump(),
                reasoning="Narrative generated successfully",
                execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                success=True
            )
            return output

        except Exception as e:
            self.logger.log_agent_action(
                agent_type="ComplianceOfficerAgent",
                action="generate_compliance_narrative",
                case_id=case_data.case_id,
                input_data={"case": case_data.model_dump(), "risk_analysis": risk_analysis.model_dump()},
                output_data={},
                reasoning="Narrative generation failed",
                execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                success=False,
                error_message=str(e)
            )
            raise ValueError(f"Failed to generate compliance narrative: {e}")
    

    def _extract_json_from_response(self, response_content: str) -> str:
        """Extract JSON content from LLM response
        
        TODO: Implement JSON extraction that handles:
        - JSON in code blocks (```json)
        - JSON in plain text
        - Malformed responses
        - Empty responses
        """
        try:
            if "```json" in response_content:
                response_content = response_content.split("```json")[1].split("```")[0]
            elif "```" in response_content:
                response_content = response_content.split("```")[1].split("```")[0]

            stripped = response_content.strip()
            if not stripped:
                raise ValueError("No JSON content found")

            return json.loads(stripped)

        except Exception as e:
            raise ValueError(f"Failed to parse Risk Analyst JSON output: {e}")


    def _format_risk_analysis_for_prompt(self, risk_analysis) -> str:
        """Format risk analysis results for compliance prompt
        
        TODO: Create structured format that includes:
        - Classification and confidence
        - Key suspicious indicators
        - Risk level assessment
        - Analyst reasoning
        """
        return (
            f"Classification: {risk_analysis.classification} (Confidence: {risk_analysis.confidence:.1f}%)\n"
            f"Risk Level: {risk_analysis.risk_level}\n"
            f"Suspicious Indicators:\n" +
            "\n".join(f"- {indicator}" for indicator in risk_analysis.suspicious_indicators) + "\n"
            f"Analyst Reasoning: {risk_analysis.reasoning}"
        )


    def _validate_narrative_compliance(self, narrative: str) -> Dict[str, Any]:
        """Validate narrative meets regulatory requirements
        
        TODO: Implement validation that checks:
        - Word count (≤120 words)
        - Required elements present
        - Appropriate terminology
        - Regulatory completeness
        """
        word_count = len(narrative.split())
        if word_count > 120:
            return {"compliant": False, "reason": f"Narrative exceeds 120-word limit ({word_count} words)"}

        required_terms = ["suspicious", "transaction", "customer", "account"]
        missing = [term for term in required_terms if term not in narrative.lower()]
        if missing:
            return {"compliant": False, "reason": f"Missing required terms: {', '.join(missing)}"}

        return {"compliant": True}


# ===== REACT PROMPTING HELPERS =====

def create_react_framework():
    """Helper function showing ReACT structure
    
    TODO: Study this example and adapt for compliance narratives:
    
    **REASONING Phase:**
    1. Review the risk analyst's findings
    2. Assess regulatory narrative requirements
    3. Identify key compliance elements
    4. Consider narrative structure
    
    **ACTION Phase:**
    1. Draft concise narrative (≤120 words)
    2. Include specific details and amounts
    3. Reference suspicious activity pattern
    4. Ensure regulatory language
    """
    return {
        "reasoning_phase": [
            "Review risk analysis findings",
            "Assess regulatory requirements", 
            "Identify compliance elements",
            "Plan narrative structure"
        ],
        "action_phase": [
            "Draft concise narrative",
            "Include specific details",
            "Reference activity patterns",
            "Use regulatory language"
        ]
    }

def get_regulatory_requirements():
    """Key regulatory requirements for SAR narratives
    
    TODO: Use these requirements in your prompts:
    """
    return {
        "word_limit": 120,
        "required_elements": [
            "Customer identification",
            "Suspicious activity description", 
            "Transaction amounts and dates",
            "Why activity is suspicious"
        ],
        "terminology": [
            "Suspicious activity",
            "Regulatory threshold",
            "Financial institution",
            "Money laundering",
            "Bank Secrecy Act"
        ],
        "citations": [
            "31 CFR 1020.320 (BSA)",
            "12 CFR 21.11 (SAR Filing)",
            "FinCEN SAR Instructions"
        ]
    }

# ===== TESTING UTILITIES =====

def test_narrative_generation():
    """Test the agent with sample risk analysis
    
    TODO: Use this function to test your implementation:
    - Create sample risk analysis results
    - Initialize compliance agent
    - Generate narrative
    - Validate compliance requirements
    """
    print("🧪 Testing Compliance Officer Agent")
    print("TODO: Implement test case")

def validate_word_count(text: str, max_words: int = 120) -> bool:
    """Helper to validate word count
    
    TODO: Use this utility in your validation:
    """
    word_count = len(text.split())
    return word_count <= max_words

if __name__ == "__main__":
    print("✅ Compliance Officer Agent Module")
    print("ReACT prompting for regulatory narrative generation")
    print("\n📋 TODO Items:")
    print("• Design ReACT system prompt")
    print("• Implement generate_compliance_narrative method")
    print("• Add narrative validation (word count, terminology)")
    print("• Create regulatory citation system")
    print("• Test with sample risk analysis results")
    print("\n💡 Key Concepts:")
    print("• ReACT: Reasoning + Action structured prompting")
    print("• Regulatory Compliance: BSA/AML requirements")
    print("• Narrative Constraints: Word limits and terminology")
    print("• Audit Logging: Complete decision documentation")

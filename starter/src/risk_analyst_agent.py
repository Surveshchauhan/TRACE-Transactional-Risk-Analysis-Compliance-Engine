# Risk Analyst Agent - Chain-of-Thought Implementation
# TODO: Implement Risk Analyst Agent using Chain-of-Thought prompting

"""
Risk Analyst Agent Module

This agent performs suspicious activity classification using Chain-of-Thought reasoning.
It analyzes customer profiles, account behavior, and transaction patterns to identify
potential financial crimes.

YOUR TASKS:
- Study Chain-of-Thought prompting methodology
- Design system prompt with structured reasoning framework
- Implement case analysis with proper error handling
- Parse and validate structured JSON responses
- Create comprehensive audit logging
"""

import json
import openai
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# TODO: Import your foundation components
from foundation_sar import (
        RiskAnalystOutput,
        ExplainabilityLogger,
        CaseData,
        CustomerData,
        AccountData,
        TransactionData
    )
# Load environment variables
load_dotenv()

class RiskAnalystAgent:
    """
    Risk Analyst agent using Chain-of-Thought reasoning.
    
    TODO: Implement agent that:
    - Uses systematic Chain-of-Thought prompting
    - Classifies suspicious activity patterns
    - Returns structured JSON output
    - Handles errors gracefully
    - Logs all operations for audit
    """
    
    def __init__(self, openai_client, explainability_logger, model="gpt-4"):
        """Initialize the Risk Analyst Agent
        
        Args:
            openai_client: OpenAI client instance
            explainability_logger: Logger for audit trails
            model: OpenAI model to use
        """
        self.client = openai_client
        self.logger = explainability_logger
        self.model = model
        self.system_prompt = """
            You are a Senior Financial Crime Risk Analyst specializing in Anti-Money Laundering (AML) investigations. Your task is to analyze suspicious activity using a structured 5-step reasoning framework. Think critically, document your rationale, and produce a clear classification decision.

            Follow this 5-step Chain-of-Thought analysis:

            1. Data Review – Summarize key customer, account, and transaction details.
            2. Pattern Recognition – Identify suspicious behaviors or typologies.
            3. Regulatory Mapping – Link behavior to AML rules or precedents.
            4. Risk Quantification – Assess severity based on volume, velocity, geography, and profile
            5. Classification Decision – Choose one category:
                "Structuring": "Transactions designed to avoid reporting thresholds",
                "Sanctions": "Potential sanctions violations or prohibited parties",
                "Fraud": "Fraudulent transactions or identity-related crimes",
                "Money_Laundering": "Complex schemes to obscure illicit fund sources", 
                "Other": "Suspicious patterns not fitting standard categories"

            Output your reasoning in this JSON format:

            {
                "classification": "<string>",
                "confidence_score": <float between 0 and 1>,
                "reasoning": "<summary of rationale>",
                "key_indicators": ["<indicator_1>", "<indicator_2>", "..."],
                "risk_level": "<Low | Medium | High | Critical>"
            }
            Limit the reasoning to 500 chracters
```'''


        """

# {
#                 "case_id": "<string>",
#                 "classification": "<Structuring | Sanctions | Fraud | Money_Laundering | Other>",
#                 "confidence_score": <float between 0 and 1>,
#                 "reasoning": "<summary of rationale>",
#                 "key_indicators": ["<indicator_1>", "<indicator_2>", "..."],
#                 "risk_level": "<Low | Medium | High>",
#                 "analysis": {
#                     "data_review": "<summary>",
#                     "pattern_recognition": "<suspicious patterns>",
#                     "regulatory_mapping": "<AML rules or precedents>",
#                     "risk_quantification": "<risk assessment>",
#                     "classification_decision": "<Structuring | Sanctions | Fraud | Money_Laundering | Other>"
#                 }
#             }
    def analyze_case(self, case_data) -> 'RiskAnalystOutput':  # Use quotes for forward reference
        """
        Perform risk analysis on a case using Chain-of-Thought reasoning.
        
        TODO: Implement analysis that:
        - Creates structured user prompt with case details
        - Makes OpenAI API call with system prompt
        - Parses and validates JSON response
        - Handles errors and logs operations
        - Returns validated RiskAnalystOutput
        """
        start_time = datetime.now()
        case_id = case_data.case_id

        try:
            user_prompt = self._format_case_for_prompt(case_data)
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3
            )

            content = response.choices[0].message.content
            parsed_json = self._extract_json_from_response(content)
            parsed_json = json.loads(parsed_json)
            output = RiskAnalystOutput(**parsed_json)

            self.logger.log_agent_action(
                agent_type="RiskAnalyst",
                action="analyze_case",
                case_id=case_id,
                input_data={"case_summary": user_prompt},
                output_data=parsed_json,
                reasoning="Chain-of-Thought classification",
                execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                success=True
            )

            return output

        except Exception as e:
            self.logger.log_agent_action(
                agent_type="RiskAnalystS",
                action="analyze_case",
                case_id=case_id,
                input_data={"case_summary": user_prompt},
                output_data={},
                reasoning="Failed to classify case",
                execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                success=False,
                error_message=str(e)
            )
            raise ValueError("No JSON content found")



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
                response_content = response_content.split("```")[1]
            if not response_content.strip():
                raise ValueError("No JSON content found")

            return response_content.strip()
        except Exception as e:
            raise ValueError(f"No JSON content found: {e}")


    def _format_case_for_prompt(self, case_data) -> str:
        """Format case data for the analysis prompt
        
        TODO: Create readable prompt format that includes:
        - Customer profile summary
        - Account information
        - Transaction details with key metrics
        - Financial summary statistics
        """
        customer = case_data.customer
        accounts = case_data.accounts
        transactions = case_data.transactions

        # Customer profile
        summary = f"""Customer Profile:
        - ID: {customer.customer_id}
        - Name: {customer.name}
        - DOB: {customer.date_of_birth}
        - Risk Rating: {customer.risk_rating}
        - Onboarded: {customer.customer_since}

        Accounts ({len(accounts)}):"""
        for a in accounts:
            summary += f"\n- {a.account_id} ({a.account_type}, Balance: {a.current_balance}, Status: {a.status})"

        # Transactions
        txn_summary = f"\n\nTransactions ({len(transactions)} shown below, max 10):"
        for t in transactions[:10]:
            txn_summary += f"\n- {t.transaction_date}: {t.amount} via {t.method} ({t.transaction_type})"

        # Financial summary
        total_balance = sum(a.current_balance for a in accounts)
        total_txn_volume = sum(t.amount for t in transactions)
        avg_txn_amount = total_txn_volume / len(transactions) if transactions else 0

        stats = f"""
    \nFinancial Summary:
    - Total Account Balance: {total_balance:,.2f}
    - Total Transaction Volume: {total_txn_volume:,.2f}
    - Average Transaction Amount: {avg_txn_amount:,.2f}
    """

        return summary + txn_summary + stats
    def _format_accounts(self, accounts: list) -> str:
        """Format account details for prompt inclusion"""
        if not accounts:
            return "No accounts available."

        formatted = [
            f"- {a.account_id}: {a.account_type}, Balance: ${a.current_balance:,.2f}, Status: {a.status}"
            for a in accounts
        ]
        return f"Accounts ({len(accounts)}):\n" + "\n".join(formatted)


    def _format_transactions(self, transactions: list) -> str:
        """Format transaction details for prompt inclusion"""
        if not transactions:
            return "No transactions available."

        formatted = [
            f"{i+1}. {t.transaction_date}: {t.transaction_type} ${t.amount:,.2f} — {t.description}"
            for i, t in enumerate(transactions[:10])
        ]
        return f"Transactions ({len(transactions)} shown below, max 10):\n" + "\n".join(formatted)


# ===== PROMPT ENGINEERING HELPERS =====

def create_chain_of_thought_framework():
    """Helper function showing Chain-of-Thought structure
    
    TODO: Study this example and adapt for financial crime analysis:
    
    **Analysis Framework** (Think step-by-step):
    1. **Data Review**: What does the data tell us?
    2. **Pattern Recognition**: What patterns are suspicious?
    3. **Regulatory Mapping**: Which regulations apply?
    4. **Risk Quantification**: How severe is the risk?
    5. **Classification Decision**: What category fits best?
    """
    return {
        "step_1": "Data Review - Examine all available information",
        "step_2": "Pattern Recognition - Identify suspicious indicators", 
        "step_3": "Regulatory Mapping - Connect to known typologies",
        "step_4": "Risk Quantification - Assess severity level",
        "step_5": "Classification Decision - Determine final category"
    }

def get_classification_categories():
    """Standard SAR classification categories
    
    TODO: Use these categories in your prompts:
    """
    return {
        "Structuring": "Transactions designed to avoid reporting thresholds",
        "Sanctions": "Potential sanctions violations or prohibited parties",
        "Fraud": "Fraudulent transactions or identity-related crimes",
        "Money_Laundering": "Complex schemes to obscure illicit fund sources", 
        "Other": "Suspicious patterns not fitting standard categories"
    }

# ===== TESTING UTILITIES =====

def test_agent_with_sample_case():
    """Test the agent with a sample case
    
    TODO: Use this function to test your implementation:
    - Create sample case data
    - Initialize agent
    - Run analysis
    - Validate results
    """
    print("🧪 Testing Risk Analyst Agent")
    print("TODO: Implement test case")

if __name__ == "__main__":
    print("🔍 Risk Analyst Agent Module")
    print("Chain-of-Thought reasoning for suspicious activity classification")
    print("\n📋 TODO Items:")
    print("• Design Chain-of-Thought system prompt")
    print("• Implement analyze_case method")
    print("• Add JSON parsing and validation")
    print("• Create comprehensive error handling")
    print("• Test with sample cases")
    print("\n💡 Key Concepts:")
    print("• Chain-of-Thought: Step-by-step reasoning")
    print("• Structured Output: Validated JSON responses")
    print("• Financial Crime Detection: Pattern recognition")
    print("• Audit Logging: Complete decision trails")

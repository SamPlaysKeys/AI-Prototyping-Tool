#!/usr/bin/env python3
"""
AI Prototyping Tool

A tool that uses LM Studio to guide users through the complete prototyping process,
from initial idea to implementation plan and presentation generation.

Author: Sam Fleming (SamPlaysKeys)
Email: info@samplayskeys.com
Date: 2025-06-03
"""

import json
import requests
import argparse
import sys
from datetime import datetime
from typing import Dict, List, Optional
import os


class LMStudioClient:
    """Client for interacting with LM Studio API"""

    def __init__(self, base_url: str = "http://localhost:1234"):
        self.base_url = base_url
        self.api_url = f"{base_url}/v1/chat/completions"

    def generate_response(
        self, prompt: str, system_prompt: str = None, max_tokens: int = 2000
    ) -> str:
        """Generate response from LM Studio model"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": "local-model",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=120)
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            return f"Error connecting to LM Studio: {e}"
        except Exception as e:
            return f"Error processing response: {e}"


class AIPrototypingTool:
    """Main prototyping tool class"""

    def __init__(self, lm_studio_url: str = "http://localhost:1234"):
        self.client = LMStudioClient(lm_studio_url)
        self.results = {}

    def generate_problem_statement(self, user_prompt: str) -> str:
        """Generate a clear problem statement from user input"""
        system_prompt = """
You are an expert product manager and business analyst. Your task is to analyze a user's initial idea
and create a clear, concise problem statement that defines the core issue or opportunity.

A good problem statement should:
- Clearly define the problem or opportunity
- Identify the target audience affected
- Explain why this problem matters
- Be specific and actionable
- Avoid proposing solutions

Format your response as a clear problem statement paragraph.
"""

        prompt = f"""
User's initial idea: {user_prompt}

Please create a clear problem statement based on this idea.
"""

        return self.client.generate_response(prompt, system_prompt)

    def generate_personas(self, problem_statement: str) -> str:
        """Generate user personas based on the problem statement"""
        system_prompt = """
You are a UX researcher specializing in persona development. Create 2-3 detailed user personas
based on the given problem statement.

For each persona, include:
- Name and basic demographics
- Role/occupation
- Goals and motivations
- Pain points and frustrations
- Technology comfort level
- Preferred communication methods
- Key quote that represents their mindset

Format each persona clearly with headers and bullet points.
"""

        prompt = f"""
Problem Statement: {problem_statement}

Please create 2-3 detailed user personas who would be affected by this problem.
"""

        return self.client.generate_response(prompt, system_prompt)

    def generate_use_cases(self, problem_statement: str, personas: str) -> str:
        """Generate use cases based on problem statement and personas"""
        system_prompt = """
You are a product analyst specializing in use case development. Create detailed use cases
based on the problem statement and user personas provided.

For each use case, include:
- Use case title
- Primary actor (which persona)
- Preconditions
- Main flow (step-by-step)
- Alternative flows
- Success criteria
- Frequency of use

Create 3-5 comprehensive use cases that cover the main scenarios.
"""

        prompt = f"""
Problem Statement: {problem_statement}

Personas: {personas}

Please create 3-5 detailed use cases based on this information.
"""

        return self.client.generate_response(prompt, system_prompt, max_tokens=3000)

    def generate_tool_outline(
        self, problem_statement: str, personas: str, use_cases: str
    ) -> str:
        """Generate a comprehensive tool outline"""
        system_prompt = """
You are a senior product architect. Create a comprehensive outline for a tool/solution
that addresses the given problem statement, serves the identified personas, and supports the use cases.

Your outline should include:
- Solution overview and key features
- Core functionality breakdown
- User interface considerations
- Technical architecture overview
- Data requirements
- Integration points
- Success metrics
- Risk considerations

Be specific and actionable in your recommendations.
"""

        prompt = f"""
Problem Statement: {problem_statement}

Personas: {personas}

Use Cases: {use_cases}

Please create a comprehensive outline for a tool that addresses this problem.
"""

        return self.client.generate_response(prompt, system_prompt, max_tokens=3000)

    def generate_implementation_instructions(self, tool_outline: str) -> str:
        """Generate step-by-step implementation instructions"""
        system_prompt = """
You are a technical lead and project manager. Create detailed, step-by-step instructions
for implementing the tool outlined.

Your instructions should include:
- Development phases and timeline
- Technical requirements and dependencies
- Team roles and responsibilities
- Development environment setup
- Testing strategy
- Deployment considerations
- Maintenance and support plans

Make the instructions practical and actionable for a development team.
"""

        prompt = f"""
Tool Outline: {tool_outline}

Please create detailed implementation instructions for building this tool.
"""

        return self.client.generate_response(prompt, system_prompt, max_tokens=3000)

    def generate_copilot_presentation_prompt(self, all_content: Dict[str, str]) -> str:
        """Generate a prompt for CoPilot365 to create a presentation deck"""
        system_prompt = """
You are an expert in creating presentation prompts for Microsoft CoPilot365.
Create a detailed prompt that CoPilot365 can use to generate a professional presentation deck.

The prompt should:
- Specify the presentation structure and slide count
- Include key content points for each slide
- Suggest visual elements and design preferences
- Be clear and actionable for CoPilot365
- Include speaker notes guidance

Format the prompt as instructions that can be directly used in CoPilot365.
"""

        prompt = f"""
Based on the following prototyping analysis:

Problem Statement: {all_content['problem_statement']}

Personas: {all_content['personas']}

Use Cases: {all_content['use_cases']}

Tool Outline: {all_content['tool_outline']}

Implementation Instructions: {all_content['implementation_instructions']}

Please create a comprehensive prompt for CoPilot365 to generate a presentation deck for this tool.
"""

        return self.client.generate_response(prompt, system_prompt, max_tokens=2500)

    def evaluate_plan_accuracy(self, all_content: Dict[str, str]) -> str:
        """Evaluate the accuracy and effectiveness of the current plan"""
        system_prompt = """
You are a senior product strategist and consultant. Analyze the complete prototyping plan
and provide an honest assessment of its accuracy, effectiveness, and completeness.

Your evaluation should include:
- Strengths of the current plan
- Potential gaps or weaknesses
- Feasibility assessment
- Market viability considerations
- Technical complexity evaluation
- Resource requirements reality check
- Recommended next steps
- Risk mitigation strategies

Be honest and constructive in your assessment.
"""

        content_summary = f"""
Problem Statement: {all_content['problem_statement']}

Personas: {all_content['personas']}

Use Cases: {all_content['use_cases']}

Tool Outline: {all_content['tool_outline']}

Implementation Instructions: {all_content['implementation_instructions']}
"""

        prompt = f"""
Please evaluate this complete prototyping plan:

{content_summary}

Provide a comprehensive assessment of the plan's accuracy, effectiveness, and next steps.
"""

        return self.client.generate_response(prompt, system_prompt, max_tokens=3000)

    def run_full_analysis(self, user_prompt: str) -> Dict[str, str]:
        """Run the complete prototyping analysis"""
        print("🚀 Starting AI Prototyping Analysis...\n")

        # Step 1: Problem Statement
        print("📋 Generating Problem Statement...")
        problem_statement = self.generate_problem_statement(user_prompt)
        self.results["problem_statement"] = problem_statement
        print("✅ Problem Statement complete\n")

        # Step 2: Personas
        print("👥 Generating User Personas...")
        personas = self.generate_personas(problem_statement)
        self.results["personas"] = personas
        print("✅ Personas complete\n")

        # Step 3: Use Cases
        print("📝 Generating Use Cases...")
        use_cases = self.generate_use_cases(problem_statement, personas)
        self.results["use_cases"] = use_cases
        print("✅ Use Cases complete\n")

        # Step 4: Tool Outline
        print("🔧 Generating Tool Outline...")
        tool_outline = self.generate_tool_outline(
            problem_statement, personas, use_cases
        )
        self.results["tool_outline"] = tool_outline
        print("✅ Tool Outline complete\n")

        # Step 5: Implementation Instructions
        print("📚 Generating Implementation Instructions...")
        implementation_instructions = self.generate_implementation_instructions(
            tool_outline
        )
        self.results["implementation_instructions"] = implementation_instructions
        print("✅ Implementation Instructions complete\n")

        # Step 6: CoPilot Presentation Prompt
        print("🎯 Generating CoPilot365 Presentation Prompt...")
        copilot_prompt = self.generate_copilot_presentation_prompt(self.results)
        self.results["copilot_prompt"] = copilot_prompt
        print("✅ CoPilot Prompt complete\n")

        # Step 7: Plan Evaluation
        print("🔍 Evaluating Plan Accuracy and Effectiveness...")
        plan_evaluation = self.evaluate_plan_accuracy(self.results)
        self.results["plan_evaluation"] = plan_evaluation
        print("✅ Plan Evaluation complete\n")

        return self.results

    def save_results(self, filename: str = None) -> str:
        """Save results to a file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"prototyping_analysis_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)

        return filename

    def generate_markdown_report(self, filename: str = None) -> str:
        """Generate a markdown report of the analysis"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"prototyping_report_{timestamp}.md"

        markdown_content = f"""
# AI Prototyping Analysis Report

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📋 Problem Statement

{self.results.get('problem_statement', 'Not generated')}

## 👥 User Personas

{self.results.get('personas', 'Not generated')}

## 📝 Use Cases

{self.results.get('use_cases', 'Not generated')}

## 🔧 Tool Outline

{self.results.get('tool_outline', 'Not generated')}

## 📚 Implementation Instructions

{self.results.get('implementation_instructions', 'Not generated')}

## 🎯 CoPilot365 Presentation Prompt

{self.results.get('copilot_prompt', 'Not generated')}

## 🔍 Plan Evaluation & Next Steps

{self.results.get('plan_evaluation', 'Not generated')}

---

*Generated by AI Prototyping Tool*
"""

        with open(filename, "w") as f:
            f.write(markdown_content)

        return filename


def main():
    parser = argparse.ArgumentParser(description="AI Prototyping Tool using LM Studio")
    parser.add_argument(
        "--url",
        default="http://localhost:1234",
        help="LM Studio API URL (default: http://localhost:1234)",
    )
    parser.add_argument(
        "--prompt", required=True, help="Initial user prompt for prototyping"
    )
    parser.add_argument("--output-json", help="Output JSON filename (optional)")
    parser.add_argument("--output-md", help="Output Markdown filename (optional)")
    parser.add_argument(
        "--interactive", action="store_true", help="Run in interactive mode"
    )

    args = parser.parse_args()

    # Initialize the tool
    tool = AIPrototypingTool(args.url)

    try:
        if args.interactive:
            print("🎯 AI Prototyping Tool - Interactive Mode")
            print("==========================================\n")

            user_prompt = input("Please enter your initial idea or problem: ")
            if not user_prompt.strip():
                print("Error: No prompt provided")
                sys.exit(1)
        else:
            user_prompt = args.prompt

        # Run the analysis
        results = tool.run_full_analysis(user_prompt)

        # Save results
        json_file = tool.save_results(args.output_json)
        md_file = tool.generate_markdown_report(args.output_md)

        print(f"🎉 Analysis Complete!")
        print(f"📄 JSON Report: {json_file}")
        print(f"📝 Markdown Report: {md_file}")

        # Display summary
        print("\n" + "=" * 50)
        print("📋 PROBLEM STATEMENT")
        print("=" * 50)
        print(results["problem_statement"])

        print("\n" + "=" * 50)
        print("🔍 PLAN EVALUATION & NEXT STEPS")
        print("=" * 50)
        print(results["plan_evaluation"])

    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

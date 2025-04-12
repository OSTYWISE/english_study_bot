import os
import aiohttp
from typing import Dict, Tuple, Optional, List
from dotenv import load_dotenv

from app.llm.utils import extract_questionary, get_questionary_system_prompt, \
    create_questionary_prompt
from app.rag.rag_utils import RAGManager

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize RAG manager
rag_manager = RAGManager()


async def make_api_call(
    prompt: str,
    system_prompt: Optional[str] = None,
    messages: Optional[List[Dict]] = None,
    model_name: str = "gpt-4",
    temperature: float = 1,
    max_tokens: Optional[int] = None,
    structured_flg: bool = False,
    functions: Optional[List[Dict]] = None
) -> Tuple[str, Dict[str, int]]:
    """Make an API call to OpenAI's chat completion endpoint.

    Args:
        prompt: The user's prompt
        system_prompt: Optional system prompt
        model_name: Model to use (default: gpt-4)
        temperature: Sampling temperature (default: 1)
        max_tokens: Max tokens to generate
        structured_flg: Whether to use function calling
        functions: List of function definitions for structured output

    Returns:
        Tuple of (response text, usage statistics)
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    if messages is None:
        messages = [{"role": "user", "content": prompt}]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    if structured_flg and functions:
        payload["functions"] = functions
        payload["function_call"] = {"name": functions[0]["name"]}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, headers=headers, json=payload
            ) as response:
                if response.status != 200:
                    error_detail = await response.text()
                    msg = (
                        f"API call failed with status {response.status}: "
                        f"{error_detail}"
                    )
                    raise aiohttp.ClientError(msg)

                result = await response.json()
                usage_dict = {
                    "input_tokens": result.get('usage', {}).get(
                        'prompt_tokens', 0
                    ),
                    "output_tokens": result.get('usage', {}).get(
                        'completion_tokens', 0
                    )
                }
                print(result)

                if structured_flg and functions:
                    function_call = result['choices'][0]['message'].get(
                        'function_call'
                    )
                    if function_call:
                        return function_call['arguments'], usage_dict

                content = result.get('choices', [{}])[0].get(
                    'message', {}).get('content', '')
                return content, usage_dict

    except Exception as e:
        raise Exception(f"Failed to make OpenAI API call: {str(e)}")


async def generate_questionary(
        litwork_text: str,
        litwork_id: int,
        temperature: float = 1,
        max_tokens: int | None = None,
        raw_result: bool = False
        ):
    try:
        # Get relevant excerpts using RAG
        relevant_excerpts = rag_manager.get_relevant_excerpts_for_questionary(
            litwork_id, k=5
        )
        
        # If no relevant excerpts found, use the full text
        if not relevant_excerpts:
            relevant_excerpts = litwork_text
            
        system_prompt = get_questionary_system_prompt()
        questionary_prompt = create_questionary_prompt(relevant_excerpts)

        text_result, _ = await make_api_call(
            prompt=questionary_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        print(f"Generated text: {text_result}")

        if raw_result:
            return text_result

        questionary = extract_questionary(text_result)
        print(questionary)
        return questionary
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return f"Error: {str(e)}"


async def discuss_litwork(
        discussion_messages: list[dict[str, str]],
        literary_work: str,
        litwork_id: int,
        temperature: float = 0.7,
        max_tokens: int | None = None) -> str:
    try:
        # Get the last user message as the query
        last_user_message = None
        for msg in reversed(discussion_messages):
            if msg["role"] == "user":
                last_user_message = msg["content"]
                break
                
        # If no user message found, use a default query
        if not last_user_message:
            last_user_message = "What is this literary work about?"
            
        # Get relevant excerpts using RAG
        relevant_excerpts = rag_manager.get_relevant_excerpts_for_discussion(
            last_user_message, litwork_id, k=5
        )
        
        # If no relevant excerpts found, use the full text
        if not relevant_excerpts:
            relevant_excerpts = literary_work
            
        system_prompt = (
            "You are a brilliant literature scholar with expertise in 'Drama and Theatre' "
            "advanced English courses. You have a deep understanding of literary theory, "
            "narrative techniques, and critical analysis. When discussing the literary work "
            "with your classmate, focus on deeper analytical insights rather than simple "
            "plot summaries. Explore themes, symbolism, character psychology, narrative "
            "structure, and the author's stylistic choices. Draw connections between the "
            "text and broader literary traditions, historical context, or philosophical "
            "ideas. Challenge conventional interpretations and offer unique perspectives "
            "that reveal hidden layers of meaning. Use your background knowledge about "
            "the work, author, and literary theory to enrich the discussion. Be concise "
            "but insightful in your responses (1-3 sentences), focusing on quality of "
            "analysis over quantity of text."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Literary work text:\n{relevant_excerpts}"}
        ]
        messages.extend(discussion_messages)

        result, _ = await make_api_call(
            prompt="",
            system_prompt=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return result
    except Exception as e:
        return f"Error generating new message to discussion: {str(e)}"


async def generate_idea(
        topic: str,
        litwork_text: str,
        litwork_id: int,
        temperature: float = 0.9,
        max_tokens: int | None = None) -> str:
    try:
        # Get relevant excerpts using RAG
        relevant_excerpts = rag_manager.get_relevant_excerpts_for_idea(
            topic, litwork_id, k=5
        )
        
        # If no relevant excerpts found, use the full text
        if not relevant_excerpts:
            relevant_excerpts = litwork_text
            
        # Prompt in english to create a new non-obvious thought or idea on the certain topic in context of the text of literary work
        idea_prompt = f"""Create a truly original, unconventional, and thought-provoking idea on the following topic in the context of the literary work.

Topic: {topic}
Literary work text: {relevant_excerpts}

Your idea should:
- Be completely original and not obvious
- Connect the topic to unexpected elements in the text
- Challenge conventional interpretations
- Draw surprising parallels or contrasts
- Offer a fresh perspective that most readers would miss
- Be intellectually stimulating and potentially controversial

In your response, provide only the idea and a brief explanation of your reasoning, without any introductory text or additional commentary.
"""
        system_prompt = (
            "You are a brilliant literary theorist and creative thinker with expertise in "
            "generating unconventional ideas. You excel at making unexpected connections, "
            "challenging assumptions, and seeing patterns that others miss. Your ideas are "
            "always original, thought-provoking, and intellectually stimulating. You're not "
            "afraid to be controversial or challenge conventional wisdom when your analysis "
            "supports it."
        )

        result, _ = await make_api_call(
            prompt=idea_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return result or "Failed to generate idea."
    except Exception as e:
        return f"Error generating idea: {str(e)}"

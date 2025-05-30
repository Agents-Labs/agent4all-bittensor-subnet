import os
import time
import json
import logging
import asyncio
from typing import List, Optional, Any, Dict, Union, Literal, TYPE_CHECKING
from rich.console import Console
from rich.live import Live
from openai import AsyncOpenAI
from ..main import (
    display_error,
    display_tool_call,
    display_instruction,
    display_interaction,
    display_generating,
    display_self_reflection,
    ReflectionOutput,
    client,
    adisplay_instruction
)
import inspect
import uuid
from dataclasses import dataclass

if TYPE_CHECKING:
    from ..task.task import Task

@dataclass
class ChatCompletionMessage:
    content: str
    role: str = "assistant"
    refusal: Optional[str] = None
    audio: Optional[str] = None
    function_call: Optional[dict] = None
    tool_calls: Optional[List] = None
    reasoning_content: Optional[str] = None

@dataclass
class Choice:
    finish_reason: Optional[str]
    index: int
    message: ChatCompletionMessage
    logprobs: Optional[dict] = None

@dataclass
class CompletionTokensDetails:
    accepted_prediction_tokens: Optional[int] = None
    audio_tokens: Optional[int] = None
    reasoning_tokens: Optional[int] = None
    rejected_prediction_tokens: Optional[int] = None

@dataclass
class PromptTokensDetails:
    audio_tokens: Optional[int] = None
    cached_tokens: int = 0

@dataclass
class CompletionUsage:
    completion_tokens: int = 0
    prompt_tokens: int = 0
    total_tokens: int = 0
    completion_tokens_details: Optional[CompletionTokensDetails] = None
    prompt_tokens_details: Optional[PromptTokensDetails] = None
    prompt_cache_hit_tokens: int = 0
    prompt_cache_miss_tokens: int = 0

@dataclass
class ChatCompletion:
    id: str
    choices: List[Choice]
    created: int
    model: str
    object: str = "chat.completion"
    system_fingerprint: Optional[str] = None
    service_tier: Optional[str] = None
    usage: Optional[CompletionUsage] = None

def process_stream_chunks(chunks):
    """Process streaming chunks into combined response"""
    if not chunks:
        return None
    
    try:
        first_chunk = chunks[0]
        last_chunk = chunks[-1]
        
        # Basic metadata
        id = getattr(first_chunk, "id", None) 
        created = getattr(first_chunk, "created", None)
        model = getattr(first_chunk, "model", None)
        system_fingerprint = getattr(first_chunk, "system_fingerprint", None)
        
        # Track usage
        completion_tokens = 0
        prompt_tokens = 0
        
        content_list = []
        reasoning_list = []
        tool_calls = []
        current_tool_call = None

        # First pass: Get initial tool call data
        for chunk in chunks:
            if not hasattr(chunk, "choices") or not chunk.choices:
                continue
            
            delta = getattr(chunk.choices[0], "delta", None)
            if not delta:
                continue

            # Handle content and reasoning
            if hasattr(delta, "content") and delta.content:
                content_list.append(delta.content)
            if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                reasoning_list.append(delta.reasoning_content)
            
            # Handle tool calls
            if hasattr(delta, "tool_calls") and delta.tool_calls:
                for tool_call_delta in delta.tool_calls:
                    if tool_call_delta.index is not None and tool_call_delta.id:
                        # Found the initial tool call
                        current_tool_call = {
                            "id": tool_call_delta.id,
                            "type": "function",
                            "function": {
                                "name": tool_call_delta.function.name,
                                "arguments": ""
                            }
                        }
                        while len(tool_calls) <= tool_call_delta.index:
                            tool_calls.append(None)
                        tool_calls[tool_call_delta.index] = current_tool_call
                        current_tool_call = tool_calls[tool_call_delta.index]
                    elif current_tool_call is not None and hasattr(tool_call_delta.function, "arguments"):
                        if tool_call_delta.function.arguments:
                            current_tool_call["function"]["arguments"] += tool_call_delta.function.arguments

        # Remove any None values and empty tool calls
        tool_calls = [tc for tc in tool_calls if tc and tc["id"] and tc["function"]["name"]]

        combined_content = "".join(content_list) if content_list else ""
        combined_reasoning = "".join(reasoning_list) if reasoning_list else None
        finish_reason = getattr(last_chunk.choices[0], "finish_reason", None) if hasattr(last_chunk, "choices") and last_chunk.choices else None

        # Create ToolCall objects
        processed_tool_calls = []
        if tool_calls:
            try:
                from openai.types.chat import ChatCompletionMessageToolCall
                for tc in tool_calls:
                    tool_call = ChatCompletionMessageToolCall(
                        id=tc["id"],
                        type=tc["type"],
                        function={
                            "name": tc["function"]["name"],
                            "arguments": tc["function"]["arguments"]
                        }
                    )
                    processed_tool_calls.append(tool_call)
            except Exception as e:
                print(f"Error processing tool call: {e}")

        message = ChatCompletionMessage(
            content=combined_content,
            role="assistant",
            reasoning_content=combined_reasoning,
            tool_calls=processed_tool_calls if processed_tool_calls else None
        )
        
        choice = Choice(
            finish_reason=finish_reason or "tool_calls" if processed_tool_calls else None,
            index=0,
            message=message
        )

        usage = CompletionUsage(
            completion_tokens=completion_tokens,
            prompt_tokens=prompt_tokens,
            total_tokens=completion_tokens + prompt_tokens,
            completion_tokens_details=CompletionTokensDetails(),
            prompt_tokens_details=PromptTokensDetails()
        )
        
        return ChatCompletion(
            id=id,
            choices=[choice],
            created=created,
            model=model,
            system_fingerprint=system_fingerprint,
            usage=usage
        )
        
    except Exception as e:
        print(f"Error processing chunks: {e}")
        return None

class Agent:
    def _generate_tool_definition(self, function_name):
        """
        Generate a tool definition from a function name by inspecting the function.
        """
        logging.debug(f"Attempting to generate tool definition for: {function_name}")
        
        # First try to get the tool definition if it exists
        tool_def_name = f"{function_name}_definition"
        tool_def = globals().get(tool_def_name)
        logging.debug(f"Looking for {tool_def_name} in globals: {tool_def is not None}")
        
        if not tool_def:
            import __main__
            tool_def = getattr(__main__, tool_def_name, None)
            logging.debug(f"Looking for {tool_def_name} in __main__: {tool_def is not None}")
        
        if tool_def:
            logging.debug(f"Found tool definition: {tool_def}")
            return tool_def

        # Try to find the function in the agent's tools list first
        func = None
        for tool in self.tools:
            if callable(tool) and getattr(tool, '__name__', '') == function_name:
                func = tool
                break
        
        logging.debug(f"Looking for {function_name} in agent tools: {func is not None}")
        
        # If not found in tools, try globals and main
        if not func:
            func = globals().get(function_name)
            logging.debug(f"Looking for {function_name} in globals: {func is not None}")
            
            if not func:
                import __main__
                func = getattr(__main__, function_name, None)
                logging.debug(f"Looking for {function_name} in __main__: {func is not None}")

        if not func or not callable(func):
            logging.debug(f"Function {function_name} not found or not callable")
            return None

        import inspect
        # Langchain tools
        if inspect.isclass(func) and hasattr(func, 'run') and not hasattr(func, '_run'):
            original_func = func
            func = func.run
            function_name = original_func.__name__
        # CrewAI tools
        elif inspect.isclass(func) and hasattr(func, '_run'):
            original_func = func
            func = func._run
            function_name = original_func.__name__

        sig = inspect.signature(func)
        logging.debug(f"Function signature: {sig}")
        
        # Skip self, *args, **kwargs, so they don't get passed in arguments
        parameters_list = []
        for name, param in sig.parameters.items():
            if name == "self":
                continue
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            parameters_list.append((name, param))

        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # Parse docstring for parameter descriptions
        docstring = inspect.getdoc(func)
        logging.debug(f"Function docstring: {docstring}")
        
        param_descriptions = {}
        if docstring:
            import re
            param_section = re.split(r'\s*Args:\s*', docstring)
            logging.debug(f"Param section split: {param_section}")
            if len(param_section) > 1:
                param_lines = param_section[1].split('\n')
                for line in param_lines:
                    line = line.strip()
                    if line and ':' in line:
                        param_name, param_desc = line.split(':', 1)
                        param_descriptions[param_name.strip()] = param_desc.strip()
        
        logging.debug(f"Parameter descriptions: {param_descriptions}")

        for name, param in parameters_list:
            param_type = "string"  # Default type
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == list:
                    param_type = "array"
                elif param.annotation == dict:
                    param_type = "object"
            
            param_info = {"type": param_type}
            if name in param_descriptions:
                param_info["description"] = param_descriptions[name]
            
            parameters["properties"][name] = param_info
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(name)
        
        logging.debug(f"Generated parameters: {parameters}")

        # Extract description from docstring
        description = docstring.split('\n')[0] if docstring else f"Function {function_name}"
        
        tool_def = {
            "type": "function",
            "function": {
                "name": function_name,
                "description": description,
                "parameters": parameters
            }
        }
        logging.debug(f"Generated tool definition: {tool_def}")
        return tool_def

    def __init__(
        self,
        name: Optional[str] = None,
        role: Optional[str] = None,
        goal: Optional[str] = None,
        backstory: Optional[str] = None,
        instructions: Optional[str] = None,
        llm: Optional[Union[str, Any]] = None,
        tools: Optional[List[Any]] = None,
        function_calling_llm: Optional[Any] = None,
        max_iter: int = 20,
        max_rpm: Optional[int] = None,
        max_execution_time: Optional[int] = None,
        memory: Optional[Any] = None,
        verbose: bool = True,
        allow_delegation: bool = False,
        step_callback: Optional[Any] = None,
        cache: bool = True,
        system_template: Optional[str] = None,
        prompt_template: Optional[str] = None,
        response_template: Optional[str] = None,
        allow_code_execution: Optional[bool] = False,
        max_retry_limit: int = 2,
        respect_context_window: bool = True,
        code_execution_mode: Literal["safe", "unsafe"] = "safe",
        embedder_config: Optional[Dict[str, Any]] = None,
        knowledge: Optional[List[str]] = None,
        knowledge_config: Optional[Dict[str, Any]] = None,
        use_system_prompt: Optional[bool] = True,
        markdown: bool = True,
        self_reflect: bool = False,
        max_reflect: int = 3,
        min_reflect: int = 1,
        reflect_llm: Optional[str] = None,
        user_id: Optional[str] = None,
        reasoning_steps: bool = False
    ):
        # Add check at start if memory is requested
        if memory is not None:
            try:
                from ..memory.memory import Memory
                MEMORY_AVAILABLE = True
            except ImportError:
                raise ImportError(
                    "Memory features requested in Agent but memory dependencies not installed. "
                    "Please install with: pip install \"praisonaiagents[memory]\""
                )

        # Handle backward compatibility for required fields
        if all(x is None for x in [name, role, goal, backstory, instructions]):
            raise ValueError("At least one of name, role, goal, backstory, or instructions must be provided")

        # Configure logging to suppress unwanted outputs
        logging.getLogger("litellm").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)

        # If instructions are provided, use them to set role, goal, and backstory
        if instructions:
            self.name = name or "Agent"
            self.role = role or "Assistant"
            self.goal = goal or instructions
            self.backstory = backstory or instructions
            # Set self_reflect to False by default for instruction-based agents
            self.self_reflect = False if self_reflect is None else self_reflect
        else:
            # Use provided values or defaults
            self.name = name or "Agent"
            self.role = role or "Assistant"
            self.goal = goal or "Help the user with their tasks"
            self.backstory = backstory or "I am an AI assistant"
            # Default to True for traditional agents if not specified
            self.self_reflect = True if self_reflect is None else self_reflect
        
        self.instructions = instructions
        # Check for model name in environment variable if not provided
        self._using_custom_llm = False

        # If the user passes a dictionary (for advanced configuration)
        if isinstance(llm, dict) and "model" in llm:
            try:
                from ..llm.llm import LLM
                self.llm_instance = LLM(**llm)  # Pass all dict items as kwargs
                self._using_custom_llm = True
            except ImportError as e:
                raise ImportError(
                    "LLM features requested but dependencies not installed. "
                    "Please install with: pip install \"praisonaiagents[llm]\""
                ) from e
        # If the user passes a string with a slash (provider/model)
        elif isinstance(llm, str) and "/" in llm:
            try:
                from ..llm.llm import LLM
                # Pass the entire string so LiteLLM can parse provider/model
                self.llm_instance = LLM(model=llm)
                self._using_custom_llm = True
                
                # Ensure tools are properly accessible when using custom LLM
                if tools:
                    logging.debug(f"Tools passed to Agent with custom LLM: {tools}")
                    # Store the tools for later use
                    self.tools = tools
            except ImportError as e:
                raise ImportError(
                    "LLM features requested but dependencies not installed. "
                    "Please install with: pip install \"praisonaiagents[llm]\""
                ) from e
        # Otherwise, fall back to OpenAI environment/name
        else:
            self.llm = llm or os.getenv('OPENAI_MODEL_NAME', 'gpt-4o')
        self.tools = tools if tools else []  # Store original tools
        self.function_calling_llm = function_calling_llm
        self.max_iter = max_iter
        self.max_rpm = max_rpm
        self.max_execution_time = max_execution_time
        self.memory = memory
        self.verbose = verbose
        self.allow_delegation = allow_delegation
        self.step_callback = step_callback
        self.cache = cache
        self.system_template = system_template
        self.prompt_template = prompt_template
        self.response_template = response_template
        self.allow_code_execution = allow_code_execution
        self.max_retry_limit = max_retry_limit
        self.respect_context_window = respect_context_window
        self.code_execution_mode = code_execution_mode
        self.embedder_config = embedder_config
        self.knowledge = knowledge
        self.use_system_prompt = use_system_prompt
        self.chat_history = []
        self.markdown = markdown
        self.max_reflect = max_reflect
        self.min_reflect = min_reflect
        # Use the same model selection logic for reflect_llm
        self.reflect_llm = reflect_llm or os.getenv('OPENAI_MODEL_NAME', 'gpt-4o')
        self.console = Console()  # Create a single console instance for the agent
        
        # Initialize system prompt
        self.system_prompt = f"""{self.backstory}\n
Your Role: {self.role}\n
Your Goal: {self.goal}
        """

        # Generate unique IDs
        self.agent_id = str(uuid.uuid4())

        # Store user_id
        self.user_id = user_id or "praison"
        self.reasoning_steps = reasoning_steps

        # Check if knowledge parameter has any values
        if not knowledge:
            self.knowledge = None
        else:
            # Initialize Knowledge with provided or default config
            from praisonaiagents.knowledge import Knowledge
            self.knowledge = Knowledge(knowledge_config or None)
            
            # Handle knowledge
            if knowledge:
                for source in knowledge:
                    self._process_knowledge(source)

    def _process_knowledge(self, knowledge_item):
        """Process and store knowledge from a file path, URL, or string."""
        try:
            if os.path.exists(knowledge_item):
                # It's a file path
                self.knowledge.add(knowledge_item, user_id=self.user_id, agent_id=self.agent_id)
            elif knowledge_item.startswith("http://") or knowledge_item.startswith("https://"):
                # It's a URL
                pass
            else:
                # It's a string content
                self.knowledge.store(knowledge_item, user_id=self.user_id, agent_id=self.agent_id)
        except Exception as e:
            logging.error(f"Error processing knowledge item: {knowledge_item}, error: {e}")

    def generate_task(self) -> 'Task':
        """Generate a Task object from the agent's instructions"""
        from ..task.task import Task
        
        description = self.instructions if self.instructions else f"Execute task as {self.role} with goal: {self.goal}"
        expected_output = "Complete the assigned task successfully"
        
        return Task(
            name=self.name,
            description=description,
            expected_output=expected_output,
            agent=self,
            tools=self.tools
        )

    def execute_tool(self, function_name, arguments):
        """
        Execute a tool dynamically based on the function name and arguments.
        """
        logging.debug(f"{self.name} executing tool {function_name} with arguments: {arguments}")

        # Special handling for MCP tools
        # Check if tools is an MCP instance with the requested function name
        from ..mcp.mcp import MCP
        if isinstance(self.tools, MCP):
            logging.debug(f"Looking for MCP tool {function_name}")
            # Check if any of the MCP tools match the function name
            for mcp_tool in self.tools.runner.tools:
                if hasattr(mcp_tool, 'name') and mcp_tool.name == function_name:
                    logging.debug(f"Found matching MCP tool: {function_name}")
                    return self.tools.runner.call_tool(function_name, arguments)

        # Try to find the function in the agent's tools list first
        func = None
        for tool in self.tools if isinstance(self.tools, (list, tuple)) else []:
            if (callable(tool) and getattr(tool, '__name__', '') == function_name) or \
               (inspect.isclass(tool) and tool.__name__ == function_name):
                func = tool
                break
        
        if func is None:
            # If not found in tools, try globals and main
            func = globals().get(function_name)
            if not func:
                import __main__
                func = getattr(__main__, function_name, None)

        if func:
            try:
                # Langchain: If it's a class with run but not _run, instantiate and call run
                if inspect.isclass(func) and hasattr(func, 'run') and not hasattr(func, '_run'):
                    instance = func()
                    run_params = {k: v for k, v in arguments.items() 
                                  if k in inspect.signature(instance.run).parameters 
                                  and k != 'self'}
                    return instance.run(**run_params)

                # CrewAI: If it's a class with an _run method, instantiate and call _run
                elif inspect.isclass(func) and hasattr(func, '_run'):
                    instance = func()
                    run_params = {k: v for k, v in arguments.items() 
                                  if k in inspect.signature(instance._run).parameters 
                                  and k != 'self'}
                    return instance._run(**run_params)

                # Otherwise treat as regular function
                elif callable(func):
                    return func(**arguments)
            except Exception as e:
                error_msg = str(e)
                logging.error(f"Error executing tool {function_name}: {error_msg}")
                return {"error": error_msg}
        
        error_msg = f"Tool '{function_name}' is not callable"
        logging.error(error_msg)
        return {"error": error_msg}

    def clear_history(self):
        self.chat_history = []

    def __str__(self):
        return f"Agent(name='{self.name}', role='{self.role}', goal='{self.goal}')"

    def _process_stream_response(self, messages, temperature, start_time, formatted_tools=None, reasoning_steps=False):
        """Process streaming response and return final response"""
        try:
            # Create the response stream
            response_stream = client.chat.completions.create(
                model=self.llm,
                messages=messages,
                temperature=temperature,
                tools=formatted_tools if formatted_tools else None,
                stream=True
            )
            
            full_response_text = ""
            reasoning_content = ""
            chunks = []
            
            # Create Live display with proper configuration
            with Live(
                display_generating("", start_time),
                console=self.console,
                refresh_per_second=4,
                transient=True,
                vertical_overflow="ellipsis",
                auto_refresh=True
            ) as live:
                for chunk in response_stream:
                    chunks.append(chunk)
                    if chunk.choices[0].delta.content:
                        full_response_text += chunk.choices[0].delta.content
                        live.update(display_generating(full_response_text, start_time))
                    
                    # Update live display with reasoning content if enabled
                    if reasoning_steps and hasattr(chunk.choices[0].delta, "reasoning_content"):
                        rc = chunk.choices[0].delta.reasoning_content
                        if rc:
                            reasoning_content += rc
                            live.update(display_generating(f"{full_response_text}\n[Reasoning: {reasoning_content}]", start_time))
            
            # Clear the last generating display with a blank line
            self.console.print()
            final_response = process_stream_chunks(chunks)
            return final_response
            
        except Exception as e:
            display_error(f"Error in stream processing: {e}")
            return None

    def _chat_completion(self, messages, temperature=0.2, tools=None, stream=True, reasoning_steps=False):
        start_time = time.time()
        logging.debug(f"{self.name} sending messages to LLM: {messages}")

        formatted_tools = []
        if tools is None:
            tools = self.tools
        if tools:
            for tool in tools:
                if isinstance(tool, str):
                    # Generate tool definition for string tool names
                    tool_def = self._generate_tool_definition(tool)
                    if tool_def:
                        formatted_tools.append(tool_def)
                    else:
                        logging.warning(f"Could not generate definition for tool: {tool}")
                elif isinstance(tool, dict):
                    formatted_tools.append(tool)
                elif hasattr(tool, "to_openai_tool"):
                    formatted_tools.append(tool.to_openai_tool())
                elif callable(tool):
                    formatted_tools.append(self._generate_tool_definition(tool.__name__))
                else:
                    logging.warning(f"Tool {tool} not recognized")

        try:
            # Use the custom LLM instance if available
            if self._using_custom_llm and hasattr(self, 'llm_instance'):
                if stream:
                    # Debug logs for tool info
                    if formatted_tools:
                        logging.debug(f"Passing {len(formatted_tools)} formatted tools to LLM instance: {formatted_tools}")
                    
                    # Use the LLM instance for streaming responses
                    final_response = self.llm_instance.get_response(
                        prompt=messages[1:],  # Skip system message as LLM handles it separately  
                        system_prompt=messages[0]['content'] if messages and messages[0]['role'] == 'system' else None,
                        temperature=temperature,
                        tools=formatted_tools if formatted_tools else None,
                        verbose=self.verbose,
                        markdown=self.markdown,
                        stream=True,
                        console=self.console,
                        execute_tool_fn=self.execute_tool,
                        agent_name=self.name,
                        agent_role=self.role,
                        reasoning_steps=reasoning_steps
                    )
                else:
                    # Non-streaming with custom LLM
                    final_response = self.llm_instance.get_response(
                        prompt=messages[1:],
                        system_prompt=messages[0]['content'] if messages and messages[0]['role'] == 'system' else None,
                        temperature=temperature,
                        tools=formatted_tools if formatted_tools else None,
                        verbose=self.verbose,
                        markdown=self.markdown,
                        stream=False,
                        console=self.console,
                        execute_tool_fn=self.execute_tool,
                        agent_name=self.name,
                        agent_role=self.role,
                        reasoning_steps=reasoning_steps
                    )
            else:
                # Use the standard OpenAI client approach
                if stream:
                    # Process as streaming response with formatted tools
                    final_response = self._process_stream_response(
                        messages, 
                        temperature, 
                        start_time, 
                        formatted_tools=formatted_tools if formatted_tools else None,
                        reasoning_steps=reasoning_steps
                    )
                else:
                    # Process as regular non-streaming response
                    final_response = client.chat.completions.create(
                        model=self.llm,
                        messages=messages,
                        temperature=temperature,
                        tools=formatted_tools if formatted_tools else None,
                        stream=False
                    )

            tool_calls = getattr(final_response.choices[0].message, 'tool_calls', None)

            if tool_calls:
                messages.append({
                    "role": "assistant", 
                    "content": final_response.choices[0].message.content,
                    "tool_calls": tool_calls
                })

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    if self.verbose:
                        display_tool_call(f"Agent {self.name} is calling function '{function_name}' with arguments: {arguments}")

                    tool_result = self.execute_tool(function_name, arguments)
                    results_str = json.dumps(tool_result) if tool_result else "Function returned an empty output"

                    if self.verbose:
                        display_tool_call(f"Function '{function_name}' returned: {results_str}")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": results_str
                    })

                # Get final response after tool calls
                if stream:
                    final_response = self._process_stream_response(
                        messages, 
                        temperature, 
                        start_time,
                        formatted_tools=formatted_tools if formatted_tools else None,
                        reasoning_steps=reasoning_steps
                    )
                else:
                    final_response = client.chat.completions.create(
                        model=self.llm,
                        messages=messages,
                        temperature=temperature,
                        stream=False
                    )

            return final_response

        except Exception as e:
            display_error(f"Error in chat completion: {e}")
            return None

    def chat(self, prompt, temperature=0.2, tools=None, output_json=None, output_pydantic=None, reasoning_steps=False, stream=True):
        # Log all parameter values when in debug mode
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            param_info = {
                "prompt": str(prompt)[:100] + "..." if isinstance(prompt, str) and len(str(prompt)) > 100 else str(prompt),
                "temperature": temperature,
                "tools": [t.__name__ if hasattr(t, "__name__") else str(t) for t in tools] if tools else None,
                "output_json": str(output_json.__class__.__name__) if output_json else None,
                "output_pydantic": str(output_pydantic.__class__.__name__) if output_pydantic else None,
                "reasoning_steps": reasoning_steps,
                "agent_name": self.name,
                "agent_role": self.role,
                "agent_goal": self.goal
            }
            logging.debug(f"Agent.chat parameters: {json.dumps(param_info, indent=2, default=str)}")
        
        start_time = time.time()
        reasoning_steps = reasoning_steps or self.reasoning_steps
        # Search for existing knowledge if any knowledge is provided
        if self.knowledge:
            search_results = self.knowledge.search(prompt, agent_id=self.agent_id)
            if search_results:
                # Check if search_results is a list of dictionaries or strings
                if isinstance(search_results, dict) and 'results' in search_results:
                    # Extract memory content from the results
                    knowledge_content = "\n".join([result['memory'] for result in search_results['results']])
                else:
                    # If search_results is a list of strings, join them directly
                    knowledge_content = "\n".join(search_results)
                
                # Append found knowledge to the prompt
                prompt = f"{prompt}\n\nKnowledge: {knowledge_content}"

        if self._using_custom_llm:
            try:
                # Special handling for MCP tools when using provider/model format
                tool_param = self.tools if tools is None else tools
                
                # Convert MCP tool objects to OpenAI format if needed
                if tool_param is not None:
                    from ..mcp.mcp import MCP
                    if isinstance(tool_param, MCP) and hasattr(tool_param, 'to_openai_tool'):
                        logging.debug("Converting MCP tool to OpenAI format")
                        openai_tool = tool_param.to_openai_tool()
                        if openai_tool:
                            tool_param = [openai_tool]
                            logging.debug(f"Converted MCP tool: {tool_param}")
                
                # Pass everything to LLM class
                response_text = self.llm_instance.get_response(
                    prompt=prompt,
                    system_prompt=f"{self.backstory}\n\nYour Role: {self.role}\n\nYour Goal: {self.goal}" if self.use_system_prompt else None,
                    chat_history=self.chat_history,
                    temperature=temperature,
                    tools=tool_param,
                    output_json=output_json,
                    output_pydantic=output_pydantic,
                    verbose=self.verbose,
                    markdown=self.markdown,
                    self_reflect=self.self_reflect,
                    max_reflect=self.max_reflect,
                    min_reflect=self.min_reflect,
                    console=self.console,
                    agent_name=self.name,
                    agent_role=self.role,
                    agent_tools=[t.__name__ if hasattr(t, '__name__') else str(t) for t in (tools if tools is not None else self.tools)],
                    execute_tool_fn=self.execute_tool,  # Pass tool execution function
                    reasoning_steps=reasoning_steps
                )

                self.chat_history.append({"role": "user", "content": prompt})
                self.chat_history.append({"role": "assistant", "content": response_text})

                # Log completion time if in debug mode
                if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                    total_time = time.time() - start_time
                    logging.debug(f"Agent.chat completed in {total_time:.2f} seconds")

                return response_text
            except Exception as e:
                display_error(f"Error in LLM chat: {e}")
                return None
        else:
            if self.use_system_prompt:
                system_prompt = f"""{self.backstory}\n
Your Role: {self.role}\n
Your Goal: {self.goal}
                """
                if output_json:
                    system_prompt += f"\nReturn ONLY a JSON object that matches this Pydantic model: {json.dumps(output_json.model_json_schema())}"
                elif output_pydantic:
                    system_prompt += f"\nReturn ONLY a JSON object that matches this Pydantic model: {json.dumps(output_pydantic.model_json_schema())}"
            else:
                system_prompt = None

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.extend(self.chat_history)

            # Modify prompt if output_json or output_pydantic is specified
            original_prompt = prompt
            if output_json or output_pydantic:
                if isinstance(prompt, str):
                    prompt += "\nReturn ONLY a valid JSON object. No other text or explanation."
                elif isinstance(prompt, list):
                    # For multimodal prompts, append to the text content
                    for item in prompt:
                        if item["type"] == "text":
                            item["text"] += "\nReturn ONLY a valid JSON object. No other text or explanation."
                            break

            if isinstance(prompt, list):
                # If we receive a multimodal prompt list, place it directly in the user message
                messages.append({"role": "user", "content": prompt})
            else:
                messages.append({"role": "user", "content": prompt})

            final_response_text = None
            reflection_count = 0
            start_time = time.time()

            while True:
                try:
                    if self.verbose:
                        # Handle both string and list prompts for instruction display
                        display_text = prompt
                        if isinstance(prompt, list):
                            # Extract text content from multimodal prompt
                            display_text = next((item["text"] for item in prompt if item["type"] == "text"), "")
                        
                        if display_text and str(display_text).strip():
                            # Pass agent information to display_instruction
                            agent_tools = [t.__name__ if hasattr(t, '__name__') else str(t) for t in self.tools]
                            display_instruction(
                                f"Agent {self.name} is processing prompt: {display_text}", 
                                console=self.console,
                                agent_name=self.name,
                                agent_role=self.role,
                                agent_tools=agent_tools
                            )

                    response = self._chat_completion(messages, temperature=temperature, tools=tools if tools else None, reasoning_steps=reasoning_steps, stream=stream)
                    if not response:
                        return None

                    tool_calls = getattr(response.choices[0].message, 'tool_calls', None)
                    response_text = response.choices[0].message.content.strip()
                    if tool_calls: ## TODO: Most likely this tool call is already called in _chat_completion, so maybe we can remove this.
                        messages.append({
                            "role": "assistant",
                            "content": response_text,
                            "tool_calls": tool_calls
                        })
                        
                        for tool_call in tool_calls:
                            function_name = tool_call.function.name
                            arguments = json.loads(tool_call.function.arguments)

                            if self.verbose:
                                display_tool_call(f"Agent {self.name} is calling function '{function_name}' with arguments: {arguments}", console=self.console)

                            tool_result = self.execute_tool(function_name, arguments)

                            if tool_result:
                                if self.verbose:
                                    display_tool_call(f"Function '{function_name}' returned: {tool_result}", console=self.console)
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": json.dumps(tool_result)
                                })
                            else:
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": "Function returned an empty output"
                                })
                            
                        response = self._chat_completion(messages, temperature=temperature, stream=stream)
                        if not response:
                            return None
                        response_text = response.choices[0].message.content.strip()

                    # Handle output_json or output_pydantic if specified
                    if output_json or output_pydantic:
                        # Add to chat history and return raw response
                        self.chat_history.append({"role": "user", "content": original_prompt})
                        self.chat_history.append({"role": "assistant", "content": response_text})
                        if self.verbose:
                            display_interaction(original_prompt, response_text, markdown=self.markdown, 
                                             generation_time=time.time() - start_time, console=self.console)
                        return response_text

                    if not self.self_reflect:
                        self.chat_history.append({"role": "user", "content": original_prompt})
                        self.chat_history.append({"role": "assistant", "content": response_text})
                        if self.verbose:
                            logging.debug(f"Agent {self.name} final response: {response_text}")
                        display_interaction(original_prompt, response_text, markdown=self.markdown, generation_time=time.time() - start_time, console=self.console)
                        # Return only reasoning content if reasoning_steps is True
                        if reasoning_steps and hasattr(response.choices[0].message, 'reasoning_content'):
                            return response.choices[0].message.reasoning_content
                        return response_text

                    reflection_prompt = f"""
Reflect on your previous response: '{response_text}'.
Identify any flaws, improvements, or actions.
Provide a "satisfactory" status ('yes' or 'no').
Output MUST be JSON with 'reflection' and 'satisfactory'.
                    """
                    logging.debug(f"{self.name} reflection attempt {reflection_count+1}, sending prompt: {reflection_prompt}")
                    messages.append({"role": "user", "content": reflection_prompt})

                    try:
                        reflection_response = client.beta.chat.completions.parse(
                            model=self.reflect_llm if self.reflect_llm else self.llm,
                            messages=messages,
                            temperature=temperature,
                            response_format=ReflectionOutput
                        )

                        reflection_output = reflection_response.choices[0].message.parsed

                        if self.verbose:
                            display_self_reflection(f"Agent {self.name} self reflection (using {self.reflect_llm if self.reflect_llm else self.llm}): reflection='{reflection_output.reflection}' satisfactory='{reflection_output.satisfactory}'", console=self.console)

                        messages.append({"role": "assistant", "content": f"Self Reflection: {reflection_output.reflection} Satisfactory?: {reflection_output.satisfactory}"})

                        # Only consider satisfactory after minimum reflections
                        if reflection_output.satisfactory == "yes" and reflection_count >= self.min_reflect - 1:
                            if self.verbose:
                                display_self_reflection("Agent marked the response as satisfactory after meeting minimum reflections", console=self.console)
                            self.chat_history.append({"role": "user", "content": prompt})
                            self.chat_history.append({"role": "assistant", "content": response_text})
                            display_interaction(prompt, response_text, markdown=self.markdown, generation_time=time.time() - start_time, console=self.console)
                            return response_text

                        # Check if we've hit max reflections
                        if reflection_count >= self.max_reflect - 1:
                            if self.verbose:
                                display_self_reflection("Maximum reflection count reached, returning current response", console=self.console)
                            self.chat_history.append({"role": "user", "content": prompt})
                            self.chat_history.append({"role": "assistant", "content": response_text})
                            display_interaction(prompt, response_text, markdown=self.markdown, generation_time=time.time() - start_time, console=self.console)
                            return response_text

                        logging.debug(f"{self.name} reflection count {reflection_count + 1}, continuing reflection process")
                        messages.append({"role": "user", "content": "Now regenerate your response using the reflection you made"})
                        response = self._chat_completion(messages, temperature=temperature, tools=None, stream=stream)
                        response_text = response.choices[0].message.content.strip()
                        reflection_count += 1
                        continue  # Continue the loop for more reflections

                    except Exception as e:
                        display_error(f"Error in parsing self-reflection json {e}. Retrying", console=self.console)
                        logging.error("Reflection parsing failed.", exc_info=True)
                        messages.append({"role": "assistant", "content": f"Self Reflection failed."})
                        reflection_count += 1
                        continue  # Continue even after error to try again
                    
                except Exception as e:
                    display_error(f"Error in chat: {e}", console=self.console)
                    return None 

        # Log completion time if in debug mode
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            total_time = time.time() - start_time
            logging.debug(f"Agent.chat completed in {total_time:.2f} seconds")
            
        return response_text

    def clean_json_output(self, output: str) -> str:
        """Clean and extract JSON from response text."""
        cleaned = output.strip()
        # Remove markdown code blocks if present
        if cleaned.startswith("```json"):
            cleaned = cleaned[len("```json"):].strip()
        if cleaned.startswith("```"):
            cleaned = cleaned[len("```"):].strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
        return cleaned  

    async def achat(self, prompt: str, temperature=0.2, tools=None, output_json=None, output_pydantic=None, reasoning_steps=False):
        """Async version of chat method. TODO: Requires Syncing with chat method.""" 
        # Log all parameter values when in debug mode
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            param_info = {
                "prompt": str(prompt)[:100] + "..." if isinstance(prompt, str) and len(str(prompt)) > 100 else str(prompt),
                "temperature": temperature,
                "tools": [t.__name__ if hasattr(t, "__name__") else str(t) for t in tools] if tools else None,
                "output_json": str(output_json.__class__.__name__) if output_json else None,
                "output_pydantic": str(output_pydantic.__class__.__name__) if output_pydantic else None,
                "reasoning_steps": reasoning_steps,
                "agent_name": self.name,
                "agent_role": self.role,
                "agent_goal": self.goal
            }
            logging.debug(f"Agent.achat parameters: {json.dumps(param_info, indent=2, default=str)}")
        
        start_time = time.time()
        reasoning_steps = reasoning_steps or self.reasoning_steps
        try:
            # Search for existing knowledge if any knowledge is provided
            if self.knowledge:
                search_results = self.knowledge.search(prompt, agent_id=self.agent_id)
                if search_results:
                    if isinstance(search_results, dict) and 'results' in search_results:
                        knowledge_content = "\n".join([result['memory'] for result in search_results['results']])
                    else:
                        knowledge_content = "\n".join(search_results)
                    prompt = f"{prompt}\n\nKnowledge: {knowledge_content}"

            if self._using_custom_llm:
                try:
                    response_text = await self.llm_instance.get_response_async(
                        prompt=prompt,
                        system_prompt=f"{self.backstory}\n\nYour Role: {self.role}\n\nYour Goal: {self.goal}" if self.use_system_prompt else None,
                        chat_history=self.chat_history,
                        temperature=temperature,
                        tools=tools,
                        output_json=output_json,
                        output_pydantic=output_pydantic,
                        verbose=self.verbose,
                        markdown=self.markdown,
                        self_reflect=self.self_reflect,
                        max_reflect=self.max_reflect,
                        min_reflect=self.min_reflect,
                        console=self.console,
                        agent_name=self.name,
                        agent_role=self.role,
                        agent_tools=[t.__name__ if hasattr(t, '__name__') else str(t) for t in self.tools],
                        execute_tool_fn=self.execute_tool_async,
                        reasoning_steps=reasoning_steps
                    )

                    self.chat_history.append({"role": "user", "content": prompt})
                    self.chat_history.append({"role": "assistant", "content": response_text})

                    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                        total_time = time.time() - start_time
                        logging.debug(f"Agent.achat completed in {total_time:.2f} seconds")
                    return response_text
                except Exception as e:
                    display_error(f"Error in LLM chat: {e}")
                    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                        total_time = time.time() - start_time
                        logging.debug(f"Agent.achat failed in {total_time:.2f} seconds: {str(e)}")
                    return None

            # For OpenAI client
            if self.use_system_prompt:
                system_prompt = f"""{self.backstory}\n
Your Role: {self.role}\n
Your Goal: {self.goal}
                """
                if output_json:
                    system_prompt += f"\nReturn ONLY a JSON object that matches this Pydantic model: {json.dumps(output_json.model_json_schema())}"
                elif output_pydantic:
                    system_prompt += f"\nReturn ONLY a JSON object that matches this Pydantic model: {json.dumps(output_pydantic.model_json_schema())}"
            else:
                system_prompt = None

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.extend(self.chat_history)

            # Modify prompt if output_json or output_pydantic is specified
            original_prompt = prompt
            if output_json or output_pydantic:
                if isinstance(prompt, str):
                    prompt += "\nReturn ONLY a valid JSON object. No other text or explanation."
                elif isinstance(prompt, list):
                    for item in prompt:
                        if item["type"] == "text":
                            item["text"] += "\nReturn ONLY a valid JSON object. No other text or explanation."
                            break

            if isinstance(prompt, list):
                messages.append({"role": "user", "content": prompt})
            else:
                messages.append({"role": "user", "content": prompt})

            reflection_count = 0
            start_time = time.time()

            while True:
                try:
                    if self.verbose:
                        display_text = prompt
                        if isinstance(prompt, list):
                            display_text = next((item["text"] for item in prompt if item["type"] == "text"), "")
                        
                        if display_text and str(display_text).strip():
                            agent_tools = [t.__name__ if hasattr(t, '__name__') else str(t) for t in self.tools]
                            await adisplay_instruction(
                                f"Agent {self.name} is processing prompt: {display_text}",
                                console=self.console,
                                agent_name=self.name,
                                agent_role=self.role,
                                agent_tools=agent_tools
                            )

                    # Format tools if provided
                    formatted_tools = []
                    if tools:
                        for tool in tools:
                            if isinstance(tool, str):
                                tool_def = self._generate_tool_definition(tool)
                                if tool_def:
                                    formatted_tools.append(tool_def)
                            elif isinstance(tool, dict):
                                formatted_tools.append(tool)
                            elif hasattr(tool, "to_openai_tool"):
                                formatted_tools.append(tool.to_openai_tool())
                            elif callable(tool):
                                formatted_tools.append(self._generate_tool_definition(tool.__name__))

                    # Create async OpenAI client
                    async_client = AsyncOpenAI()

                    # Make the API call based on the type of request
                    if tools:
                        response = await async_client.chat.completions.create(
                            model=self.llm,
                            messages=messages,
                            temperature=temperature,
                            tools=formatted_tools,
                        )
                        result = await self._achat_completion(response, tools)
                        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                            total_time = time.time() - start_time
                            logging.debug(f"Agent.achat completed in {total_time:.2f} seconds")
                        return result
                    elif output_json or output_pydantic:
                        response = await async_client.chat.completions.create(
                            model=self.llm,
                            messages=messages,
                            temperature=temperature,
                            response_format={"type": "json_object"}
                        )
                        # Return the raw response
                        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                            total_time = time.time() - start_time
                            logging.debug(f"Agent.achat completed in {total_time:.2f} seconds")
                        return response.choices[0].message.content
                    else:
                        response = await async_client.chat.completions.create(
                            model=self.llm,
                            messages=messages,
                            temperature=temperature
                        )
                        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                            total_time = time.time() - start_time
                            logging.debug(f"Agent.achat completed in {total_time:.2f} seconds")
                        return response.choices[0].message.content
                except Exception as e:
                    display_error(f"Error in chat completion: {e}")
                    if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                        total_time = time.time() - start_time
                        logging.debug(f"Agent.achat failed in {total_time:.2f} seconds: {str(e)}")
                    return None
        except Exception as e:
            display_error(f"Error in achat: {e}")
            if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                total_time = time.time() - start_time
                logging.debug(f"Agent.achat failed in {total_time:.2f} seconds: {str(e)}")
            return None

    async def _achat_completion(self, response, tools, reasoning_steps=False):
        """Async version of _chat_completion method"""
        try:
            message = response.choices[0].message
            if not hasattr(message, 'tool_calls') or not message.tool_calls:
                return message.content

            results = []
            for tool_call in message.tool_calls:
                try:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    # Find the matching tool
                    tool = next((t for t in tools if t.__name__ == function_name), None)
                    if not tool:
                        display_error(f"Tool {function_name} not found")
                        continue
                    
                    # Check if the tool is async
                    if asyncio.iscoroutinefunction(tool):
                        result = await tool(**arguments)
                    else:
                        # Run sync function in executor to avoid blocking
                        loop = asyncio.get_event_loop()
                        result = await loop.run_in_executor(None, lambda: tool(**arguments))
                    
                    results.append(result)
                except Exception as e:
                    display_error(f"Error executing tool {function_name}: {e}")
                    results.append(None)

            # If we have results, format them into a response
            if results:
                formatted_results = "\n".join([str(r) for r in results if r is not None])
                if formatted_results:
                    messages = [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "assistant", "content": "Here are the tool results:"},
                        {"role": "user", "content": formatted_results + "\nPlease process these results and provide a final response."}
                    ]
                    try:
                        async_client = AsyncOpenAI()
                        final_response = await async_client.chat.completions.create(
                            model=self.llm,
                            messages=messages,
                            temperature=0.2,
                            stream=True
                        )
                        full_response_text = ""
                        reasoning_content = ""
                        chunks = []
                        start_time = time.time()
                        
                        with Live(
                            display_generating("", start_time),
                            console=self.console,
                            refresh_per_second=4,
                            transient=True,
                            vertical_overflow="ellipsis",
                            auto_refresh=True
                        ) as live:
                            async for chunk in final_response:
                                chunks.append(chunk)
                                if chunk.choices[0].delta.content:
                                    full_response_text += chunk.choices[0].delta.content
                                    live.update(display_generating(full_response_text, start_time))
                                
                                if reasoning_steps and hasattr(chunk.choices[0].delta, "reasoning_content"):
                                    rc = chunk.choices[0].delta.reasoning_content
                                    if rc:
                                        reasoning_content += rc
                                        live.update(display_generating(f"{full_response_text}\n[Reasoning: {reasoning_content}]", start_time))
                        
                        self.console.print()
                        
                        final_response = process_stream_chunks(chunks)
                        # Return only reasoning content if reasoning_steps is True
                        if reasoning_steps and hasattr(final_response.choices[0].message, 'reasoning_content'):
                            return final_response.choices[0].message.reasoning_content
                        return final_response.choices[0].message.content if final_response else full_response_text

                    except Exception as e:
                        display_error(f"Error in final chat completion: {e}")
                        return formatted_results
                return formatted_results
            return None
        except Exception as e:
            display_error(f"Error in _achat_completion: {e}")
            return None

    async def astart(self, prompt: str, **kwargs):
        """Async version of start method"""
        return await self.achat(prompt, **kwargs)

    def run(self):
        """Alias for start() method"""
        return self.start() 

    def start(self, prompt: str, **kwargs):
        """Start the agent with a prompt. This is a convenience method that wraps chat()."""
        return self.chat(prompt, **kwargs) 

    async def execute_tool_async(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Async version of execute_tool"""
        try:
            logging.info(f"Executing async tool: {function_name} with arguments: {arguments}")
            # Try to find the function in the agent's tools list first
            func = None
            for tool in self.tools:
                if (callable(tool) and getattr(tool, '__name__', '') == function_name):
                    func = tool
                    break
            
            if func is None:
                logging.error(f"Function {function_name} not found in tools")
                return {"error": f"Function {function_name} not found in tools"}

            try:
                if inspect.iscoroutinefunction(func):
                    logging.debug(f"Executing async function: {function_name}")
                    result = await func(**arguments)
                else:
                    logging.debug(f"Executing sync function in executor: {function_name}")
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, lambda: func(**arguments))
                
                # Ensure result is JSON serializable
                logging.debug(f"Raw result from tool: {result}")
                if result is None:
                    return {"result": None}
                try:
                    json.dumps(result)  # Test serialization
                    return result
                except TypeError:
                    logging.warning(f"Result not JSON serializable, converting to string: {result}")
                    return {"result": str(result)}

            except Exception as e:
                logging.error(f"Error executing {function_name}: {str(e)}", exc_info=True)
                return {"error": f"Error executing {function_name}: {str(e)}"}

        except Exception as e:
            logging.error(f"Error in execute_tool_async: {str(e)}", exc_info=True)
            return {"error": f"Error in execute_tool_async: {str(e)}"} 
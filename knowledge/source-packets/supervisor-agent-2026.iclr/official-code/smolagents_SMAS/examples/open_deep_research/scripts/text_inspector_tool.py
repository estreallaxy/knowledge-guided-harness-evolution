from smolagents import Tool
from smolagents.models import Model

class TokenUsage:
    def __init__(self, input_tokens=0, output_tokens=0):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens

class TextInspectorTool(Tool):
    name = "inspect_file_as_text"
    description = """
You cannot load files yourself: instead call this tool to read a file as markdown text and ask questions about it.
This tool handles the following file extensions: [".html", ".htm", ".xlsx", ".pptx", ".wav", ".mp3", ".m4a", ".flac", ".pdf", ".docx"], and all other types of text files. IT DOES NOT HANDLE IMAGES."""

    inputs = {
        "file_path": {
            "description": "The path to the file you want to read as text. Must be a '.something' file, like '.pdf'. If it is an image, use the visualizer tool instead! DO NOT use this tool for an HTML webpage: use the web_search tool instead!",
            "type": "string",
        },
        "question": {
            "description": "[Optional]: Your question, as a natural language sentence. Provide as much context as possible. Do not pass this parameter if you just want to directly return the content of the file.",
            "type": "string",
            "nullable": True,
        },
    }
    output_type = "string"

    def __init__(self, model: Model = None, text_limit: int = 100000):
        super().__init__()
        self.model = model
        self.text_limit = text_limit
        from .mdconvert import MarkdownConverter

        self.md_converter = MarkdownConverter()
        self.total_token_usage = TokenUsage(input_tokens=0, output_tokens=0)

    def get_total_token_counts(self) -> TokenUsage:
        return self.total_token_usage

    def forward_initial_exam_mode(self, file_path, question):
        from smolagents.models import MessageRole

        result = self.md_converter.convert(file_path)

        if file_path[-4:] in [".png", ".jpg"]:
            raise Exception("Cannot use inspect_file_as_text tool with images: use visualizer instead!")

        if ".zip" in file_path:
            return result.text_content

        if not question:
            return result.text_content

        if len(result.text_content) < 4000:
            return "Document content: " + result.text_content

        messages = [
            {
                "role": MessageRole.SYSTEM,
                "content": [
                    {
                        "type": "text",
                        "text": "Here is a file:\n### "
                        + str(result.title)
                        + "\n\n"
                        + result.text_content[: self.text_limit],
                    }
                ],
            },
            {
                "role": MessageRole.USER,
                "content": [
                    {
                        "type": "text",
                        "text": "Now please write a short, 5 sentence caption for this document, that could help someone asking this question: "
                        + question
                        + "\n\nDon't answer the question yourself! Just provide useful notes on the document",
                    }
                ],
            },
        ]

        response_message = self.model(messages)
        # 安全地检查并累加token消耗
        if response_message and response_message.token_usage:
            self.total_token_usage.input_tokens += response_message.token_usage.input_tokens
            self.total_token_usage.output_tokens += response_message.token_usage.output_tokens

        return response_message.content

    def forward(self, file_path, question: str | None = None) -> str:
        from smolagents.models import MessageRole

        # result = self.md_converter.convert(file_path)     # 原始代码
        try:
            # 步骤 1: 执行转换并立刻检查结果
            result = self.md_converter.convert(file_path)
            
            # 步骤 2: 增加对转换结果的有效性检查
            if result is None or not hasattr(result, 'text_content') or result.text_content is None:
                # 如果转换结果对象无效或文本内容为 None，则返回明确的错误信息
                return f"[Tool Error: Failed to convert or read the file at '{file_path}'. The file might be inaccessible, corrupted, or the download was blocked.]"

            text_content = result.text_content.strip()
            
            # 步骤 3: 检查提取的文本是否为空
            if not text_content:
                return f"[Tool Error: The file at '{file_path}' was processed, but no text could be extracted. It might be an image-only document or empty.]"

        except Exception as e:
            # 步骤 4: 捕获在 convert 过程中可能抛出的任何其他异常
            # 确保即使 md_converter 内部发生意外，我们也能给智能体一个交代
            return f"[Tool Error: An unexpected error occurred while processing '{file_path}'. Details: {str(e)}]"

        if file_path[-4:] in [".png", ".jpg"]:
            raise Exception("Cannot use inspect_file_as_text tool with images: use visualizer instead!")

        if ".zip" in file_path:
            return result.text_content

        if not question:
            return result.text_content

        messages = [
            {
                "role": MessageRole.SYSTEM,
                "content": [
                    {
                        "type": "text",
                        "text": "You will have to write a short caption for this file, then answer this question:"
                        + question,
                    }
                ],
            },
            {
                "role": MessageRole.USER,
                "content": [
                    {
                        "type": "text",
                        "text": "Here is the complete file:\n### "
                        + str(result.title)
                        + "\n\n"
                        + result.text_content[: self.text_limit],
                    }
                ],
            },
            {
                "role": MessageRole.USER,
                "content": [
                    {
                        "type": "text",
                        "text": "Now answer the question below. Use these three headings: '1. Short answer', '2. Extremely detailed answer', '3. Additional Context on the document and question asked'."
                        + question,
                    }
                ],
            },
        ]

        response_message = self.model(messages)

        # 安全地检查并累加token消耗
        if response_message and response_message.token_usage:
            self.total_token_usage.input_tokens += response_message.token_usage.input_tokens
            self.total_token_usage.output_tokens += response_message.token_usage.output_tokens
            
        return response_message.content

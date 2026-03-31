from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown

if __name__ == '__main__':
    console = Console()

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
    )

    try:
        resp = client.chat.completions.create(
            model="stepfun/step-3.5-flash:free",
            messages=[
                {
                    "role": "user",
                    "content": "谁是辛顿?"
                }
            ],
            extra_body={"reasoning": {"enabled": True}}
        )

        content = resp.choices[0].message.content or ""

        console.print("\n[bold cyan]模型回答：[/bold cyan]\n")
        console.print(Markdown(content))

    except RateLimitError as e:
        console.print("\n[bold red]请求被限流了（429）[/bold red]")
        console.print(str(e))
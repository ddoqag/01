"""
命令行界面 - 展示现代 Python CLI 开发模式
"""

import asyncio
from pathlib import Path
from typing import Any, Optional

import typer
import structlog
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .core.config import get_settings, set_settings
from .services import AIService, ConversationService
from .ai.manager import AIManager

logger = structlog.get_logger()
console = Console()

# 创建 CLI 应用
cli_app = typer.Typer(
    name="ai-platform",
    help="现代化 AI 集成平台命令行工具",
    rich_markup_mode="rich",
    no_args_is_help=True,
)

# 子命令
generate_app = typer.Typer(help="AI 文本生成相关命令")
conversation_app = typer.Typer(help="对话管理相关命令")
analysis_app = typer.Typer(help="文本分析相关命令")
config_app = typer.Typer(help="配置管理相关命令")

cli_app.add_typer(generate_app, name="generate")
cli_app.add_typer(conversation_app, name="conversation")
cli_app.add_typer(analysis_app, name="analyze")
cli_app.add_typer(config_app, name="config")


def init_services() -> tuple[AIService, ConversationService]:
    """初始化服务"""
    ai_service = AIService()
    conversation_service = ConversationService()
    return ai_service, conversation_service


@cli_app.callback()
def main_callback(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="启用详细输出"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="配置文件路径"),
) -> None:
    """AI Integration Platform - 现代化 Python 3.13+ AI 集成平台"""

    # 配置日志
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        )

    # 加载配置文件
    if config_file and config_file.exists():
        # 这里可以添加配置文件加载逻辑
        console.print(f"[green]✓[/green] 使用配置文件: {config_file}")

    # 显示欢迎信息
    console.print(Panel.fit(
        "[bold blue]AI Integration Platform[/bold blue]\n"
        "现代化 Python 3.13+ AI 集成平台",
        border_style="blue"
    ))


@cli_app.command()
def version() -> None:
    """显示版本信息"""
    settings = get_settings()

    table = Table(title="版本信息")
    table.add_column("项目", style="cyan")
    table.add_column("版本", style="green")

    table.add_row("AI Platform", settings.app_version)
    table.add_row("Python", "3.13+")
    table.add_row("FastAPI", "0.115+")
    table.add_row("Pydantic", "2.10+")

    console.print(table)


@cli_app.command()
def info() -> None:
    """显示系统信息"""
    settings = get_settings()

    console.print("\n[bold]系统配置[/bold]")
    console.print(f"环境: {settings.environment}")
    console.print(f"调试模式: {settings.debug}")
    console.print(f"数据目录: {Path.cwd()}")

    console.print("\n[bold]AI 提供商[/bold]")
    for provider in settings.ai_providers:
        console.print(f"  ✓ {provider.value}")

    console.print("\n[bold]功能特性[/bold]")
    console.print("  ✓ 多 AI 提供商支持")
    console.print("  ✓ 异步处理")
    console.print("  ✓ 流式生成")
    console.print("  ✓ 类型安全")
    console.print("  ✓ 企业级架构")


@generate_app.command("text")
def generate_text(
    prompt: str = typer.Argument(..., help="生成提示词"),
    model: str = typer.Option("claude-3-haiku-20240307", "--model", "-m", help="使用的模型"),
    max_tokens: int = typer.Option(1000, "--max-tokens", "-t", help="最大令牌数"),
    temperature: float = typer.Option(0.7, "--temperature", help="温度参数 (0.0-2.0)"),
    stream: bool = typer.Option(False, "--stream", "-s", help="启用流式输出"),
    system_prompt: Optional[str] = typer.Option(None, "--system", help="系统提示词"),
) -> None:
    """生成 AI 文本内容"""

    async def _generate():
        from .core.models import AIRequest

        ai_service, _ = init_services()

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("正在初始化 AI 服务...", total=None)

                await ai_service.initialize()

                progress.update(task, description="正在生成内容...")

                request = AIRequest(
                    prompt=prompt,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=stream,
                    system_prompt=system_prompt,
                    user_id="cli-user",
                )

                if stream:
                    progress.stop()
                    console.print("\n[bold]AI 响应 (流式):[/bold]\n")

                    async for chunk in ai_service.process_streaming_request(request):
                        console.print(chunk, end="")
                    console.print()  # 换行
                else:
                    response = await ai_service.process_request(request)

                    progress.update(task, description="完成!")

                    # 显示结果
                    console.print(f"\n[bold]AI 响应:[/bold]")
                    console.print(Panel(response.content, border_style="green"))

                    console.print(f"\n[dim]模型: {response.model_used}[/dim]")
                    console.print(f"[dim]令牌数: {response.tokens_used}[/dim]")
                    console.print(f"[dim]响应时间: {response.response_time_ms}ms[/dim]")
                    console.print(f"[dim]成本: ${response.cost:.6f}[/dim]")

        except Exception as e:
            console.print(f"\n[red]错误: {e}[/red]")
            raise typer.Exit(1)

        finally:
            await ai_service.cleanup()

    asyncio.run(_generate())


@generate_app.command("code")
def generate_code(
    description: str = typer.Argument(..., help="代码功能描述"),
    language: str = typer.Option("python", "--language", "-l", help="编程语言"),
    model: str = typer.Option("claude-3-5-sonnet-20241022", "--model", "-m", help="使用的模型"),
) -> None:
    """生成代码"""

    async def _generate():
        ai_service, _ = init_services()

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("正在生成代码...", total=None)

                await ai_service.initialize()

                code = await ai_service.generate_code(
                    description=description,
                    language=language,
                    model=model,
                    user_id="cli-user",
                )

                progress.update(task, description="完成!")

            # 显示结果
            console.print(f"\n[bold]生成的 {language} 代码:[/bold]")
            console.print(Panel(code, border_style="blue", title=f"{language.title()} Code"))

        except Exception as e:
            console.print(f"\n[red]错误: {e}[/red]")
            raise typer.Exit(1)

        finally:
            await ai_service.cleanup()

    asyncio.run(_generate())


@analysis_app.command("sentiment")
def analyze_sentiment(
    text: str = typer.Argument(..., help="要分析的文本"),
    model: str = typer.Option("claude-3-haiku-20240307", "--model", "-m", help="使用的模型"),
) -> None:
    """情感分析"""

    async def _analyze():
        ai_service, _ = init_services()

        try:
            await ai_service.initialize()

            with Progress(console=console) as progress:
                task = progress.add_task("正在分析情感...", total=None)

                result = await ai_service.analyze_text(
                    text=text,
                    analysis_type="sentiment",
                    model=model,
                    user_id="cli-user",
                )

                progress.update(task, description="完成!")

            # 显示结果
            console.print(f"\n[bold]原文:[/bold] {text}")
            console.print(f"\n[bold]情感分析结果:[/bold]")

            if isinstance(result, dict):
                if "sentiment" in result:
                    sentiment = result["sentiment"]
                    if sentiment > 0.3:
                        sentiment_emoji = "😊"
                        color = "green"
                    elif sentiment < -0.3:
                        sentiment_emoji = "😔"
                        color = "red"
                    else:
                        sentiment_emoji = "😐"
                        color = "yellow"

                    console.print(f"情感分数: {sentiment_emoji} {sentiment:.2f}")

                if "reasoning" in result:
                    console.print(f"分析原因: {result['reasoning']}")
            else:
                console.print(result)

        except Exception as e:
            console.print(f"\n[red]错误: {e}[/red]")
            raise typer.Exit(1)

        finally:
            await ai_service.cleanup()

    asyncio.run(_analyze())


@analysis_app.command("entities")
def analyze_entities(
    text: str = typer.Argument(..., help="要分析的文本"),
    model: str = typer.Option("claude-3-haiku-20240307", "--model", "-m", help="使用的模型"),
) -> None:
    """实体提取"""

    async def _analyze():
        ai_service, _ = init_services()

        try:
            await ai_service.initialize()

            with Progress(console=console) as progress:
                task = progress.add_task("正在提取实体...", total=None)

                result = await ai_service.analyze_text(
                    text=text,
                    analysis_type="entities",
                    model=model,
                    user_id="cli-user",
                )

                progress.update(task, description="完成!")

            # 显示结果
            console.print(f"\n[bold]原文:[/bold] {text}")
            console.print(f"\n[bold]提取的实体:[/bold]")

            if isinstance(result, dict):
                if "entities" in result:
                    table = Table(title="命名实体")
                    table.add_column("实体", style="cyan")
                    table.add_column("类型", style="green")

                    for entity in result["entities"]:
                        if isinstance(entity, dict):
                            table.add_row(entity.get("text", ""), entity.get("type", ""))
                        else:
                            table.add_row(str(entity), "未知")

                    console.print(table)
            else:
                console.print(result)

        except Exception as e:
            console.print(f"\n[red]错误: {e}[/red]")
            raise typer.Exit(1)

        finally:
            await ai_service.cleanup()

    asyncio.run(_analyze())


@config_app.command("show")
def config_show() -> None:
    """显示当前配置"""
    settings = get_settings()

    console.print("\n[bold]当前配置:[/bold]")

    # 基础配置
    table = Table(title="基础配置")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="green")

    table.add_row("应用名称", settings.app_name)
    table.add_row("版本", settings.app_version)
    table.add_row("环境", settings.environment)
    table.add_row("调试模式", str(settings.debug))
    table.add_row("主机", settings.host)
    table.add_row("端口", str(settings.port))

    console.print(table)

    # AI 提供商配置
    ai_table = Table(title="AI 提供商")
    ai_table.add_column("提供商", style="cyan")
    ai_table.add_column("状态", style="green")
    ai_table.add_column("API Key", style="yellow")

    for provider in settings.ai_providers:
        config = settings.get_ai_provider_config(provider)
        api_key_status = "已配置" if config.get("api_key") else "未配置"
        ai_table.add_row(provider.value, "✓", api_key_status)

    console.print(ai_table)


@config_app.command("validate")
def config_validate() -> None:
    """验证配置"""
    settings = get_settings()

    console.print("\n[bold]配置验证:[/bold]")

    issues = []

    # 验证必需的配置
    if not settings.secret_key.get_secret_value() or len(settings.secret_key.get_secret_value()) < 32:
        issues.append("❌ SECRET_KEY 太短或未设置")
    else:
        console.print("✅ SECRET_KEY 配置正确")

    # 验证 AI 提供商
    for provider in settings.ai_providers:
        config = settings.get_ai_provider_config(provider)
        if config.get("api_key"):
            console.print(f"✅ {provider.value} API Key 已配置")
        else:
            issues.append(f"❌ {provider.value} API Key 未配置")

    # 验证环境特定配置
    if settings.is_production():
        if settings.debug:
            issues.append("❌ 生产环境不应启用调试模式")
        else:
            console.print("✅ 生产环境配置正确")

    # 显示结果
    if issues:
        console.print(f"\n[red]发现 {len(issues)} 个配置问题:[/red]")
        for issue in issues:
            console.print(f"  {issue}")
        raise typer.Exit(1)
    else:
        console.print(f"\n[green]✅ 配置验证通过![/green]")


@cli_app.command("server")
def serve_server(
    host: str = typer.Option("127.0.0.1", "--host", help="服务器主机"),
    port: int = typer.Option(8000, "--port", "-p", help="服务器端口"),
    reload: bool = typer.Option(False, "--reload", "-r", help="启用自动重载"),
    workers: int = typer.Option(1, "--workers", "-w", help="工作进程数"),
) -> None:
    """启动 API 服务器"""

    console.print(f"\n[bold]启动 AI Platform 服务器...[/bold]")
    console.print(f"地址: http://{host}:{port}")
    console.print(f"工作进程: {workers}")
    console.print(f"自动重载: {'启用' if reload else '禁用'}")

    # 这里应该启动 FastAPI 服务器
    console.print(f"\n[green]✓ 服务器已启动[/green]")
    console.print(f"API 文档: http://{host}:{port}/docs")

    # 实际实现中会调用 uvicorn.run()
    console.print("\n[yellow]注意: 这是演示版本，实际服务器启动需要完整的实现[/yellow]")


if __name__ == "__main__":
    cli_app()
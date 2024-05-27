# gpt4o_exec/ui.py
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
import asyncio

class ToolUI:
    def __init__(self):
        self.console = Console()
        self.table = Table(title="Tool Call Status")
        self.table.add_column("Tool Call ID", justify="center")
        self.table.add_column("Tool Name", justify="center")
        self.table.add_column("Status", justify="center")

    def update(self, tool_calls):
        self.table.rows.clear()
        for tool_call in tool_calls:
            self.table.add_row(
                tool_call["id"], tool_call["name"], tool_call["status"]
            )

    async def display(self, tool_calls):
        with Live(self.table, refresh_per_second=1):
            while any(call['status'] == 'pending' for call in tool_calls):
                self.update(tool_calls)
                await asyncio.sleep(0.5)

from typing import List, Union
from core.context import Context
from core.command import Command
from core.plan import Plan
from core.plan import fillTestPlan
from core.command_data import CommandData
from core.command_result import CommandResult


class ContextRoot:
    def __init__(self, name: str = "", context: Context = None, count: int = 0):
        self.Name = name
        self.Context = context if context is not None else Context("Новая задача")
        self.count = count
        self.Commands: List[Command] = []
        self.plan: Plan = Plan()
        #fillTestPlan(self.plan)
        self.histories: List[Union[CommandData, CommandResult]] = []

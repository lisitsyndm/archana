from core.context_root import ContextRoot
from core.command_processor import CommandProcessor
from tools.context import RegisterContextCommands
from tools.controls import RegisterControlCommands
from tools.search import RegisterSearchCommands
from tools.researcher import RegisterResearcherCommands
from tools.unclassified import RegisterUnclassifiedCommands
from tools.file_system import RegisterFileCommands
from tools.database import RegisterDatabaseCommands
from tools.plan import RegisterPlanCommands

def initTools(cp: CommandProcessor):
    RegisterContextCommands(cp)
    RegisterControlCommands(cp)
    RegisterResearcherCommands(cp)
    #RegisterSearchCommands(cp)
    RegisterUnclassifiedCommands(cp)
    RegisterFileCommands(cp)
    RegisterDatabaseCommands(cp)
    RegisterPlanCommands(cp)
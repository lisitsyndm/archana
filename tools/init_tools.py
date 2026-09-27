from core.context_root import ContextRoot
from tools.context import RegisterContextCommands
from tools.controls import RegisterControlCommands
from tools.search import RegisterSearchCommands
from tools.researcher import RegisterResearcherCommands
from tools.unclassified import RegisterUnclassifiedCommands
from tools.file_system import RegisterFileCommands
from tools.database import RegisterDatabaseCommands
from tools.plan import RegisterPlanCommands

def initTools(ctx: ContextRoot):
    RegisterContextCommands(ctx)
    RegisterControlCommands(ctx)
    RegisterResearcherCommands(ctx)
    #RegisterSearchCommands(ctx)
    RegisterUnclassifiedCommands(ctx)
    RegisterFileCommands(ctx)
    RegisterDatabaseCommands(ctx)
    RegisterPlanCommands(ctx)
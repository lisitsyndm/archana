from core.context_root import ContextRoot
import re

def fillKnowledge(ctx_root: ContextRoot, text: str) -> str:
    knowledge_names = ctx_root.Context.getKnowledgeList()
    if not knowledge_names:
        return text

    pattern = r"<@\s*(.+?)\s*@>"

    def replace_match(match):
        var_name = match.group(1)

        if var_name == "последний результат":
            return ctx_root.Context.lastResult

        text_value = ctx_root.Context.getKnowledgeTextByName(var_name)
        if text_value is not None:
            return text_value
        return ""

    return re.sub(pattern, replace_match, text)

#-----------------------------------------------------------------------------#
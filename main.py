from core.context_root import ContextRoot
from core.message_service import MessageService
from core.command_processor import CommandProcessor
from tools.init_tools import initTools
from prometheus_client import start_http_server


if __name__ == '__main__':
    # Запуск HTTP сервера для Prometheus метрик на порту 8001
    start_http_server(8001)
    
    service = MessageService()
    ctx_root = ContextRoot()
    service.CommandProcessor = CommandProcessor(ctx_root)

    initTools(ctx_root)

    #service.Prepare()
    service.Run()

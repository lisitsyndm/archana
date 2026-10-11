Необходимо переписать метод `process` класса `CommandProcessor`
таким образом, чтобы вся логика была реализована на базе LangGraph.

## вершины
### `exec_text_command`

начальное состояние
выполняется всегда при запуске графа
выполняет следующие действия

### `exec_plan-command` - второе состояние графа

выполняет следующие действия:

            commandData: CommandData = self.ctx_root.plan.next()
            if commandData is not None:
                result = self.process_command( f"/ {commandData.commandName} : {commandData.commandPayload}"  )
                callback(result)


## переходы

### 1 

если self.ctx_root.plan.planStatus == PlanStatus.Started
    из exec_text_command в exec_plan_command
иначе выход из графа 

### 2

если self.ctx_root.plan.planStatus == PlanStatus.Started
   из exec_plan_command в exec_plan_command
иначе выход из графа 
class CommandResult:
    def __init__(self, output_text: str = "",  update_result: bool = True, should_continue: bool = True):
        self.output_text = output_text
        self.should_continue = should_continue
        self.update_result = update_result

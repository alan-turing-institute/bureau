from datetime import datetime
from pathlib import Path
from pulumi import automation as auto

date_string = datetime.today().strftime('%Y%m%dT%H%M%S')
stack_name = f'dev_{date_string}'
work_dir = Path(__file__).parent.parent.absolute() / Path('infrastructure/')

stack = auto.create_or_select_stack(
    stack_name=stack_name,
    work_dir=work_dir
)

stack.set_config('date_string', auto.ConfigValue(value=date_string))
stack.set_config('azure-native:location', auto.ConfigValue(value='uksouth'))

stack.refresh(on_output=print)

stack.up(on_output=print)

#!/home/knight/personal-packages/friends/MCSR/env/bin/python
from persistent import RunResponse, persistent
from sheets_copy import copy

USER = "pinchyish"

def suggest_discard(run: RunResponse) -> bool:
    print('\t'.join(run.flatten()))
    print('Do you want to discard this run? (will not appear in the spreadsheet)')
    return input('[y/N] ').upper() == 'Y'

def fetch():
    runs = persistent.fetch()
    if not runs: return print("No new runs found")
    new: list[RunResponse] = []
    for run in runs:
        if not suggest_discard(run): new.append(run)
        else: print(f"Discarded run {persistent.discard(run.id)}")
    print('New runs:\n' + '\n'.join('\t'.join(run.flatten()) for run in new))
    if input('Do you want to copy these? [Y/n] ').upper() == 'N': return
    copy(new)

def get_selection() -> slice:
    while True:
        left, _, right = input("Input the ID's of the first (inclusive) and the last (non-inclusive) run you want to copy with space in between or just the first run to copy everything starting from this point\n").partition(' ')
        try: return slice(int(left), (int(right) if right else None))
        except ValueError: print("Invalid format. For example '3, 10' to copy [3:10] or '3' for copy [3:]")

def select_copy():
    for i, run in enumerate(persistent.runs):
        print(f'{i})', '\t'.join(run.flatten()))
    cut = get_selection()
    print(f"Copying {cut}")
    copy(persistent.runs[cut])

def funchelp():
    print('\n'.join(f'- {function}\t\t{functions[function][0]}' for function in functions))

functions = {'exit': ("This one's easy", lambda:print("Exiting, bye"))}
functions['fetch'] = "Get new data from mcsrranked server", fetch
functions['copy'] = "Select runs from the already fetched and copy them for the spreadsheet", select_copy
functions['help'] = "You just used it", funchelp
command = None
while command != 'exit':
    command = input("What do you want to do? type help for options\n")
    func = functions.get(command, (None, lambda:(print("Command not recognised, try typing help"), funchelp())))
    func[1]()
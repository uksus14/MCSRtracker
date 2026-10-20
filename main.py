#!/home/knight/personal-packages/friends/MCSR/env/bin/python
from persistent import RunResponse, persistent
import requests

USER = "pinchyish"

def get(id: int) -> RunResponse:
    data = requests.get(f"https://mcsrranked.com/api/matches/{id}").json()['data']
    return persistent.cache(RunResponse.project(data))

def suggest_discard(run: RunResponse) -> bool:
    print('\t'.join(run.flatten()))
    print('Do you want to discard this run? (will not appear in the spreadsheet)')
    return input('[y/N] ').upper() == 'Y'

def make_copy(runs: list[RunResponse]) -> str:
    return '<table style="text-align:right;"><tbody>' + "".join(run.tohtml() for run in runs) + '</tbody></table>'

def copy(runs: list[RunResponse]):
    make_copy(runs)
    return 

def fetch():
    data = requests.get(f"https://mcsrranked.com/api/users/{USER}/matches").json()['data']
    data = list(filter(lambda run: not persistent.find(run['id']), data))
    if not data: return print("No new runs found")
    new: list[RunResponse] = []
    for run in data[::-1]:
        run = get(run['id'])
        if suggest_discard(run): print(f"Discarded run {persistent.discard(run.id)}")
        new.append(run)
    print('New runs:\n' + '\n'.join('\t'.join(run.flatten()) for run in new))
    if input('Do you want to copy these? [Y/n] ').upper() == 'N': return
    copy(new)

def funchelp():
    print('\n'.join(f'- {function}\t\t{functions[function][0]}' for function in functions))

functions = {'exit': ("This one's easy", lambda:print("Exiting, bye"))}
functions['fetch'] = "Get new data from mcsrranked server", fetch
functions['help'] = "You just used it", funchelp
if __name__ == "__main__":
    command = None
    while command != 'exit':
        command = input("What do you want to do? type help for options\n")
        func = functions.get(command, (None, lambda:print("Command not recognised, try typing help")))
        func[1]()